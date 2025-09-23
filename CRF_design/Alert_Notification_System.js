/**
 * Alert and Notification System Module
 * Multi-level alert system with 4 severity levels for laboratory quality control
 * Includes notification channels, escalation protocols, and emergency response
 * 
 * Part of the Laboratory Quality Control System v1.0
 */

const EventEmitter = require('events');

class AlertNotificationSystem extends EventEmitter {
    constructor(config = {}) {
        super();
        this.config = config;
        this.alertHistory = [];
        this.activeAlerts = new Map();
        this.notificationChannels = new Map();
        this.escalationPolicies = new Map();
        this.alertMetrics = {
            totalAlerts: 0,
            alertCounts: { info: 0, warning: 0, critical: 0, panic: 0 },
            responseTimeStats: { info: [], warning: [], critical: [], panic: [] },
            escalationCounts: { warning: 0, critical: 0, panic: 0 }
        };
        
        this.initializeNotificationChannels();
        this.initializeEscalationPolicies();
        this.initializeAlertLevels();
        
        // Start background processes
        this.startAlertProcessor();
        this.startEscalationMonitor();
    }

    /**
     * Initialize notification channels (email, SMS, pager, EMR integration)
     */
    initializeNotificationChannels() {
        // Email notification channel
        this.notificationChannels.set('email', {
            type: 'email',
            enabled: this.config.email?.enabled || true,
            config: {
                smtp: this.config.email?.smtp || 'smtp.hospital.org',
                from: this.config.email?.from || 'qc-system@hospital.org',
                templates: {
                    info: 'email_templates/info_alert.html',
                    warning: 'email_templates/warning_alert.html',
                    critical: 'email_templates/critical_alert.html',
                    panic: 'email_templates/panic_alert.html'
                }
            },
            send: async (alert, recipients) => {
                return await this.sendEmailAlert(alert, recipients);
            }
        });

        // SMS notification channel
        this.notificationChannels.set('sms', {
            type: 'sms',
            enabled: this.config.sms?.enabled || true,
            config: {
                gateway: this.config.sms?.gateway || 'twilio',
                emergencyNumbers: this.config.sms?.emergencyNumbers || [],
                maxMessageLength: 160
            },
            send: async (alert, recipients) => {
                return await this.sendSMSAlert(alert, recipients);
            }
        });

        // Pager notification channel
        this.notificationChannels.set('pager', {
            type: 'pager',
            enabled: this.config.pager?.enabled || true,
            config: {
                system: this.config.pager?.system || 'hospital_paging',
                urgentCodes: { critical: '911', panic: '999' }
            },
            send: async (alert, recipients) => {
                return await this.sendPagerAlert(alert, recipients);
            }
        });

        // EMR integration channel
        this.notificationChannels.set('emr', {
            type: 'emr_integration',
            enabled: this.config.emr?.enabled || true,
            config: {
                system: this.config.emr?.system || 'epic',
                autoFlagCritical: this.config.emr?.autoFlagCritical || true,
                endpoint: this.config.emr?.endpoint
            },
            send: async (alert, recipients) => {
                return await this.sendEMRAlert(alert, recipients);
            }
        });

        // Slack integration
        this.notificationChannels.set('slack', {
            type: 'slack',
            enabled: this.config.slack?.enabled || false,
            config: {
                webhookUrl: this.config.slack?.webhookUrl,
                channels: this.config.slack?.channels || ['#lab-alerts', '#quality-control']
            },
            send: async (alert, recipients) => {
                return await this.sendSlackAlert(alert, recipients);
            }
        });
    }

    /**
     * Initialize escalation policies for different alert levels
     */
    initializeEscalationPolicies() {
        // Info Level (Level 1) - Minor deviations, data quality notes
        this.escalationPolicies.set('info', {
            level: 1,
            priority: 'low',
            notificationDelay: 300000, // 5 minutes
            escalationRequired: false,
            autoAcknowledge: true,
            channels: ['email'],
            recipients: {
                primary: ['lab-quality@hospital.org'],
                escalation: []
            },
            responseTimeTarget: 24 * 60 * 60 * 1000, // 24 hours
            actions: [
                'log_for_quality_metrics',
                'add_to_weekly_report'
            ]
        });

        // Warning Level (Level 2) - Significant anomalies requiring review
        this.escalationPolicies.set('warning', {
            level: 2,
            priority: 'medium',
            notificationDelay: 60000, // 1 minute
            escalationRequired: false,
            autoAcknowledge: false,
            channels: ['email', 'slack'],
            recipients: {
                primary: ['lab-supervisor@hospital.org', 'care-team@hospital.org'],
                escalation: ['lab-manager@hospital.org']
            },
            responseTimeTarget: 4 * 60 * 60 * 1000, // 4 hours
            escalationTime: 8 * 60 * 60 * 1000, // 8 hours if no response
            actions: [
                'add_to_review_queue',
                'notify_care_team',
                'trigger_trending_analysis'
            ]
        });

        // Critical Level (Level 3) - Critical values requiring immediate attention
        this.escalationPolicies.set('critical', {
            level: 3,
            priority: 'high',
            notificationDelay: 5000, // 5 seconds
            escalationRequired: true,
            autoAcknowledge: false,
            channels: ['email', 'sms', 'emr'],
            recipients: {
                primary: ['attending-physician@hospital.org', 'lab-supervisor@hospital.org'],
                escalation: ['department-head@hospital.org', 'medical-director@hospital.org']
            },
            responseTimeTarget: 30 * 60 * 1000, // 30 minutes
            escalationTime: 15 * 60 * 1000, // 15 minutes if no response
            actions: [
                'notify_attending_physician',
                'flag_in_emr',
                'generate_intervention_recommendations',
                'create_incident_record'
            ]
        });

        // Panic Level (Level 4) - Life-threatening values requiring emergency response
        this.escalationPolicies.set('panic', {
            level: 4,
            priority: 'emergency',
            notificationDelay: 0, // Immediate
            escalationRequired: true,
            autoAcknowledge: false,
            immediateEscalation: true,
            emergencyProtocol: true,
            channels: ['sms', 'pager', 'emr', 'slack'],
            recipients: {
                primary: [
                    'emergency-response@hospital.org',
                    'attending-physician@hospital.org',
                    'lab-director@hospital.org'
                ],
                escalation: [
                    'medical-director@hospital.org',
                    'chief-of-staff@hospital.org'
                ],
                emergency: [
                    '+1234567890', // Emergency response team pager
                    '+0987654321'  // Medical director cell
                ]
            },
            responseTimeTarget: 5 * 60 * 1000, // 5 minutes
            escalationTime: 2 * 60 * 1000, // 2 minutes if no response
            actions: [
                'send_emergency_notification',
                'escalate_to_emergency_team',
                'log_critical_incident',
                'activate_emergency_protocol',
                'notify_administration'
            ]
        });
    }

    /**
     * Initialize alert level configurations
     */
    initializeAlertLevels() {
        this.alertLevels = {
            'info': {
                name: 'Information',
                icon: 'ℹ️',
                color: '#2196F3',
                priority: 1
            },
            'warning': {
                name: 'Warning',
                icon: '⚠️',
                color: '#FF9800',
                priority: 2
            },
            'critical': {
                name: 'Critical',
                icon: '🚨',
                color: '#F44336',
                priority: 3
            },
            'panic': {
                name: 'Panic',
                icon: '🚨',
                color: '#B71C1C',
                priority: 4
            }
        };
    }

    /**
     * Process new alert - main entry point
     */
    async processAlert(alert) {
        try {
            // Validate alert structure
            const validatedAlert = this.validateAlert(alert);
            if (!validatedAlert.isValid) {
                console.error('Invalid alert structure:', validatedAlert.errors);
                return false;
            }

            // Enrich alert with metadata
            const enrichedAlert = await this.enrichAlert(alert);

            // Store in history and active alerts
            this.storeAlert(enrichedAlert);

            // Update metrics
            this.updateAlertMetrics(enrichedAlert);

            // Process based on alert level
            await this.processAlertByLevel(enrichedAlert);

            // Emit event for other system components
            this.emit('alertProcessed', enrichedAlert);

            return true;
        } catch (error) {
            console.error('Error processing alert:', error);
            return false;
        }
    }

    /**
     * Validate alert structure and required fields
     */
    validateAlert(alert) {
        const errors = [];
        const requiredFields = ['level', 'message', 'testId', 'timestamp', 'value', 'unit'];

        requiredFields.forEach(field => {
            if (!alert[field]) {
                errors.push(`Missing required field: ${field}`);
            }
        });

        if (!['info', 'warning', 'critical', 'panic'].includes(alert.level)) {
            errors.push('Invalid alert level');
        }

        return {
            isValid: errors.length === 0,
            errors: errors
        };
    }

    /**
     * Enrich alert with additional metadata and context
     */
    async enrichAlert(alert) {
        const enriched = {
            ...alert,
            alertId: this.generateAlertId(),
            processedAt: new Date(),
            status: 'active',
            acknowledged: false,
            acknowledgedBy: null,
            acknowledgedAt: null,
            escalated: false,
            escalationLevel: 0,
            responseTime: null,
            notificationsSent: [],
            actions: [],
            priority: this.alertLevels[alert.level].priority
        };

        // Add clinical context if available
        if (alert.testId && alert.patientId) {
            enriched.clinicalContext = await this.getClinicalContext(alert.patientId, alert.testId);
        }

        // Add historical context
        enriched.historicalContext = await this.getHistoricalContext(alert.testId, alert.patientId);

        return enriched;
    }

    /**
     * Store alert in history and active alerts
     */
    storeAlert(alert) {
        // Add to history
        this.alertHistory.push(alert);

        // Add to active alerts if not info level
        if (alert.level !== 'info') {
            this.activeAlerts.set(alert.alertId, alert);
        }

        // Cleanup old alerts (keep last 10000)
        if (this.alertHistory.length > 10000) {
            this.alertHistory = this.alertHistory.slice(-10000);
        }
    }

    /**
     * Update alert metrics
     */
    updateAlertMetrics(alert) {
        this.alertMetrics.totalAlerts++;
        this.alertMetrics.alertCounts[alert.level]++;
    }

    /**
     * Process alert based on its level using escalation policies
     */
    async processAlertByLevel(alert) {
        const policy = this.escalationPolicies.get(alert.level);
        if (!policy) {
            console.error(`No escalation policy found for level: ${alert.level}`);
            return;
        }

        // Apply notification delay
        if (policy.notificationDelay > 0) {
            setTimeout(() => {
                this.executeAlertPolicy(alert, policy);
            }, policy.notificationDelay);
        } else {
            await this.executeAlertPolicy(alert, policy);
        }
    }

    /**
     * Execute alert policy actions and notifications
     */
    async executeAlertPolicy(alert, policy) {
        try {
            // Send notifications through configured channels
            await this.sendNotifications(alert, policy);

            // Execute policy actions
            await this.executeActions(alert, policy.actions);

            // Set up escalation timer if required
            if (policy.escalationRequired && !policy.immediateEscalation) {
                this.scheduleEscalation(alert, policy);
            }

            // Handle immediate escalation for panic alerts
            if (policy.immediateEscalation) {
                await this.immediateEscalation(alert, policy);
            }

            // Update alert status
            this.updateAlertStatus(alert.alertId, 'notified');

        } catch (error) {
            console.error('Error executing alert policy:', error);
            await this.handlePolicyExecutionError(alert, policy, error);
        }
    }

    /**
     * Send notifications through configured channels
     */
    async sendNotifications(alert, policy) {
        const notificationPromises = [];

        for (const channelName of policy.channels) {
            const channel = this.notificationChannels.get(channelName);
            if (channel && channel.enabled) {
                const promise = this.sendNotificationThroughChannel(alert, channel, policy.recipients);
                notificationPromises.push(promise);
            }
        }

        try {
            const results = await Promise.allSettled(notificationPromises);
            this.processNotificationResults(alert, results);
        } catch (error) {
            console.error('Error sending notifications:', error);
        }
    }

    /**
     * Send notification through specific channel
     */
    async sendNotificationThroughChannel(alert, channel, recipients) {
        try {
            const channelRecipients = this.getChannelRecipients(recipients, channel.type);
            const result = await channel.send(alert, channelRecipients);
            
            // Log successful notification
            alert.notificationsSent.push({
                channel: channel.type,
                recipients: channelRecipients,
                sentAt: new Date(),
                success: true,
                result: result
            });

            return result;
        } catch (error) {
            // Log failed notification
            alert.notificationsSent.push({
                channel: channel.type,
                sentAt: new Date(),
                success: false,
                error: error.message
            });
            
            console.error(`Failed to send ${channel.type} notification:`, error);
            throw error;
        }
    }

    // =====================================================================
    // NOTIFICATION CHANNEL IMPLEMENTATIONS
    // =====================================================================

    /**
     * Send email alert
     */
    async sendEmailAlert(alert, recipients) {
        const emailData = {
            from: this.notificationChannels.get('email').config.from,
            to: recipients.join(','),
            subject: this.generateEmailSubject(alert),
            html: this.generateEmailBody(alert),
            priority: this.getEmailPriority(alert.level)
        };

        // In production, integrate with actual email service (SMTP, SendGrid, etc.)
        console.log('📧 Email Alert Sent:', {
            to: recipients,
            subject: emailData.subject,
            level: alert.level,
            testId: alert.testId
        });

        return { success: true, messageId: `email_${Date.now()}` };
    }

    /**
     * Send SMS alert
     */
    async sendSMSAlert(alert, recipients) {
        const message = this.generateSMSMessage(alert);
        
        // In production, integrate with SMS gateway (Twilio, etc.)
        console.log('📱 SMS Alert Sent:', {
            to: recipients,
            message: message,
            level: alert.level
        });

        return { success: true, messageId: `sms_${Date.now()}` };
    }

    /**
     * Send pager alert
     */
    async sendPagerAlert(alert, recipients) {
        const pagerMessage = this.generatePagerMessage(alert);
        
        // In production, integrate with paging system
        console.log('📟 Pager Alert Sent:', {
            to: recipients,
            message: pagerMessage,
            urgentCode: alert.level === 'panic' ? '999' : '911'
        });

        return { success: true, messageId: `pager_${Date.now()}` };
    }

    /**
     * Send EMR integration alert
     */
    async sendEMRAlert(alert, recipients) {
        const emrFlag = {
            patientId: alert.patientId,
            alertLevel: alert.level,
            testId: alert.testId,
            message: alert.message,
            value: alert.value,
            timestamp: alert.timestamp,
            autoFlag: alert.level === 'critical' || alert.level === 'panic'
        };

        // In production, integrate with EMR system API
        console.log('🏥 EMR Alert Created:', {
            patientId: alert.patientId,
            flag: emrFlag,
            autoFlag: emrFlag.autoFlag
        });

        return { success: true, flagId: `emr_${Date.now()}` };
    }

    /**
     * Send Slack alert
     */
    async sendSlackAlert(alert, recipients) {
        const slackMessage = this.generateSlackMessage(alert);
        
        // In production, send to Slack webhook
        console.log('💬 Slack Alert Sent:', {
            channels: recipients,
            message: slackMessage
        });

        return { success: true, messageId: `slack_${Date.now()}` };
    }

    // =====================================================================
    // ESCALATION MANAGEMENT
    // =====================================================================

    /**
     * Schedule escalation for alerts that require it
     */
    scheduleEscalation(alert, policy) {
        const escalationTimeout = setTimeout(async () => {
            if (this.activeAlerts.has(alert.alertId) && !alert.acknowledged) {
                await this.escalateAlert(alert, policy);
            }
        }, policy.escalationTime);

        alert.escalationTimeout = escalationTimeout;
    }

    /**
     * Escalate unacknowledged alert
     */
    async escalateAlert(alert, policy) {
        try {
            alert.escalated = true;
            alert.escalationLevel++;
            this.alertMetrics.escalationCounts[alert.level]++;

            console.log(`🔺 Escalating ${alert.level} alert: ${alert.alertId}`);

            // Send escalation notifications
            await this.sendEscalationNotifications(alert, policy);

            // Log escalation
            alert.actions.push({
                action: 'escalated',
                timestamp: new Date(),
                escalationLevel: alert.escalationLevel,
                reason: 'no_acknowledgment_within_timeframe'
            });

            this.emit('alertEscalated', alert);
        } catch (error) {
            console.error('Error escalating alert:', error);
        }
    }

    /**
     * Handle immediate escalation for panic alerts
     */
    async immediateEscalation(alert, policy) {
        alert.escalated = true;
        alert.escalationLevel = 1;
        
        console.log(`⚡ Immediate escalation for panic alert: ${alert.alertId}`);

        // Send to emergency recipients immediately
        const emergencyChannels = ['sms', 'pager'];
        for (const channelName of emergencyChannels) {
            const channel = this.notificationChannels.get(channelName);
            if (channel && channel.enabled) {
                await this.sendNotificationThroughChannel(
                    alert, 
                    channel, 
                    { emergency: policy.recipients.emergency }
                );
            }
        }

        // Activate emergency protocol
        await this.activateEmergencyProtocol(alert);
    }

    /**
     * Send escalation notifications
     */
    async sendEscalationNotifications(alert, policy) {
        const escalationRecipients = policy.recipients.escalation || [];
        
        for (const channelName of policy.channels) {
            const channel = this.notificationChannels.get(channelName);
            if (channel && channel.enabled) {
                await this.sendNotificationThroughChannel(
                    alert,
                    channel,
                    { escalation: escalationRecipients }
                );
            }
        }
    }

    /**
     * Activate emergency protocol for panic alerts
     */
    async activateEmergencyProtocol(alert) {
        console.log('🚨 EMERGENCY PROTOCOL ACTIVATED 🚨');
        console.log(`Alert ID: ${alert.alertId}`);
        console.log(`Test: ${alert.testId} = ${alert.value} ${alert.unit}`);
        console.log(`Patient: ${alert.patientId}`);
        console.log(`Time: ${alert.timestamp}`);
        
        // In production, this would:
        // - Trigger hospital-wide emergency alert systems
        // - Notify emergency response teams
        // - Create incident in hospital incident management system
        // - Alert administration and risk management
        // - Document in regulatory compliance systems
        
        alert.actions.push({
            action: 'emergency_protocol_activated',
            timestamp: new Date(),
            details: 'Full emergency response protocol initiated'
        });
    }

    // =====================================================================
    // MESSAGE GENERATION
    // =====================================================================

    /**
     * Generate email subject line
     */
    generateEmailSubject(alert) {
        const levelEmoji = this.alertLevels[alert.level].icon;
        const levelName = this.alertLevels[alert.level].name.toUpperCase();
        
        return `${levelEmoji} ${levelName} LAB ALERT - ${alert.testId} | Patient: ${alert.patientId}`;
    }

    /**
     * Generate email body
     */
    generateEmailBody(alert) {
        return `
        <html>
        <body style="font-family: Arial, sans-serif;">
            <div style="border-left: 4px solid ${this.alertLevels[alert.level].color}; padding: 20px;">
                <h2 style="color: ${this.alertLevels[alert.level].color};">
                    ${this.alertLevels[alert.level].icon} ${this.alertLevels[alert.level].name} Alert
                </h2>
                
                <table style="border-collapse: collapse; width: 100%;">
                    <tr><td><strong>Test:</strong></td><td>${alert.testId}</td></tr>
                    <tr><td><strong>Value:</strong></td><td>${alert.value} ${alert.unit}</td></tr>
                    <tr><td><strong>Patient:</strong></td><td>${alert.patientId}</td></tr>
                    <tr><td><strong>Time:</strong></td><td>${alert.timestamp}</td></tr>
                    <tr><td><strong>Message:</strong></td><td>${alert.message}</td></tr>
                </table>
                
                <div style="margin-top: 20px; padding: 10px; background-color: #f5f5f5;">
                    <strong>Required Action:</strong> 
                    ${this.getRequiredAction(alert.level)}
                </div>
                
                <div style="margin-top: 10px; font-size: 12px; color: #666;">
                    Alert ID: ${alert.alertId} | Generated at: ${alert.processedAt}
                </div>
            </div>
        </body>
        </html>`;
    }

    /**
     * Generate SMS message
     */
    generateSMSMessage(alert) {
        const levelEmoji = this.alertLevels[alert.level].icon;
        return `${levelEmoji} LAB ALERT: ${alert.testId}=${alert.value}${alert.unit} Patient:${alert.patientId} ${alert.message.substring(0, 50)}...`;
    }

    /**
     * Generate pager message
     */
    generatePagerMessage(alert) {
        const urgentCode = alert.level === 'panic' ? '999' : '911';
        return `${urgentCode} LAB: ${alert.testId}=${alert.value}${alert.unit} PT:${alert.patientId}`;
    }

    /**
     * Generate Slack message
     */
    generateSlackMessage(alert) {
        const levelEmoji = this.alertLevels[alert.level].icon;
        const color = this.alertLevels[alert.level].color;
        
        return {
            attachments: [{
                color: color,
                title: `${levelEmoji} ${this.alertLevels[alert.level].name} Laboratory Alert`,
                fields: [
                    { title: 'Test', value: alert.testId, short: true },
                    { title: 'Value', value: `${alert.value} ${alert.unit}`, short: true },
                    { title: 'Patient', value: alert.patientId, short: true },
                    { title: 'Time', value: alert.timestamp, short: true },
                    { title: 'Message', value: alert.message, short: false }
                ],
                footer: `Alert ID: ${alert.alertId}`,
                ts: Math.floor(alert.processedAt.getTime() / 1000)
            }]
        };
    }

    // =====================================================================
    // UTILITY METHODS
    // =====================================================================

    /**
     * Generate unique alert ID
     */
    generateAlertId() {
        const timestamp = Date.now();
        const random = Math.random().toString(36).substring(2, 8);
        return `ALERT_${timestamp}_${random}`;
    }

    /**
     * Get email priority based on alert level
     */
    getEmailPriority(level) {
        const priorities = {
            info: 'normal',
            warning: 'normal',
            critical: 'high',
            panic: 'urgent'
        };
        return priorities[level] || 'normal';
    }

    /**
     * Get required action text based on alert level
     */
    getRequiredAction(level) {
        const actions = {
            info: 'Review during routine quality control activities.',
            warning: 'Review and investigate within 4 hours. Consider repeat testing if indicated.',
            critical: 'IMMEDIATE REVIEW REQUIRED. Contact attending physician and correlate with clinical presentation. Response required within 30 minutes.',
            panic: 'EMERGENCY RESPONSE REQUIRED. Contact patient immediately. Ensure appropriate clinical intervention. Response required within 5 minutes.'
        };
        return actions[level] || 'Review as appropriate.';
    }

    /**
     * Get recipients for specific channel type
     */
    getChannelRecipients(recipients, channelType) {
        // Return appropriate recipients based on channel type
        if (channelType === 'sms' && recipients.emergency) {
            return recipients.emergency;
        }
        return recipients.primary || [];
    }

    /**
     * Start background alert processor
     */
    startAlertProcessor() {
        setInterval(() => {
            this.processQueuedAlerts();
        }, 1000); // Check every second
    }

    /**
     * Start escalation monitor
     */
    startEscalationMonitor() {
        setInterval(() => {
            this.monitorEscalations();
        }, 30000); // Check every 30 seconds
    }

    /**
     * Process queued alerts (placeholder for queue implementation)
     */
    processQueuedAlerts() {
        // Implementation would process queued alerts from database or message queue
    }

    /**
     * Monitor escalations
     */
    monitorEscalations() {
        // Check for alerts that need escalation
        // Implementation would check database for unacknowledged alerts
    }

    /**
     * Update alert status
     */
    updateAlertStatus(alertId, status) {
        const alert = this.activeAlerts.get(alertId);
        if (alert) {
            alert.status = status;
            alert.lastUpdated = new Date();
        }
    }

    /**
     * Acknowledge alert
     */
    async acknowledgeAlert(alertId, acknowledgedBy) {
        const alert = this.activeAlerts.get(alertId);
        if (alert) {
            alert.acknowledged = true;
            alert.acknowledgedBy = acknowledgedBy;
            alert.acknowledgedAt = new Date();
            alert.responseTime = alert.acknowledgedAt.getTime() - alert.processedAt.getTime();
            
            // Cancel escalation timeout
            if (alert.escalationTimeout) {
                clearTimeout(alert.escalationTimeout);
            }
            
            // Update response time stats
            this.alertMetrics.responseTimeStats[alert.level].push(alert.responseTime);
            
            this.emit('alertAcknowledged', alert);
            return true;
        }
        return false;
    }

    /**
     * Get alert statistics
     */
    getAlertStatistics(timeframe = '24h') {
        const now = new Date();
        const cutoffTime = this.getTimeframeCutoff(now, timeframe);
        
        const recentAlerts = this.alertHistory.filter(a => a.processedAt >= cutoffTime);
        
        return {
            timeframe: timeframe,
            totalAlerts: recentAlerts.length,
            alertBreakdown: {
                info: recentAlerts.filter(a => a.level === 'info').length,
                warning: recentAlerts.filter(a => a.level === 'warning').length,
                critical: recentAlerts.filter(a => a.level === 'critical').length,
                panic: recentAlerts.filter(a => a.level === 'panic').length
            },
            responseTimeStats: this.calculateResponseTimeStats(recentAlerts),
            escalationRate: this.calculateEscalationRate(recentAlerts),
            acknowledgedRate: this.calculateAcknowledgedRate(recentAlerts)
        };
    }

    /**
     * Calculate response time statistics
     */
    calculateResponseTimeStats(alerts) {
        const acknowledgedAlerts = alerts.filter(a => a.acknowledged && a.responseTime);
        
        if (acknowledgedAlerts.length === 0) {
            return { count: 0 };
        }
        
        const responseTimes = acknowledgedAlerts.map(a => a.responseTime);
        const sorted = responseTimes.sort((a, b) => a - b);
        
        return {
            count: acknowledgedAlerts.length,
            average: Math.round(responseTimes.reduce((sum, rt) => sum + rt, 0) / responseTimes.length),
            median: sorted[Math.floor(sorted.length / 2)],
            p95: sorted[Math.floor(sorted.length * 0.95)],
            p99: sorted[Math.floor(sorted.length * 0.99)]
        };
    }

    /**
     * Calculate escalation rate
     */
    calculateEscalationRate(alerts) {
        const escalatableAlerts = alerts.filter(a => a.level !== 'info');
        const escalatedAlerts = escalatableAlerts.filter(a => a.escalated);
        
        return {
            total: escalatableAlerts.length,
            escalated: escalatedAlerts.length,
            rate: escalatableAlerts.length > 0 ? 
                (escalatedAlerts.length / escalatableAlerts.length * 100).toFixed(1) + '%' : '0%'
        };
    }

    /**
     * Calculate acknowledged rate
     */
    calculateAcknowledgedRate(alerts) {
        const nonInfoAlerts = alerts.filter(a => a.level !== 'info');
        const acknowledgedAlerts = nonInfoAlerts.filter(a => a.acknowledged);
        
        return {
            total: nonInfoAlerts.length,
            acknowledged: acknowledgedAlerts.length,
            rate: nonInfoAlerts.length > 0 ? 
                (acknowledgedAlerts.length / nonInfoAlerts.length * 100).toFixed(1) + '%' : '0%'
        };
    }

    getTimeframeCutoff(now, timeframe) {
        const timeframes = {
            '1h': 60 * 60 * 1000,
            '24h': 24 * 60 * 60 * 1000,
            '7d': 7 * 24 * 60 * 60 * 1000,
            '30d': 30 * 24 * 60 * 60 * 1000
        };
        
        return new Date(now.getTime() - (timeframes[timeframe] || timeframes['24h']));
    }

    // Additional helper methods
    async getClinicalContext(patientId, testId) {
        // In production, fetch from EMR/HIS
        return { patientId, testId, context: 'clinical_context_placeholder' };
    }

    async getHistoricalContext(testId, patientId) {
        // In production, fetch historical results
        return { testId, patientId, context: 'historical_context_placeholder' };
    }

    processNotificationResults(alert, results) {
        results.forEach((result, index) => {
            if (result.status === 'rejected') {
                console.error(`Notification failed:`, result.reason);
            }
        });
    }

    async executeActions(alert, actions) {
        for (const action of actions) {
            try {
                await this.executeAction(alert, action);
            } catch (error) {
                console.error(`Failed to execute action ${action}:`, error);
            }
        }
    }

    async executeAction(alert, action) {
        // Implement specific actions based on action type
        console.log(`Executing action: ${action} for alert ${alert.alertId}`);
    }

    async handlePolicyExecutionError(alert, policy, error) {
        console.error(`Policy execution failed for alert ${alert.alertId}:`, error);
        // Implement fallback notification mechanisms
    }
}

module.exports = { AlertNotificationSystem };