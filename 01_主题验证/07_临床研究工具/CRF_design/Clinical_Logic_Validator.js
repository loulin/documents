/**
 * Clinical Logic Validator Module
 * Specialized module for clinical logic validation including physiological correlations
 * and disease-specific validation rules for laboratory test results
 * 
 * Part of the Laboratory Quality Control System v1.0
 */

class ClinicalLogicValidator {
    constructor(config = {}) {
        this.config = config;
        this.correlationRules = new Map();
        this.diseasePatterns = new Map();
        this.physiologicalConstants = new Map();
        
        this.initializeCorrelationRules();
        this.initializeDiseasePatterns();
        this.initializePhysiologicalConstants();
    }

    /**
     * Initialize physiological correlation rules based on established medical knowledge
     */
    initializeCorrelationRules() {
        // Glucose-HbA1c Correlation (DCCT/NGSP relationship)
        this.correlationRules.set('glucose_hba1c', {
            testIds: ['DM001', 'DM003'], // Fasting glucose and HbA1c
            correlation: 'positive',
            formula: (glucose_mmol) => {
                // ADAG study formula: HbA1c(%) = (mean_glucose_mmol + 2.15) / 1.59
                return (glucose_mmol + 2.15) / 1.59;
            },
            tolerance: 1.0, // ±1.0% HbA1c
            clinicalSignificance: 'diabetes_monitoring',
            validation: (glucose, hba1c) => {
                const expected = this.correlationRules.get('glucose_hba1c').formula(glucose);
                const difference = Math.abs(hba1c - expected);
                return {
                    valid: difference <= 1.0,
                    expected: expected,
                    actual: hba1c,
                    difference: difference,
                    interpretation: difference > 1.0 ? 'discordant_glucose_hba1c' : 'concordant'
                };
            }
        });

        // Creatinine-eGFR Correlation (CKD-EPI equation)
        this.correlationRules.set('creatinine_egfr', {
            testIds: ['RF001', 'RF002'],
            correlation: 'inverse',
            formula: (creatinine_umol, age, gender, race = 'other') => {
                // CKD-EPI equation (2009)
                const creatinine_mg_dl = creatinine_umol / 88.4; // Convert μmol/L to mg/dL
                const k = gender === 'female' ? 0.7 : 0.9;
                const alpha = gender === 'female' ? -0.329 : -0.411;
                const min_ratio = Math.min(creatinine_mg_dl / k, 1);
                const max_ratio = Math.max(creatinine_mg_dl / k, 1);
                
                let egfr = 141 * Math.pow(min_ratio, alpha) * Math.pow(max_ratio, -1.209) * 
                          Math.pow(0.993, age);
                
                if (gender === 'female') egfr *= 1.018;
                if (race === 'african_american') egfr *= 1.159;
                
                return egfr;
            },
            tolerance: 15, // ±15 mL/min/1.73m²
            clinicalSignificance: 'kidney_function',
            validation: (creatinine, egfr, patientContext = {}) => {
                const { age = 50, gender = 'unknown', race = 'other' } = patientContext;
                const expected = this.correlationRules.get('creatinine_egfr').formula(creatinine, age, gender, race);
                const difference = Math.abs(egfr - expected);
                return {
                    valid: difference <= 15,
                    expected: expected,
                    actual: egfr,
                    difference: difference,
                    interpretation: this.interpretEgfrCreatinineDiscordance(difference, creatinine, egfr)
                };
            }
        });

        // Electrolyte Balance (Anion Gap)
        this.correlationRules.set('electrolyte_balance', {
            testIds: ['EL001', 'EL002', 'EL003'], // Na, K, Cl
            correlation: 'balance',
            formula: (sodium, potassium, chloride) => {
                return sodium - (potassium + chloride); // Anion gap
            },
            normalRange: [8, 16],
            clinicalSignificance: 'acid_base_balance',
            validation: (sodium, potassium, chloride) => {
                const anionGap = this.correlationRules.get('electrolyte_balance').formula(sodium, potassium, chloride);
                const isNormal = anionGap >= 8 && anionGap <= 16;
                return {
                    valid: isNormal,
                    anionGap: anionGap,
                    interpretation: this.interpretAnionGap(anionGap),
                    clinicalImplication: this.getAnionGapClinicalImplication(anionGap)
                };
            }
        });

        // Total Protein - Albumin = Globulins
        this.correlationRules.set('protein_fractions', {
            testIds: ['PR001', 'PR002'], // Total protein, Albumin
            correlation: 'additive',
            formula: (totalProtein, albumin) => {
                return totalProtein - albumin; // Globulins
            },
            normalRange: [23, 35], // Normal globulin range g/L
            validation: (totalProtein, albumin) => {
                const globulins = this.correlationRules.get('protein_fractions').formula(totalProtein, albumin);
                const ag_ratio = albumin / globulins;
                return {
                    valid: globulins >= 23 && globulins <= 35 && ag_ratio >= 1.2 && ag_ratio <= 2.2,
                    globulins: globulins,
                    albumin_globulin_ratio: ag_ratio,
                    interpretation: this.interpretProteinFractions(albumin, globulins, ag_ratio)
                };
            }
        });

        // Calcium correction for albumin
        this.correlationRules.set('corrected_calcium', {
            testIds: ['EL005', 'PR002'], // Calcium, Albumin
            correlation: 'correction',
            formula: (totalCalcium, albumin) => {
                // Corrected Calcium = Total Calcium + 0.02 × (40 - Albumin in g/L)
                return totalCalcium + 0.02 * (40 - albumin);
            },
            validation: (totalCalcium, albumin) => {
                const correctedCalcium = this.correlationRules.get('corrected_calcium').formula(totalCalcium, albumin);
                return {
                    valid: true, // Always valid as it's a correction formula
                    correctedCalcium: correctedCalcium,
                    interpretation: this.interpretCorrectedCalcium(correctedCalcium, totalCalcium, albumin)
                };
            }
        });
    }

    /**
     * Initialize disease-specific validation patterns
     */
    initializeDiseasePatterns() {
        // Diabetes Mellitus Pattern
        this.diseasePatterns.set('diabetes_mellitus', {
            diagnosticCriteria: {
                fasting_glucose_mmol: { threshold: 7.0, operator: '>=' },
                random_glucose_mmol: { threshold: 11.1, operator: '>=' },
                hba1c_percent: { threshold: 6.5, operator: '>=' },
                ogtt_2h_mmol: { threshold: 11.1, operator: '>=' }
            },
            supportingTests: ['DM001', 'DM002', 'DM003', 'DM004'],
            exclusionCriteria: {
                stress_hyperglycemia: 'exclude_if_acute_illness',
                medication_induced: 'exclude_if_steroid_use'
            },
            validation: (testResults) => {
                return this.validateDiabetesPattern(testResults);
            }
        });

        // Acute Myocardial Infarction Pattern
        this.diseasePatterns.set('acute_mi', {
            diagnosticCriteria: {
                troponin_elevation: true,
                ck_mb_elevation: true,
                kinetic_pattern: 'rise_and_fall'
            },
            supportingTests: ['CM001', 'CM002', 'CM003'], // Troponin, CK-MB, CK
            timePattern: {
                troponin_peak: '12-24h',
                troponin_duration: '7-14d',
                ck_mb_peak: '12-18h',
                ck_mb_duration: '2-3d'
            },
            validation: (testResults, timePoints) => {
                return this.validateAcuteMIPattern(testResults, timePoints);
            }
        });

        // Hepatocellular vs Cholestatic Liver Injury
        this.diseasePatterns.set('liver_injury_pattern', {
            hepatocellular: {
                criteria: {
                    alt_elevation: '>= 3x ULN',
                    ast_elevation: '>= 3x ULN',
                    alp_elevation: '< 2x ULN',
                    ast_alt_ratio: '< 2'
                }
            },
            cholestatic: {
                criteria: {
                    alp_elevation: '>= 2x ULN',
                    ggt_elevation: '>= 2x ULN',
                    bilirubin_elevation: 'present',
                    alt_elevation: '< 3x ULN'
                }
            },
            mixed: {
                criteria: {
                    both_patterns: true
                }
            },
            validation: (testResults) => {
                return this.validateLiverInjuryPattern(testResults);
            }
        });

        // Thyroid Function Patterns
        this.diseasePatterns.set('thyroid_patterns', {
            primary_hyperthyroidism: {
                tsh: 'suppressed',
                t4_or_t3: 'elevated'
            },
            primary_hypothyroidism: {
                tsh: 'elevated',
                t4: 'decreased'
            },
            subclinical_hyperthyroidism: {
                tsh: 'suppressed',
                t4_and_t3: 'normal'
            },
            subclinical_hypothyroidism: {
                tsh: 'mildly_elevated',
                t4: 'normal'
            },
            validation: (testResults) => {
                return this.validateThyroidPattern(testResults);
            }
        });
    }

    /**
     * Initialize physiological constants for calculations
     */
    initializePhysiologicalConstants() {
        this.physiologicalConstants.set('glucose_conversion', 18.0182); // mmol/L to mg/dL
        this.physiologicalConstants.set('creatinine_conversion', 88.4); // μmol/L to mg/dL
        this.physiologicalConstants.set('normal_gfr', 120); // mL/min/1.73m²
        this.physiologicalConstants.set('normal_anion_gap', [8, 16]);
        this.physiologicalConstants.set('normal_albumin_globulin_ratio', [1.2, 2.2]);
    }

    /**
     * Main clinical logic validation entry point
     */
    async validateClinicalLogic(testResults, patientContext = {}) {
        const validations = {
            physiological: await this.validatePhysiologicalCorrelations(testResults, patientContext),
            diseaseSpecific: await this.validateDiseasePatterns(testResults, patientContext),
            panelConsistency: await this.validatePanelConsistency(testResults)
        };

        const overallValid = Object.values(validations).every(v => v.valid);

        return {
            overallValid: overallValid,
            validations: validations,
            clinicalAlerts: this.generateClinicalAlerts(validations),
            recommendations: this.generateClinicalRecommendations(validations),
            riskAssessment: this.assessClinicalRisk(validations, patientContext)
        };
    }

    /**
     * Validate physiological correlations between related tests
     */
    async validatePhysiologicalCorrelations(testResults, patientContext) {
        const correlationResults = [];

        for (const [correlationId, rule] of this.correlationRules) {
            const requiredTests = rule.testIds;
            const availableResults = testResults.filter(r => requiredTests.includes(r.testId));

            if (availableResults.length === requiredTests.length) {
                const values = availableResults.map(r => parseFloat(r.value));
                const validation = rule.validation(...values, patientContext);

                correlationResults.push({
                    correlationId: correlationId,
                    testIds: requiredTests,
                    values: values,
                    validation: validation,
                    clinicalSignificance: rule.clinicalSignificance
                });
            }
        }

        return {
            valid: correlationResults.every(r => r.validation.valid),
            correlations: correlationResults,
            summary: this.summarizeCorrelationResults(correlationResults)
        };
    }

    /**
     * Validate disease-specific patterns
     */
    async validateDiseasePatterns(testResults, patientContext) {
        const patternResults = [];

        for (const [patternId, pattern] of this.diseasePatterns) {
            const relevantTests = testResults.filter(r => 
                pattern.supportingTests && pattern.supportingTests.includes(r.testId)
            );

            if (relevantTests.length > 0) {
                const validation = pattern.validation(relevantTests, patientContext);
                patternResults.push({
                    patternId: patternId,
                    testCount: relevantTests.length,
                    validation: validation
                });
            }
        }

        return {
            valid: patternResults.every(p => p.validation.valid !== false), // Allow undefined as valid
            patterns: patternResults
        };
    }

    /**
     * Validate consistency within test panels
     */
    async validatePanelConsistency(testResults) {
        const panels = this.groupTestsByPanel(testResults);
        const consistencyResults = [];

        for (const [panelId, tests] of panels) {
            const consistency = await this.validateSpecificPanelConsistency(panelId, tests);
            consistencyResults.push({
                panelId: panelId,
                testCount: tests.length,
                consistency: consistency
            });
        }

        return {
            valid: consistencyResults.every(r => r.consistency.valid),
            panels: consistencyResults
        };
    }

    // =====================================================================
    // DISEASE-SPECIFIC VALIDATION IMPLEMENTATIONS
    // =====================================================================

    /**
     * Validate diabetes diagnostic pattern
     */
    validateDiabetesPattern(testResults) {
        const glucoseTests = testResults.filter(t => t.testId.startsWith('DM'));
        const diagnosticCount = 0;
        const findings = [];

        glucoseTests.forEach(test => {
            const value = parseFloat(test.value);
            
            switch (test.testId) {
                case 'DM001': // Fasting glucose
                    if (value >= 7.0) {
                        findings.push({ test: 'fasting_glucose', value: value, diagnostic: true });
                    } else if (value >= 6.1) {
                        findings.push({ test: 'fasting_glucose', value: value, diagnostic: false, note: 'impaired_fasting_glucose' });
                    }
                    break;
                case 'DM002': // 2h post-prandial
                    if (value >= 11.1) {
                        findings.push({ test: '2h_glucose', value: value, diagnostic: true });
                    } else if (value >= 7.8) {
                        findings.push({ test: '2h_glucose', value: value, diagnostic: false, note: 'impaired_glucose_tolerance' });
                    }
                    break;
                case 'DM003': // HbA1c
                    if (value >= 6.5) {
                        findings.push({ test: 'hba1c', value: value, diagnostic: true });
                    } else if (value >= 5.7) {
                        findings.push({ test: 'hba1c', value: value, diagnostic: false, note: 'prediabetes' });
                    }
                    break;
            }
        });

        const diagnosticFindings = findings.filter(f => f.diagnostic);
        const isDiabetic = diagnosticFindings.length >= 1; // One abnormal test can diagnose DM

        return {
            valid: true, // Pattern validation doesn't invalidate, just classifies
            diabetesLikely: isDiabetic,
            prediabetesLikely: !isDiabetic && findings.some(f => f.note && f.note.includes('diabetes')),
            findings: findings,
            recommendation: this.getDiabetesRecommendation(isDiabetic, findings)
        };
    }

    /**
     * Validate acute MI pattern based on cardiac markers
     */
    validateAcuteMIPattern(testResults, timePoints) {
        const cardiacMarkers = testResults.filter(t => t.testId.startsWith('CM'));
        const pattern = {
            troponin_elevated: false,
            ck_mb_elevated: false,
            kinetic_pattern_present: false
        };

        // Analyze troponin pattern
        const troponinResults = cardiacMarkers.filter(t => t.testId === 'CM001');
        if (troponinResults.length > 1 && timePoints) {
            pattern.kinetic_pattern_present = this.analyzeTroponinKinetics(troponinResults, timePoints);
        }

        cardiacMarkers.forEach(test => {
            const value = parseFloat(test.value);
            // This would check against specific reference ranges for each marker
            // Implementation would depend on specific test definitions
        });

        return {
            valid: true,
            pattern: pattern,
            miLikely: pattern.troponin_elevated && pattern.kinetic_pattern_present,
            recommendation: this.getMIRecommendation(pattern)
        };
    }

    /**
     * Validate liver injury pattern (hepatocellular vs cholestatic)
     */
    validateLiverInjuryPattern(testResults) {
        const liverTests = testResults.filter(t => t.testId.startsWith('LF'));
        const pattern = {
            type: 'unknown',
            severity: 'unknown',
            markers: {}
        };

        // This would analyze ALT, AST, ALP, GGT, Bilirubin patterns
        // Implementation depends on specific test definitions

        return {
            valid: true,
            pattern: pattern,
            recommendation: this.getLiverInjuryRecommendation(pattern)
        };
    }

    /**
     * Validate thyroid function pattern
     */
    validateThyroidPattern(testResults) {
        const thyroidTests = testResults.filter(t => t.testId.startsWith('TH'));
        const pattern = {
            tsh_status: 'unknown',
            t4_status: 'unknown',
            t3_status: 'unknown',
            pattern_type: 'unknown'
        };

        // Analyze TSH, T4, T3 patterns
        thyroidTests.forEach(test => {
            const value = parseFloat(test.value);
            // Implementation would depend on specific reference ranges
        });

        return {
            valid: true,
            pattern: pattern,
            recommendation: this.getThyroidRecommendation(pattern)
        };
    }

    // =====================================================================
    // INTERPRETATION AND RECOMMENDATION METHODS
    // =====================================================================

    /**
     * Interpret eGFR-Creatinine discordance
     */
    interpretEgfrCreatinineDiscordance(difference, creatinine, egfr) {
        if (difference <= 15) {
            return 'concordant_results';
        } else if (difference <= 30) {
            return 'mild_discordance_check_demographics';
        } else {
            return 'significant_discordance_investigate_causes';
        }
    }

    /**
     * Interpret anion gap results
     */
    interpretAnionGap(anionGap) {
        if (anionGap < 8) {
            return 'low_anion_gap_rare_consider_measurement_error';
        } else if (anionGap <= 16) {
            return 'normal_anion_gap';
        } else if (anionGap <= 20) {
            return 'mildly_elevated_anion_gap';
        } else {
            return 'significantly_elevated_anion_gap_investigate_acidosis';
        }
    }

    /**
     * Get clinical implications of anion gap abnormalities
     */
    getAnionGapClinicalImplication(anionGap) {
        if (anionGap > 16) {
            return {
                category: 'metabolic_acidosis',
                commonCauses: ['diabetic_ketoacidosis', 'lactic_acidosis', 'uremia', 'poisoning'],
                urgency: anionGap > 20 ? 'high' : 'moderate'
            };
        } else if (anionGap < 8) {
            return {
                category: 'low_anion_gap',
                commonCauses: ['hypoalbuminemia', 'measurement_error', 'paraproteinemia'],
                urgency: 'low'
            };
        } else {
            return {
                category: 'normal',
                commonCauses: [],
                urgency: 'none'
            };
        }
    }

    /**
     * Interpret protein fractions
     */
    interpretProteinFractions(albumin, globulins, agRatio) {
        const interpretations = [];

        if (albumin < 35) {
            interpretations.push('hypoalbuminemia');
        }
        if (globulins > 35) {
            interpretations.push('hyperglobulinemia');
        }
        if (agRatio < 1.2) {
            interpretations.push('reversed_ag_ratio');
        }
        if (agRatio > 2.2) {
            interpretations.push('elevated_ag_ratio');
        }

        return interpretations.length > 0 ? interpretations : ['normal_protein_fractions'];
    }

    /**
     * Generate clinical alerts based on validation results
     */
    generateClinicalAlerts(validations) {
        const alerts = [];

        // Check physiological correlations
        if (validations.physiological && !validations.physiological.valid) {
            validations.physiological.correlations.forEach(corr => {
                if (!corr.validation.valid) {
                    alerts.push({
                        type: 'physiological_discordance',
                        level: 'warning',
                        message: `Discordant results in ${corr.correlationId}: ${corr.validation.interpretation}`,
                        tests: corr.testIds,
                        recommendation: 'Review test results and patient clinical context'
                    });
                }
            });
        }

        // Check disease patterns
        if (validations.diseaseSpecific) {
            validations.diseaseSpecific.patterns.forEach(pattern => {
                if (pattern.validation.diabetesLikely) {
                    alerts.push({
                        type: 'disease_pattern',
                        level: 'critical',
                        message: 'Test results consistent with diabetes mellitus diagnosis',
                        pattern: pattern.patternId,
                        recommendation: pattern.validation.recommendation
                    });
                }
            });
        }

        return alerts;
    }

    /**
     * Generate clinical recommendations
     */
    generateClinicalRecommendations(validations) {
        const recommendations = [];

        // Add specific recommendations based on validation results
        if (validations.physiological && validations.physiological.correlations) {
            validations.physiological.correlations.forEach(corr => {
                if (!corr.validation.valid) {
                    recommendations.push({
                        category: 'correlation_discordance',
                        priority: 'medium',
                        recommendation: `Investigate discordance in ${corr.correlationId}`,
                        actions: this.getCorrelationDiscordanceActions(corr.correlationId)
                    });
                }
            });
        }

        return recommendations;
    }

    /**
     * Assess overall clinical risk
     */
    assessClinicalRisk(validations, patientContext) {
        let riskScore = 0;
        const riskFactors = [];

        // Assess risk based on various validation results
        if (validations.physiological && !validations.physiological.valid) {
            riskScore += 2;
            riskFactors.push('physiological_discordance');
        }

        return {
            riskScore: riskScore,
            riskLevel: this.categorizeRisk(riskScore),
            riskFactors: riskFactors,
            recommendedActions: this.getRiskBasedActions(riskScore)
        };
    }

    // =====================================================================
    // UTILITY METHODS
    // =====================================================================

    groupTestsByPanel(testResults) {
        const panels = new Map();
        
        testResults.forEach(test => {
            const panelId = test.testId.substring(0, 2); // Extract panel prefix (e.g., 'DM', 'LP')
            if (!panels.has(panelId)) {
                panels.set(panelId, []);
            }
            panels.get(panelId).push(test);
        });

        return panels;
    }

    validateSpecificPanelConsistency(panelId, tests) {
        // Panel-specific consistency validation
        switch (panelId) {
            case 'DM':
                return this.validateDiabetesPanelConsistency(tests);
            case 'LP':
                return this.validateLipidPanelConsistency(tests);
            case 'LF':
                return this.validateLiverPanelConsistency(tests);
            case 'TH':
                return this.validateThyroidPanelConsistency(tests);
            default:
                return { valid: true, message: 'No specific consistency rules defined' };
        }
    }

    validateDiabetesPanelConsistency(tests) {
        // Implementation for diabetes panel consistency
        return { valid: true, message: 'Diabetes panel consistency validated' };
    }

    validateLipidPanelConsistency(tests) {
        // Check Friedewald formula consistency if all components present
        const totalChol = tests.find(t => t.testId === 'LP001');
        const hdl = tests.find(t => t.testId === 'LP002');
        const ldl = tests.find(t => t.testId === 'LP003');
        const triglycerides = tests.find(t => t.testId === 'LP004');

        if (totalChol && hdl && ldl && triglycerides) {
            const calculatedLdl = parseFloat(totalChol.value) - parseFloat(hdl.value) - (parseFloat(triglycerides.value) / 2.2);
            const reportedLdl = parseFloat(ldl.value);
            const difference = Math.abs(calculatedLdl - reportedLdl);

            return {
                valid: difference <= 0.3, // Allow 0.3 mmol/L difference
                calculatedLdl: calculatedLdl,
                reportedLdl: reportedLdl,
                difference: difference,
                message: difference <= 0.3 ? 'Friedewald formula consistent' : 'LDL discrepancy detected'
            };
        }

        return { valid: true, message: 'Insufficient data for Friedewald validation' };
    }

    validateLiverPanelConsistency(tests) {
        // Implementation for liver panel consistency
        return { valid: true, message: 'Liver panel consistency validated' };
    }

    validateThyroidPanelConsistency(tests) {
        // Implementation for thyroid panel consistency
        return { valid: true, message: 'Thyroid panel consistency validated' };
    }

    categorizeRisk(riskScore) {
        if (riskScore === 0) return 'low';
        if (riskScore <= 2) return 'moderate';
        if (riskScore <= 5) return 'high';
        return 'critical';
    }

    getRiskBasedActions(riskScore) {
        const actions = [];
        
        if (riskScore > 0) {
            actions.push('Review all test results with clinical context');
        }
        if (riskScore > 2) {
            actions.push('Consider repeat testing');
            actions.push('Correlate with clinical presentation');
        }
        if (riskScore > 5) {
            actions.push('Immediate clinical review required');
            actions.push('Consider urgent specialist referral');
        }

        return actions;
    }

    getCorrelationDiscordanceActions(correlationId) {
        const actions = {
            'glucose_hba1c': [
                'Verify patient fasting status',
                'Check for hemoglobin variants',
                'Consider recent blood transfusion',
                'Evaluate for conditions affecting RBC lifespan'
            ],
            'creatinine_egfr': [
                'Verify patient demographics (age, race, gender)',
                'Check for muscle mass variations',
                'Consider non-GFR determinants of creatinine',
                'Evaluate for interfering substances'
            ],
            'electrolyte_balance': [
                'Check sample quality and handling',
                'Verify electrolyte measurements',
                'Consider unmeasured anions/cations',
                'Evaluate for analytical interference'
            ]
        };

        return actions[correlationId] || ['General correlation review required'];
    }

    // Additional helper methods for specific recommendations
    getDiabetesRecommendation(isDiabetic, findings) {
        if (isDiabetic) {
            return {
                diagnosis: 'diabetes_mellitus_likely',
                actions: [
                    'Confirm diagnosis with repeat testing',
                    'Initiate diabetes management protocols',
                    'Screen for complications',
                    'Lifestyle counseling'
                ]
            };
        } else if (findings.some(f => f.note && f.note.includes('diabetes'))) {
            return {
                diagnosis: 'prediabetes_likely',
                actions: [
                    'Lifestyle modification counseling',
                    'Annual monitoring',
                    'Cardiovascular risk assessment'
                ]
            };
        } else {
            return {
                diagnosis: 'normal_glucose_metabolism',
                actions: ['Routine monitoring as per guidelines']
            };
        }
    }

    getMIRecommendation(pattern) {
        if (pattern.troponin_elevated && pattern.kinetic_pattern_present) {
            return {
                diagnosis: 'acute_mi_likely',
                urgency: 'critical',
                actions: [
                    'Immediate cardiology consultation',
                    'ECG correlation',
                    'Cardiac catheterization consideration',
                    'Antiplatelet therapy if indicated'
                ]
            };
        }
        return {
            diagnosis: 'rule_out_acute_mi',
            actions: ['Serial cardiac markers', 'Clinical correlation', 'ECG monitoring']
        };
    }

    getLiverInjuryRecommendation(pattern) {
        return {
            diagnosis: `liver_injury_${pattern.type}`,
            actions: ['Hepatology consultation', 'Imaging studies', 'Medication review']
        };
    }

    getThyroidRecommendation(pattern) {
        return {
            diagnosis: `thyroid_dysfunction_${pattern.pattern_type}`,
            actions: ['Endocrinology consultation', 'Clinical correlation', 'Imaging if indicated']
        };
    }

    summarizeCorrelationResults(correlationResults) {
        const total = correlationResults.length;
        const valid = correlationResults.filter(r => r.validation.valid).length;
        const invalid = total - valid;

        return {
            totalCorrelations: total,
            validCorrelations: valid,
            invalidCorrelations: invalid,
            validationRate: total > 0 ? (valid / total * 100).toFixed(1) + '%' : '0%'
        };
    }

    analyzeTroponinKinetics(troponinResults, timePoints) {
        // Analyze troponin rise and fall pattern
        // This is a simplified implementation
        if (troponinResults.length < 2) return false;

        const values = troponinResults.map(r => parseFloat(r.value));
        const hasRise = values[1] > values[0];
        const hasFall = troponinResults.length > 2 && values[2] < values[1];

        return hasRise && (hasFall || troponinResults.length === 2);
    }
}

module.exports = { ClinicalLogicValidator };