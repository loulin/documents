/**
 * Quality Metrics Dashboard Module
 * Comprehensive monitoring and visualization system for laboratory quality control metrics
 * Real-time dashboard with compliance tracking, trend analysis, and reporting
 * 
 * Part of the Laboratory Quality Control System v1.0
 */

class QualityMetricsDashboard {
    constructor(config = {}) {
        this.config = config;
        this.metrics = {
            validation: {
                total: 0,
                passed: 0,
                failed: 0,
                successRate: 100,
                trend: []
            },
            alerts: {
                total: 0,
                byLevel: { info: 0, warning: 0, critical: 0, panic: 0 },
                responseTime: { average: 0, p95: 0, p99: 0 },
                escalationRate: 0,
                trend: []
            },
            compliance: {
                overall: 100,
                loinc: 100,
                units: 100,
                biologicalLimits: 100,
                precision: 100,
                trend: []
            },
            performance: {
                processingTime: { average: 0, p95: 0, p99: 0 },
                throughput: 0,
                availability: 100,
                trend: []
            },
            clinical: {
                correlationSuccessRate: 100,
                diseasePatternDetection: 0,
                interventionsSuggested: 0,
                trend: []
            }
        };
        
        this.alerts = [];
        this.reports = [];
        this.dashboardData = {};
        this.refreshInterval = config.refreshInterval || 30000; // 30 seconds
        this.historicalData = new Map();
        
        this.initializeDashboard();
        this.startPeriodicUpdates();
    }

    /**
     * Initialize dashboard components and data structures
     */
    initializeDashboard() {
        this.dashboardData = {
            realTimeMetrics: this.generateRealTimeMetrics(),
            trendCharts: this.generateTrendCharts(),
            alertSummary: this.generateAlertSummary(),
            complianceStatus: this.generateComplianceStatus(),
            performanceIndicators: this.generatePerformanceIndicators(),
            qualityScore: this.calculateOverallQualityScore(),
            recommendations: this.generateRecommendations(),
            lastUpdated: new Date()
        };
    }

    /**
     * Update metrics with new data from quality control system
     */
    updateMetrics(newData) {
        const timestamp = new Date();
        
        // Update validation metrics
        if (newData.validation) {
            this.updateValidationMetrics(newData.validation, timestamp);
        }
        
        // Update alert metrics
        if (newData.alerts) {
            this.updateAlertMetrics(newData.alerts, timestamp);
        }
        
        // Update compliance metrics
        if (newData.compliance) {
            this.updateComplianceMetrics(newData.compliance, timestamp);
        }
        
        // Update performance metrics
        if (newData.performance) {
            this.updatePerformanceMetrics(newData.performance, timestamp);
        }
        
        // Update clinical metrics
        if (newData.clinical) {
            this.updateClinicalMetrics(newData.clinical, timestamp);
        }
        
        // Recalculate derived metrics
        this.recalculateDerivedMetrics();
        
        // Update dashboard data
        this.refreshDashboardData();
        
        // Store historical data
        this.storeHistoricalData(timestamp, newData);
    }

    /**
     * Update validation metrics
     */
    updateValidationMetrics(validationData, timestamp) {
        this.metrics.validation.total += validationData.total || 0;
        this.metrics.validation.passed += validationData.passed || 0;
        this.metrics.validation.failed += validationData.failed || 0;
        
        this.metrics.validation.successRate = this.metrics.validation.total > 0 ? 
            (this.metrics.validation.passed / this.metrics.validation.total * 100) : 100;
        
        // Add to trend data
        this.metrics.validation.trend.push({
            timestamp: timestamp,
            total: validationData.total || 0,
            passed: validationData.passed || 0,
            failed: validationData.failed || 0,
            successRate: this.metrics.validation.successRate
        });
        
        // Keep only last 1000 trend points
        if (this.metrics.validation.trend.length > 1000) {
            this.metrics.validation.trend = this.metrics.validation.trend.slice(-1000);
        }
    }

    /**
     * Update alert metrics
     */
    updateAlertMetrics(alertData, timestamp) {
        this.metrics.alerts.total += alertData.total || 0;
        
        // Update by level
        Object.keys(alertData.byLevel || {}).forEach(level => {
            this.metrics.alerts.byLevel[level] += alertData.byLevel[level] || 0;
        });
        
        // Update response time metrics
        if (alertData.responseTime) {
            this.metrics.alerts.responseTime = {
                average: alertData.responseTime.average || 0,
                p95: alertData.responseTime.p95 || 0,
                p99: alertData.responseTime.p99 || 0
            };
        }
        
        // Update escalation rate
        if (alertData.escalationRate !== undefined) {
            this.metrics.alerts.escalationRate = alertData.escalationRate;
        }
        
        // Add to trend data
        this.metrics.alerts.trend.push({
            timestamp: timestamp,
            total: alertData.total || 0,
            byLevel: { ...alertData.byLevel },
            escalationRate: this.metrics.alerts.escalationRate
        });
        
        // Trim trend data
        if (this.metrics.alerts.trend.length > 1000) {
            this.metrics.alerts.trend = this.metrics.alerts.trend.slice(-1000);
        }
    }

    /**
     * Update compliance metrics
     */
    updateComplianceMetrics(complianceData, timestamp) {
        Object.keys(complianceData).forEach(key => {
            if (this.metrics.compliance.hasOwnProperty(key)) {
                this.metrics.compliance[key] = complianceData[key];
            }
        });
        
        // Recalculate overall compliance
        const complianceValues = [
            this.metrics.compliance.loinc,
            this.metrics.compliance.units,
            this.metrics.compliance.biologicalLimits,
            this.metrics.compliance.precision
        ];
        
        this.metrics.compliance.overall = 
            complianceValues.reduce((sum, val) => sum + val, 0) / complianceValues.length;
        
        // Add to trend data
        this.metrics.compliance.trend.push({
            timestamp: timestamp,
            overall: this.metrics.compliance.overall,
            loinc: this.metrics.compliance.loinc,
            units: this.metrics.compliance.units,
            biologicalLimits: this.metrics.compliance.biologicalLimits,
            precision: this.metrics.compliance.precision
        });
        
        // Trim trend data
        if (this.metrics.compliance.trend.length > 1000) {
            this.metrics.compliance.trend = this.metrics.compliance.trend.slice(-1000);
        }
    }

    /**
     * Update performance metrics
     */
    updatePerformanceMetrics(performanceData, timestamp) {
        if (performanceData.processingTime) {
            this.metrics.performance.processingTime = {
                average: performanceData.processingTime.average || 0,
                p95: performanceData.processingTime.p95 || 0,
                p99: performanceData.processingTime.p99 || 0
            };
        }
        
        if (performanceData.throughput !== undefined) {
            this.metrics.performance.throughput = performanceData.throughput;
        }
        
        if (performanceData.availability !== undefined) {
            this.metrics.performance.availability = performanceData.availability;
        }
        
        // Add to trend data
        this.metrics.performance.trend.push({
            timestamp: timestamp,
            processingTime: { ...this.metrics.performance.processingTime },
            throughput: this.metrics.performance.throughput,
            availability: this.metrics.performance.availability
        });
        
        // Trim trend data
        if (this.metrics.performance.trend.length > 1000) {
            this.metrics.performance.trend = this.metrics.performance.trend.slice(-1000);
        }
    }

    /**
     * Update clinical metrics
     */
    updateClinicalMetrics(clinicalData, timestamp) {
        Object.keys(clinicalData).forEach(key => {
            if (this.metrics.clinical.hasOwnProperty(key)) {
                this.metrics.clinical[key] = clinicalData[key];
            }
        });
        
        // Add to trend data
        this.metrics.clinical.trend.push({
            timestamp: timestamp,
            correlationSuccessRate: this.metrics.clinical.correlationSuccessRate,
            diseasePatternDetection: this.metrics.clinical.diseasePatternDetection,
            interventionsSuggested: this.metrics.clinical.interventionsSuggested
        });
        
        // Trim trend data
        if (this.metrics.clinical.trend.length > 1000) {
            this.metrics.clinical.trend = this.metrics.clinical.trend.slice(-1000);
        }
    }

    /**
     * Generate real-time metrics display
     */
    generateRealTimeMetrics() {
        return {
            dataQualityScore: this.calculateOverallQualityScore(),
            validationsToday: this.getTodayValidations(),
            alertsToday: this.getTodayAlerts(),
            systemAvailability: this.metrics.performance.availability,
            averageProcessingTime: this.metrics.performance.processingTime.average,
            complianceScore: this.metrics.compliance.overall,
            criticalAlertsActive: this.getActiveCriticalAlerts(),
            lastValidation: this.getLastValidationTime()
        };
    }

    /**
     * Generate trend charts data for visualization
     */
    generateTrendCharts() {
        const last24h = this.getDataForTimeframe('24h');
        const last7d = this.getDataForTimeframe('7d');
        const last30d = this.getDataForTimeframe('30d');
        
        return {
            validationTrend: {
                '24h': this.prepareValidationTrendData(last24h),
                '7d': this.prepareValidationTrendData(last7d),
                '30d': this.prepareValidationTrendData(last30d)
            },
            alertTrend: {
                '24h': this.prepareAlertTrendData(last24h),
                '7d': this.prepareAlertTrendData(last7d),
                '30d': this.prepareAlertTrendData(last30d)
            },
            complianceTrend: {
                '24h': this.prepareComplianceTrendData(last24h),
                '7d': this.prepareComplianceTrendData(last7d),
                '30d': this.prepareComplianceTrendData(last30d)
            },
            performanceTrend: {
                '24h': this.preparePerformanceTrendData(last24h),
                '7d': this.preparePerformanceTrendData(last7d),
                '30d': this.preparePerformanceTrendData(last30d)
            }
        };
    }

    /**
     * Generate alert summary for dashboard
     */
    generateAlertSummary() {
        const activeAlerts = this.getActiveAlerts();
        const recentAlerts = this.getRecentAlerts('24h');
        
        return {
            active: {
                total: activeAlerts.length,
                panic: activeAlerts.filter(a => a.level === 'panic').length,
                critical: activeAlerts.filter(a => a.level === 'critical').length,
                warning: activeAlerts.filter(a => a.level === 'warning').length,
                info: activeAlerts.filter(a => a.level === 'info').length
            },
            recent: {
                total: recentAlerts.length,
                panic: recentAlerts.filter(a => a.level === 'panic').length,
                critical: recentAlerts.filter(a => a.level === 'critical').length,
                warning: recentAlerts.filter(a => a.level === 'warning').length,
                info: recentAlerts.filter(a => a.level === 'info').length
            },
            responseTime: this.metrics.alerts.responseTime,
            escalationRate: this.metrics.alerts.escalationRate,
            topAlertTypes: this.getTopAlertTypes(recentAlerts)
        };
    }

    /**
     * Generate compliance status report
     */
    generateComplianceStatus() {
        return {
            overall: {
                score: this.metrics.compliance.overall,
                status: this.getComplianceStatus(this.metrics.compliance.overall),
                trend: this.getComplianceTrend()
            },
            components: {
                loinc: {
                    score: this.metrics.compliance.loinc,
                    status: this.getComplianceStatus(this.metrics.compliance.loinc),
                    issues: this.getLoincComplianceIssues()
                },
                units: {
                    score: this.metrics.compliance.units,
                    status: this.getComplianceStatus(this.metrics.compliance.units),
                    issues: this.getUnitComplianceIssues()
                },
                biologicalLimits: {
                    score: this.metrics.compliance.biologicalLimits,
                    status: this.getComplianceStatus(this.metrics.compliance.biologicalLimits),
                    issues: this.getBiologicalLimitsIssues()
                },
                precision: {
                    score: this.metrics.compliance.precision,
                    status: this.getComplianceStatus(this.metrics.compliance.precision),
                    issues: this.getPrecisionComplianceIssues()
                }
            },
            recommendations: this.generateComplianceRecommendations()
        };
    }

    /**
     * Generate performance indicators
     */
    generatePerformanceIndicators() {
        return {
            processing: {
                averageTime: this.metrics.performance.processingTime.average,
                p95Time: this.metrics.performance.processingTime.p95,
                p99Time: this.metrics.performance.processingTime.p99,
                target: this.config.performanceTargets?.processingTimeP95 || 50,
                status: this.getPerformanceStatus('processing')
            },
            throughput: {
                current: this.metrics.performance.throughput,
                target: this.config.performanceTargets?.throughput || 1000,
                status: this.getPerformanceStatus('throughput')
            },
            availability: {
                current: this.metrics.performance.availability,
                target: this.config.performanceTargets?.availability || 99.9,
                status: this.getPerformanceStatus('availability'),
                uptime: this.calculateUptime()
            },
            errorRate: {
                current: this.calculateErrorRate(),
                target: this.config.performanceTargets?.errorRate || 0.1,
                status: this.getPerformanceStatus('errorRate')
            }
        };
    }

    /**
     * Calculate overall quality score
     */
    calculateOverallQualityScore() {
        const weights = {
            validation: 0.25,
            compliance: 0.25,
            performance: 0.20,
            alerts: 0.20,
            clinical: 0.10
        };
        
        const scores = {
            validation: this.metrics.validation.successRate,
            compliance: this.metrics.compliance.overall,
            performance: this.calculatePerformanceScore(),
            alerts: this.calculateAlertScore(),
            clinical: this.metrics.clinical.correlationSuccessRate
        };
        
        let overallScore = 0;
        Object.keys(weights).forEach(key => {
            overallScore += weights[key] * scores[key];
        });
        
        return Math.round(overallScore * 100) / 100;
    }

    /**
     * Calculate performance score
     */
    calculatePerformanceScore() {
        const targets = this.config.performanceTargets || {};
        const processingScore = this.metrics.performance.processingTime.p95 <= (targets.processingTimeP95 || 50) ? 100 : 80;
        const availabilityScore = this.metrics.performance.availability;
        const throughputScore = this.metrics.performance.throughput >= (targets.throughput || 1000) ? 100 : 80;
        
        return (processingScore + availabilityScore + throughputScore) / 3;
    }

    /**
     * Calculate alert score based on alert frequency and severity
     */
    calculateAlertScore() {
        const recentAlerts = this.getRecentAlerts('24h');
        const totalAlerts = recentAlerts.length;
        
        if (totalAlerts === 0) return 100;
        
        // Penalize based on alert severity
        const severityPenalties = { info: 0.1, warning: 1, critical: 5, panic: 10 };
        let totalPenalty = 0;
        
        recentAlerts.forEach(alert => {
            totalPenalty += severityPenalties[alert.level] || 0;
        });
        
        // Calculate score (max penalty of 100 gives score of 0)
        const score = Math.max(0, 100 - totalPenalty);
        return score;
    }

    /**
     * Generate recommendations based on current metrics
     */
    generateRecommendations() {
        const recommendations = [];
        
        // Validation recommendations
        if (this.metrics.validation.successRate < 95) {
            recommendations.push({
                category: 'validation',
                priority: 'high',
                title: 'Improve Validation Success Rate',
                description: `Current validation success rate is ${this.metrics.validation.successRate.toFixed(1)}%. Target is 95%+.`,
                actions: [
                    'Review validation rules for accuracy',
                    'Check for systematic data quality issues',
                    'Update reference ranges if needed',
                    'Provide additional training to laboratory staff'
                ]
            });
        }
        
        // Alert recommendations
        const criticalAlerts = this.getRecentAlerts('24h').filter(a => a.level === 'critical' || a.level === 'panic');
        if (criticalAlerts.length > 5) {
            recommendations.push({
                category: 'alerts',
                priority: 'critical',
                title: 'High Critical Alert Frequency',
                description: `${criticalAlerts.length} critical/panic alerts in last 24 hours.`,
                actions: [
                    'Investigate root cause of critical values',
                    'Review specimen collection procedures',
                    'Check instrument calibration',
                    'Evaluate preanalytical factors'
                ]
            });
        }
        
        // Performance recommendations
        if (this.metrics.performance.processingTime.p95 > (this.config.performanceTargets?.processingTimeP95 || 50)) {
            recommendations.push({
                category: 'performance',
                priority: 'medium',
                title: 'Processing Time Optimization Needed',
                description: `95th percentile processing time is ${this.metrics.performance.processingTime.p95}ms. Target is ${this.config.performanceTargets?.processingTimeP95 || 50}ms.`,
                actions: [
                    'Optimize validation algorithms',
                    'Implement caching for frequent lookups',
                    'Scale system resources',
                    'Review database query performance'
                ]
            });
        }
        
        // Compliance recommendations
        if (this.metrics.compliance.overall < 98) {
            recommendations.push({
                category: 'compliance',
                priority: 'high',
                title: 'Compliance Improvement Required',
                description: `Overall compliance score is ${this.metrics.compliance.overall.toFixed(1)}%. Target is 98%+.`,
                actions: [
                    'Update LOINC code mappings',
                    'Standardize unit conversions',
                    'Review biological limit definitions',
                    'Implement stricter precision controls'
                ]
            });
        }
        
        return recommendations.sort((a, b) => {
            const priorityOrder = { critical: 0, high: 1, medium: 2, low: 3 };
            return priorityOrder[a.priority] - priorityOrder[b.priority];
        });
    }

    /**
     * Generate comprehensive quality report
     */
    generateQualityReport(timeframe = '30d', format = 'json') {
        const data = this.getDataForTimeframe(timeframe);
        const report = {
            reportId: `QC_REPORT_${Date.now()}`,
            generatedAt: new Date(),
            timeframe: timeframe,
            summary: {
                overallQualityScore: this.calculateOverallQualityScore(),
                totalValidations: this.sumValidations(data),
                totalAlerts: this.sumAlerts(data),
                complianceScore: this.metrics.compliance.overall,
                systemAvailability: this.calculateAverageAvailability(data)
            },
            detailed: {
                validation: this.generateValidationReport(data),
                alerts: this.generateAlertReport(data),
                compliance: this.generateDetailedComplianceReport(data),
                performance: this.generatePerformanceReport(data),
                clinical: this.generateClinicalReport(data)
            },
            trends: {
                qualityScoreTrend: this.calculateQualityScoreTrend(data),
                alertTrend: this.calculateAlertTrend(data),
                complianceTrend: this.calculateComplianceTrendForReport(data)
            },
            recommendations: this.generateReportRecommendations(data),
            appendices: {
                methodology: this.getMethodologyNotes(),
                definitions: this.getDefinitions(),
                standards: this.getStandardsReference()
            }
        };
        
        if (format === 'json') {
            return report;
        } else if (format === 'html') {
            return this.formatReportAsHTML(report);
        } else if (format === 'pdf') {
            return this.formatReportAsPDF(report);
        }
        
        return report;
    }

    /**
     * Export dashboard data for external systems
     */
    exportDashboardData(format = 'json') {
        const exportData = {
            exportId: `DASHBOARD_EXPORT_${Date.now()}`,
            exportedAt: new Date(),
            realTimeMetrics: this.generateRealTimeMetrics(),
            currentMetrics: this.metrics,
            dashboardData: this.dashboardData,
            alerts: this.getActiveAlerts(),
            configuration: this.config
        };
        
        switch (format) {
            case 'json':
                return JSON.stringify(exportData, null, 2);
            case 'csv':
                return this.formatAsCSV(exportData);
            case 'xml':
                return this.formatAsXML(exportData);
            default:
                return exportData;
        }
    }

    // =====================================================================
    // HELPER METHODS
    // =====================================================================

    /**
     * Refresh dashboard data
     */
    refreshDashboardData() {
        this.dashboardData = {
            realTimeMetrics: this.generateRealTimeMetrics(),
            trendCharts: this.generateTrendCharts(),
            alertSummary: this.generateAlertSummary(),
            complianceStatus: this.generateComplianceStatus(),
            performanceIndicators: this.generatePerformanceIndicators(),
            qualityScore: this.calculateOverallQualityScore(),
            recommendations: this.generateRecommendations(),
            lastUpdated: new Date()
        };
    }

    /**
     * Recalculate derived metrics
     */
    recalculateDerivedMetrics() {
        // Update success rates
        this.metrics.validation.successRate = this.metrics.validation.total > 0 ? 
            (this.metrics.validation.passed / this.metrics.validation.total * 100) : 100;
        
        // Update overall compliance
        const complianceValues = [
            this.metrics.compliance.loinc,
            this.metrics.compliance.units,
            this.metrics.compliance.biologicalLimits,
            this.metrics.compliance.precision
        ];
        this.metrics.compliance.overall = 
            complianceValues.reduce((sum, val) => sum + val, 0) / complianceValues.length;
    }

    /**
     * Store historical data for trending
     */
    storeHistoricalData(timestamp, data) {
        const key = timestamp.toISOString().substring(0, 10); // Date only
        if (!this.historicalData.has(key)) {
            this.historicalData.set(key, []);
        }
        this.historicalData.get(key).push({ timestamp, data });
        
        // Keep only last 90 days
        const cutoffDate = new Date();
        cutoffDate.setDate(cutoffDate.getDate() - 90);
        
        Array.from(this.historicalData.keys()).forEach(key => {
            if (new Date(key) < cutoffDate) {
                this.historicalData.delete(key);
            }
        });
    }

    /**
     * Get data for specific timeframe
     */
    getDataForTimeframe(timeframe) {
        const now = new Date();
        const timeframes = {
            '1h': 60 * 60 * 1000,
            '24h': 24 * 60 * 60 * 1000,
            '7d': 7 * 24 * 60 * 60 * 1000,
            '30d': 30 * 24 * 60 * 60 * 1000
        };
        
        const cutoffTime = new Date(now.getTime() - timeframes[timeframe]);
        const data = [];
        
        this.historicalData.forEach((dayData, date) => {
            if (new Date(date) >= cutoffTime) {
                data.push(...dayData);
            }
        });
        
        return data.filter(item => item.timestamp >= cutoffTime);
    }

    /**
     * Get today's validations count
     */
    getTodayValidations() {
        const today = new Date().toISOString().substring(0, 10);
        const todayData = this.historicalData.get(today) || [];
        return todayData.reduce((sum, item) => sum + (item.data.validation?.total || 0), 0);
    }

    /**
     * Get today's alerts count
     */
    getTodayAlerts() {
        const today = new Date().toISOString().substring(0, 10);
        const todayData = this.historicalData.get(today) || [];
        return todayData.reduce((sum, item) => sum + (item.data.alerts?.total || 0), 0);
    }

    /**
     * Get active critical alerts count
     */
    getActiveCriticalAlerts() {
        return this.alerts.filter(a => 
            (a.level === 'critical' || a.level === 'panic') && 
            a.status === 'active'
        ).length;
    }

    /**
     * Get last validation time
     */
    getLastValidationTime() {
        // In production, this would come from the actual validation system
        return new Date();
    }

    /**
     * Get active alerts
     */
    getActiveAlerts() {
        return this.alerts.filter(a => a.status === 'active');
    }

    /**
     * Get recent alerts for timeframe
     */
    getRecentAlerts(timeframe) {
        const data = this.getDataForTimeframe(timeframe);
        const alerts = [];
        data.forEach(item => {
            if (item.data.alerts && item.data.alerts.details) {
                alerts.push(...item.data.alerts.details);
            }
        });
        return alerts;
    }

    /**
     * Get compliance status text
     */
    getComplianceStatus(score) {
        if (score >= 98) return 'excellent';
        if (score >= 95) return 'good';
        if (score >= 90) return 'acceptable';
        if (score >= 80) return 'needs_improvement';
        return 'poor';
    }

    /**
     * Get performance status
     */
    getPerformanceStatus(metric) {
        const targets = this.config.performanceTargets || {};
        const current = this.metrics.performance;
        
        switch (metric) {
            case 'processing':
                return current.processingTime.p95 <= (targets.processingTimeP95 || 50) ? 'good' : 'needs_improvement';
            case 'throughput':
                return current.throughput >= (targets.throughput || 1000) ? 'good' : 'needs_improvement';
            case 'availability':
                return current.availability >= (targets.availability || 99.9) ? 'excellent' : 'needs_improvement';
            case 'errorRate':
                return this.calculateErrorRate() <= (targets.errorRate || 0.1) ? 'good' : 'needs_improvement';
            default:
                return 'unknown';
        }
    }

    /**
     * Calculate uptime
     */
    calculateUptime() {
        // Simplified calculation - in production would use actual uptime data
        return this.metrics.performance.availability;
    }

    /**
     * Calculate error rate
     */
    calculateErrorRate() {
        return this.metrics.validation.total > 0 ? 
            (this.metrics.validation.failed / this.metrics.validation.total * 100) : 0;
    }

    /**
     * Start periodic updates
     */
    startPeriodicUpdates() {
        setInterval(() => {
            this.refreshDashboardData();
        }, this.refreshInterval);
    }

    /**
     * Prepare validation trend data for charts
     */
    prepareValidationTrendData(data) {
        return data.map(item => ({
            timestamp: item.timestamp,
            total: item.data.validation?.total || 0,
            passed: item.data.validation?.passed || 0,
            failed: item.data.validation?.failed || 0,
            successRate: item.data.validation?.successRate || 100
        }));
    }

    /**
     * Prepare alert trend data for charts
     */
    prepareAlertTrendData(data) {
        return data.map(item => ({
            timestamp: item.timestamp,
            total: item.data.alerts?.total || 0,
            info: item.data.alerts?.byLevel?.info || 0,
            warning: item.data.alerts?.byLevel?.warning || 0,
            critical: item.data.alerts?.byLevel?.critical || 0,
            panic: item.data.alerts?.byLevel?.panic || 0
        }));
    }

    /**
     * Prepare compliance trend data for charts
     */
    prepareComplianceTrendData(data) {
        return data.map(item => ({
            timestamp: item.timestamp,
            overall: item.data.compliance?.overall || 100,
            loinc: item.data.compliance?.loinc || 100,
            units: item.data.compliance?.units || 100,
            biologicalLimits: item.data.compliance?.biologicalLimits || 100,
            precision: item.data.compliance?.precision || 100
        }));
    }

    /**
     * Prepare performance trend data for charts
     */
    preparePerformanceTrendData(data) {
        return data.map(item => ({
            timestamp: item.timestamp,
            processingTime: item.data.performance?.processingTime?.average || 0,
            throughput: item.data.performance?.throughput || 0,
            availability: item.data.performance?.availability || 100
        }));
    }

    // Additional helper methods would be implemented here for:
    // - getTopAlertTypes()
    // - getComplianceTrend()
    // - getLoincComplianceIssues()
    // - getUnitComplianceIssues()
    // - getBiologicalLimitsIssues()
    // - getPrecisionComplianceIssues()
    // - generateComplianceRecommendations()
    // - Report generation methods
    // - Data formatting methods (CSV, XML, PDF, HTML)
    
    /**
     * Get dashboard state for external access
     */
    getDashboardState() {
        return {
            metrics: this.metrics,
            dashboardData: this.dashboardData,
            lastUpdated: this.dashboardData.lastUpdated,
            qualityScore: this.calculateOverallQualityScore(),
            systemStatus: this.getSystemStatus(),
            recommendations: this.generateRecommendations()
        };
    }

    /**
     * Get system status overview
     */
    getSystemStatus() {
        const qualityScore = this.calculateOverallQualityScore();
        const activeAlerts = this.getActiveAlerts();
        const criticalAlerts = activeAlerts.filter(a => a.level === 'critical' || a.level === 'panic');
        
        let status = 'operational';
        if (criticalAlerts.length > 0) {
            status = 'degraded';
        }
        if (qualityScore < 80) {
            status = 'major_issues';
        }
        if (this.metrics.performance.availability < 95) {
            status = 'outage';
        }
        
        return {
            status: status,
            qualityScore: qualityScore,
            activeAlerts: activeAlerts.length,
            criticalAlerts: criticalAlerts.length,
            availability: this.metrics.performance.availability
        };
    }
}

module.exports = { QualityMetricsDashboard };