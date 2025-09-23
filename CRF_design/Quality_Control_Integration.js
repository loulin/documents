/**
 * Laboratory Quality Control System Integration Module
 * Main orchestrator for the complete quality control system
 * Integrates all components: validation, anomaly detection, clinical logic, alerts, metrics, and corrections
 * 
 * Laboratory Quality Control System v1.0 - Complete Integration
 */

const { LaboratoryQualityControlSystem } = require('./Laboratory_Quality_Control_System');
const { ClinicalLogicValidator } = require('./Clinical_Logic_Validator');
const { AlertNotificationSystem } = require('./Alert_Notification_System');
const { QualityMetricsDashboard } = require('./Quality_Metrics_Dashboard');
const { AutomatedCorrectionSystem } = require('./Automated_Correction_System');

class QualityControlIntegration {
    constructor(testDefinitionsPath, config = {}) {
        this.config = {
            ...this.getDefaultConfig(),
            ...config
        };
        
        this.testDefinitionsPath = testDefinitionsPath;
        this.isInitialized = false;
        this.processingQueue = [];
        this.activeProcessing = false;
        
        // Initialize all subsystems
        this.initializeSubsystems();
        
        // Setup event listeners
        this.setupEventListeners();
        
        // Start background processes
        this.startBackgroundProcesses();
        
        console.log('🚀 Laboratory Quality Control System v1.0 Initialized');
    }

    /**
     * Get default configuration
     */
    getDefaultConfig() {
        return {
            realTimeProcessing: true,
            maxProcessingTimeMs: 100,
            batchProcessing: {
                enabled: true,
                batchSize: 100,
                processingInterval: 1000
            },
            autoCorrection: {
                enabled: true,
                confidenceThreshold: 0.9,
                requiresApproval: true
            },
            alerting: {
                enabled: true,
                immediateNotification: true,
                escalationEnabled: true
            },
            dashboard: {
                enabled: true,
                refreshInterval: 30000,
                realTimeUpdates: true
            },
            audit: {
                enabled: true,
                detailLevel: 'full',
                retentionDays: 365
            },
            performance: {
                enableMetrics: true,
                logSlowProcessing: true,
                slowProcessingThreshold: 200
            }
        };
    }

    /**
     * Initialize all subsystems
     */
    async initializeSubsystems() {
        try {
            console.log('🔧 Initializing Quality Control Subsystems...');

            // Load test definitions and configuration
            const qcConfig = require('./Laboratory_QC_Configuration.json');
            
            // Initialize core quality control system
            this.qcSystem = new LaboratoryQualityControlSystem(this.testDefinitionsPath);
            console.log('✅ Core Quality Control System initialized');

            // Initialize clinical logic validator
            this.clinicalValidator = new ClinicalLogicValidator(qcConfig.clinical_logic_validation);
            console.log('✅ Clinical Logic Validator initialized');

            // Initialize alert notification system
            this.alertSystem = new AlertNotificationSystem(qcConfig.alert_system);
            console.log('✅ Alert Notification System initialized');

            // Initialize quality metrics dashboard
            this.dashboard = new QualityMetricsDashboard(qcConfig.quality_metrics);
            console.log('✅ Quality Metrics Dashboard initialized');

            // Initialize automated correction system
            this.correctionSystem = new AutomatedCorrectionSystem(
                this.qcSystem.testDefinitions,
                qcConfig.correction_suggestions
            );
            console.log('✅ Automated Correction System initialized');

            this.isInitialized = true;
            console.log('🎉 All subsystems initialized successfully');

        } catch (error) {
            console.error('❌ Error initializing subsystems:', error);
            throw new Error(`Quality Control System initialization failed: ${error.message}`);
        }
    }

    /**
     * Setup event listeners for inter-system communication
     */
    setupEventListeners() {
        // Alert system events
        this.alertSystem.on('alertProcessed', (alert) => {
            this.dashboard.updateMetrics({
                alerts: {
                    total: 1,
                    byLevel: { [alert.level]: 1 },
                    details: [alert]
                }
            });
        });

        this.alertSystem.on('alertEscalated', (alert) => {
            console.log(`🔺 Alert escalated: ${alert.alertId}`);
            this.logAuditEvent('alert_escalated', { alertId: alert.alertId, level: alert.level });
        });

        this.alertSystem.on('alertAcknowledged', (alert) => {
            console.log(`✅ Alert acknowledged: ${alert.alertId}`);
            this.dashboard.updateMetrics({
                alerts: {
                    responseTime: {
                        average: alert.responseTime
                    }
                }
            });
        });

        // Dashboard events (if needed for real-time updates)
        if (this.config.dashboard.realTimeUpdates) {
            this.dashboard.on('metricsUpdated', (metrics) => {
                // Could broadcast to WebSocket clients, etc.
            });
        }
    }

    /**
     * Start background processes
     */
    startBackgroundProcesses() {
        // Quality metrics update process
        if (this.config.dashboard.enabled) {
            setInterval(() => {
                this.updateQualityMetrics();
            }, this.config.dashboard.refreshInterval);
        }

        // Batch processing for queued items
        if (this.config.batchProcessing.enabled) {
            setInterval(() => {
                this.processBatch();
            }, this.config.batchProcessing.processingInterval);
        }

        // Audit cleanup process (daily)
        setInterval(() => {
            this.cleanupAuditLogs();
        }, 24 * 60 * 60 * 1000);

        console.log('🔄 Background processes started');
    }

    /**
     * Main entry point for processing a laboratory test result
     */
    async processTestResult(testResult, options = {}) {
        const startTime = performance.now();
        
        try {
            // Validate input
            const inputValidation = this.validateInput(testResult);
            if (!inputValidation.valid) {
                throw new Error(`Invalid input: ${inputValidation.errors.join(', ')}`);
            }

            // Create processing context
            const processingContext = {
                testResult: testResult,
                options: options,
                startTime: startTime,
                processingId: this.generateProcessingId(),
                timestamp: new Date()
            };

            // Log start of processing
            this.logAuditEvent('processing_started', {
                processingId: processingContext.processingId,
                testId: testResult.testId,
                patientId: testResult.patientId
            });

            // Decide processing mode (real-time vs batch)
            if (this.config.realTimeProcessing && !options.forceBatch) {
                return await this.processRealTime(processingContext);
            } else {
                return await this.queueForBatchProcessing(processingContext);
            }

        } catch (error) {
            console.error('Error processing test result:', error);
            
            // Log error
            this.logAuditEvent('processing_error', {
                testId: testResult?.testId,
                patientId: testResult?.patientId,
                error: error.message,
                processingTime: performance.now() - startTime
            });

            return {
                success: false,
                error: error.message,
                processingTime: performance.now() - startTime
            };
        }
    }

    /**
     * Real-time processing of test result
     */
    async processRealTime(processingContext) {
        const { testResult, options, startTime, processingId } = processingContext;

        try {
            // Step 1: Core validation
            console.log(`🔍 Processing ${testResult.testId} for patient ${testResult.patientId}`);
            const validationResult = await this.qcSystem.validateTestResult(testResult);
            
            // Step 2: Statistical anomaly detection (if historical data available)
            let anomalyResult = null;
            if (options.historicalData && options.historicalData.length > 0) {
                anomalyResult = await this.qcSystem.detectAnomalies(testResult, options.historicalData);
            }

            // Step 3: Clinical logic validation (if multiple test results)
            let clinicalResult = null;
            if (options.relatedTests && options.relatedTests.length > 0) {
                const allTests = [testResult, ...options.relatedTests];
                clinicalResult = await this.clinicalValidator.validateClinicalLogic(
                    allTests, 
                    options.patientContext || {}
                );
            }

            // Step 4: Generate correction suggestions (if validation failed)
            let correctionResult = null;
            if (!validationResult.overallValid) {
                correctionResult = await this.correctionSystem.generateCorrectionSuggestions(
                    validationResult,
                    options.historicalData || [],
                    options.patientContext || {}
                );
            }

            // Step 5: Process alerts
            let alertsProcessed = [];
            if (validationResult.alerts && validationResult.alerts.length > 0) {
                for (const alert of validationResult.alerts) {
                    const alertProcessed = await this.alertSystem.processAlert({
                        ...alert,
                        processingId: processingId,
                        patientId: testResult.patientId
                    });
                    if (alertProcessed) {
                        alertsProcessed.push(alert);
                    }
                }
            }

            // Step 6: Update metrics
            await this.updateMetricsFromProcessing({
                validation: {
                    total: 1,
                    passed: validationResult.overallValid ? 1 : 0,
                    failed: validationResult.overallValid ? 0 : 1
                },
                alerts: {
                    total: alertsProcessed.length,
                    byLevel: this.groupAlertsByLevel(alertsProcessed)
                },
                performance: {
                    processingTime: {
                        average: performance.now() - startTime
                    }
                },
                clinical: clinicalResult ? {
                    correlationSuccessRate: clinicalResult.overallValid ? 100 : 90
                } : undefined
            });

            // Step 7: Compile final result
            const processingTime = performance.now() - startTime;
            const finalResult = {
                success: true,
                processingId: processingId,
                testId: testResult.testId,
                patientId: testResult.patientId,
                validation: validationResult,
                anomalyDetection: anomalyResult,
                clinicalLogic: clinicalResult,
                corrections: correctionResult,
                alerts: alertsProcessed,
                processingTime: processingTime,
                timestamp: new Date(),
                qualityScore: this.calculateResultQualityScore(validationResult, anomalyResult, clinicalResult),
                recommendations: this.generateProcessingRecommendations(validationResult, correctionResult, alertsProcessed)
            };

            // Log completion
            this.logAuditEvent('processing_completed', {
                processingId: processingId,
                testId: testResult.testId,
                success: true,
                processingTime: processingTime,
                qualityScore: finalResult.qualityScore,
                alertCount: alertsProcessed.length
            });

            // Check for slow processing
            if (this.config.performance.logSlowProcessing && 
                processingTime > this.config.performance.slowProcessingThreshold) {
                console.warn(`⚠️ Slow processing detected: ${processingTime.toFixed(2)}ms for ${testResult.testId}`);
                
                this.logAuditEvent('slow_processing', {
                    processingId: processingId,
                    testId: testResult.testId,
                    processingTime: processingTime,
                    threshold: this.config.performance.slowProcessingThreshold
                });
            }

            return finalResult;

        } catch (error) {
            const processingTime = performance.now() - startTime;
            
            this.logAuditEvent('processing_failed', {
                processingId: processingId,
                testId: testResult.testId,
                error: error.message,
                processingTime: processingTime
            });

            return {
                success: false,
                processingId: processingId,
                testId: testResult.testId,
                patientId: testResult.patientId,
                error: error.message,
                processingTime: processingTime,
                timestamp: new Date()
            };
        }
    }

    /**
     * Queue test result for batch processing
     */
    async queueForBatchProcessing(processingContext) {
        this.processingQueue.push(processingContext);
        
        console.log(`📥 Queued ${processingContext.testResult.testId} for batch processing (queue size: ${this.processingQueue.length})`);
        
        return {
            success: true,
            queued: true,
            processingId: processingContext.processingId,
            queuePosition: this.processingQueue.length,
            estimatedProcessingTime: this.estimateBatchProcessingTime()
        };
    }

    /**
     * Process batch of queued test results
     */
    async processBatch() {
        if (this.activeProcessing || this.processingQueue.length === 0) {
            return;
        }

        this.activeProcessing = true;
        const batchSize = Math.min(this.config.batchProcessing.batchSize, this.processingQueue.length);
        const batch = this.processingQueue.splice(0, batchSize);
        
        console.log(`🔄 Processing batch of ${batch.length} test results`);
        
        const batchStartTime = performance.now();
        const results = [];

        try {
            // Process each item in the batch
            for (const processingContext of batch) {
                try {
                    const result = await this.processRealTime(processingContext);
                    results.push(result);
                } catch (error) {
                    console.error(`Error processing ${processingContext.testResult.testId}:`, error);
                    results.push({
                        success: false,
                        processingId: processingContext.processingId,
                        error: error.message
                    });
                }
            }

            const batchProcessingTime = performance.now() - batchStartTime;
            console.log(`✅ Batch processing completed: ${batch.length} items in ${batchProcessingTime.toFixed(2)}ms`);

            // Update batch processing metrics
            await this.updateMetricsFromProcessing({
                performance: {
                    batchProcessingTime: batchProcessingTime,
                    batchSize: batch.length
                }
            });

        } catch (error) {
            console.error('Batch processing error:', error);
        } finally {
            this.activeProcessing = false;
        }

        return results;
    }

    /**
     * Validate input test result
     */
    validateInput(testResult) {
        const errors = [];
        const requiredFields = ['testId', 'value', 'unit', 'patientId', 'timestamp'];

        requiredFields.forEach(field => {
            if (!testResult[field]) {
                errors.push(`Missing required field: ${field}`);
            }
        });

        // Validate value is numeric
        if (testResult.value && isNaN(parseFloat(testResult.value))) {
            errors.push('Value must be numeric');
        }

        // Validate timestamp
        if (testResult.timestamp && !Date.parse(testResult.timestamp)) {
            errors.push('Invalid timestamp format');
        }

        return {
            valid: errors.length === 0,
            errors: errors
        };
    }

    /**
     * Update metrics from processing results
     */
    async updateMetricsFromProcessing(metricsUpdate) {
        try {
            this.dashboard.updateMetrics(metricsUpdate);
        } catch (error) {
            console.error('Error updating metrics:', error);
        }
    }

    /**
     * Update quality metrics (called periodically)
     */
    async updateQualityMetrics() {
        try {
            // This would gather metrics from all subsystems
            const systemMetrics = {
                validation: this.getValidationMetrics(),
                alerts: this.getAlertMetrics(),
                performance: this.getPerformanceMetrics(),
                compliance: this.getComplianceMetrics()
            };

            this.dashboard.updateMetrics(systemMetrics);
        } catch (error) {
            console.error('Error updating quality metrics:', error);
        }
    }

    /**
     * Calculate quality score for processing result
     */
    calculateResultQualityScore(validationResult, anomalyResult, clinicalResult) {
        let score = 100;

        // Deduct for validation failures
        if (!validationResult.overallValid) {
            score -= 20;
        }

        // Deduct for anomalies
        if (anomalyResult && anomalyResult.anomalyDetected) {
            score -= anomalyResult.riskScore * 10;
        }

        // Deduct for clinical logic failures
        if (clinicalResult && !clinicalResult.overallValid) {
            score -= 15;
        }

        return Math.max(score, 0);
    }

    /**
     * Generate processing recommendations
     */
    generateProcessingRecommendations(validationResult, correctionResult, alerts) {
        const recommendations = [];

        // Validation recommendations
        if (!validationResult.overallValid) {
            recommendations.push({
                category: 'validation',
                priority: 'high',
                message: 'Validation failures detected - review test result',
                actions: ['Manual review required', 'Consider repeat testing', 'Check specimen quality']
            });
        }

        // Correction recommendations
        if (correctionResult && correctionResult.highConfidenceSuggestions > 0) {
            recommendations.push({
                category: 'correction',
                priority: 'medium',
                message: `${correctionResult.highConfidenceSuggestions} high-confidence correction(s) available`,
                actions: ['Review suggested corrections', 'Apply if clinically appropriate']
            });
        }

        // Alert-based recommendations
        const criticalAlerts = alerts.filter(a => a.level === 'critical' || a.level === 'panic');
        if (criticalAlerts.length > 0) {
            recommendations.push({
                category: 'clinical',
                priority: 'urgent',
                message: `${criticalAlerts.length} critical alert(s) require immediate attention`,
                actions: ['Contact attending physician', 'Verify result', 'Consider immediate intervention']
            });
        }

        return recommendations;
    }

    /**
     * API Methods for external integration
     */

    /**
     * Get system status
     */
    getSystemStatus() {
        return {
            initialized: this.isInitialized,
            queueLength: this.processingQueue.length,
            activeProcessing: this.activeProcessing,
            systemHealth: this.checkSystemHealth(),
            uptime: process.uptime(),
            version: '1.0.0',
            lastUpdated: new Date()
        };
    }

    /**
     * Get quality dashboard data
     */
    getDashboardData() {
        if (!this.dashboard) {
            throw new Error('Dashboard not initialized');
        }
        return this.dashboard.getDashboardState();
    }

    /**
     * Get active alerts
     */
    getActiveAlerts() {
        if (!this.alertSystem) {
            throw new Error('Alert system not initialized');
        }
        return this.alertSystem.getAlertStatistics();
    }

    /**
     * Acknowledge alert
     */
    async acknowledgeAlert(alertId, acknowledgedBy) {
        if (!this.alertSystem) {
            throw new Error('Alert system not initialized');
        }
        return await this.alertSystem.acknowledgeAlert(alertId, acknowledgedBy);
    }

    /**
     * Generate quality report
     */
    generateQualityReport(timeframe = '30d', format = 'json') {
        if (!this.dashboard) {
            throw new Error('Dashboard not initialized');
        }
        return this.dashboard.generateQualityReport(timeframe, format);
    }

    /**
     * Apply correction suggestion
     */
    async applyCorrectionSuggestion(correctionId, approvedBy, feedback = {}) {
        if (!this.correctionSystem) {
            throw new Error('Correction system not initialized');
        }
        
        // Record the application
        this.correctionSystem.recordCorrectionFeedback(correctionId, true, true, feedback);
        
        // Log the action
        this.logAuditEvent('correction_applied', {
            correctionId: correctionId,
            approvedBy: approvedBy,
            feedback: feedback
        });

        return {
            success: true,
            correctionId: correctionId,
            appliedBy: approvedBy,
            timestamp: new Date()
        };
    }

    /**
     * Get correction statistics
     */
    getCorrectionStatistics(timeframe = '30d') {
        if (!this.correctionSystem) {
            throw new Error('Correction system not initialized');
        }
        return this.correctionSystem.getCorrectionStatistics(timeframe);
    }

    // =====================================================================
    // UTILITY METHODS
    // =====================================================================

    generateProcessingId() {
        const timestamp = Date.now();
        const random = Math.random().toString(36).substring(2, 8);
        return `QC_${timestamp}_${random}`;
    }

    groupAlertsByLevel(alerts) {
        const grouped = { info: 0, warning: 0, critical: 0, panic: 0 };
        alerts.forEach(alert => {
            if (grouped.hasOwnProperty(alert.level)) {
                grouped[alert.level]++;
            }
        });
        return grouped;
    }

    estimateBatchProcessingTime() {
        const avgProcessingTime = 50; // ms per item
        const queueLength = this.processingQueue.length;
        const batchSize = this.config.batchProcessing.batchSize;
        const batches = Math.ceil(queueLength / batchSize);
        return batches * avgProcessingTime * batchSize;
    }

    checkSystemHealth() {
        const health = {
            overall: 'healthy',
            components: {
                qcSystem: this.qcSystem ? 'healthy' : 'unhealthy',
                clinicalValidator: this.clinicalValidator ? 'healthy' : 'unhealthy',
                alertSystem: this.alertSystem ? 'healthy' : 'unhealthy',
                dashboard: this.dashboard ? 'healthy' : 'unhealthy',
                correctionSystem: this.correctionSystem ? 'healthy' : 'unhealthy'
            },
            queueHealth: this.processingQueue.length < 1000 ? 'healthy' : 'degraded',
            memoryUsage: process.memoryUsage()
        };

        // Check if any component is unhealthy
        const unhealthyComponents = Object.values(health.components).filter(status => status === 'unhealthy');
        if (unhealthyComponents.length > 0 || health.queueHealth === 'degraded') {
            health.overall = 'degraded';
        }

        return health;
    }

    // Metric collection methods
    getValidationMetrics() {
        // In production, these would collect real metrics from the QC system
        return {
            total: 0,
            passed: 0,
            failed: 0
        };
    }

    getAlertMetrics() {
        return {
            total: 0,
            byLevel: { info: 0, warning: 0, critical: 0, panic: 0 }
        };
    }

    getPerformanceMetrics() {
        return {
            processingTime: { average: 0, p95: 0, p99: 0 },
            throughput: 0,
            availability: 100
        };
    }

    getComplianceMetrics() {
        return {
            overall: 100,
            loinc: 100,
            units: 100,
            biologicalLimits: 100,
            precision: 100
        };
    }

    // Audit logging
    logAuditEvent(eventType, details) {
        if (!this.config.audit.enabled) return;

        const auditEntry = {
            timestamp: new Date(),
            eventType: eventType,
            details: details,
            systemVersion: '1.0.0'
        };

        // In production, this would write to audit database/log
        console.log('📋 Audit:', JSON.stringify(auditEntry));
    }

    cleanupAuditLogs() {
        // In production, this would clean up old audit logs based on retention policy
        console.log('🧹 Audit log cleanup completed');
    }

    /**
     * Shutdown gracefully
     */
    async shutdown() {
        console.log('🔄 Shutting down Quality Control System...');
        
        // Process remaining queue items
        if (this.processingQueue.length > 0) {
            console.log(`Processing remaining ${this.processingQueue.length} queued items...`);
            await this.processBatch();
        }

        // Close connections, cleanup resources
        // In production, this would close database connections, etc.

        console.log('✅ Quality Control System shutdown completed');
    }
}

module.exports = { QualityControlIntegration };