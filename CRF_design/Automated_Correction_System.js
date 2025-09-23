/**
 * Automated Correction Suggestions System
 * Intelligent system for suggesting corrections to laboratory test results
 * Includes unit conversion, value correction, missing data imputation, and pattern-based corrections
 * 
 * Part of the Laboratory Quality Control System v1.0
 */

class AutomatedCorrectionSystem {
    constructor(testDefinitions, config = {}) {
        this.testDefinitions = testDefinitions;
        this.config = config;
        this.correctionHistory = [];
        this.errorPatterns = new Map();
        this.learningDatabase = new Map();
        this.correctionConfidenceThresholds = {
            unit_conversion: 0.9,
            decimal_correction: 0.8,
            digit_transposition: 0.7,
            missing_data_imputation: 0.6,
            pattern_correction: 0.75
        };
        
        this.initializeErrorPatterns();
        this.loadHistoricalCorrections();
    }

    /**
     * Initialize common error patterns database
     */
    initializeErrorPatterns() {
        // Unit conversion errors
        this.errorPatterns.set('unit_errors', {
            'glucose_mg_to_mmol': {
                pattern: 'value > 50 && unit === "mmol/L"',
                correction: 'divide by 18.0182',
                confidence: 0.95,
                description: 'Glucose value appears to be in mg/dL but reported as mmol/L'
            },
            'glucose_mmol_to_mg': {
                pattern: 'value < 4 && unit === "mg/dL"',
                correction: 'multiply by 18.0182',
                confidence: 0.95,
                description: 'Glucose value appears to be in mmol/L but reported as mg/dL'
            },
            'creatinine_mg_to_umol': {
                pattern: 'value < 2 && unit === "μmol/L"',
                correction: 'multiply by 88.4',
                confidence: 0.9,
                description: 'Creatinine value appears to be in mg/dL but reported as μmol/L'
            },
            'creatinine_umol_to_mg': {
                pattern: 'value > 500 && unit === "mg/dL"',
                correction: 'divide by 88.4',
                confidence: 0.9,
                description: 'Creatinine value appears to be in μmol/L but reported as mg/dL'
            }
        });

        // Decimal point errors
        this.errorPatterns.set('decimal_errors', {
            'factor_10_high': {
                pattern: 'value > reference_max * 10 && value / 10 within reference_range',
                correction: 'divide by 10',
                confidence: 0.85,
                description: 'Value appears to be 10x too high - possible decimal point error'
            },
            'factor_10_low': {
                pattern: 'value < reference_min / 10 && value * 10 within reference_range',
                correction: 'multiply by 10',
                confidence: 0.85,
                description: 'Value appears to be 10x too low - possible decimal point error'
            },
            'factor_100_high': {
                pattern: 'value > reference_max * 100 && value / 100 within reference_range',
                correction: 'divide by 100',
                confidence: 0.8,
                description: 'Value appears to be 100x too high - possible decimal point error'
            },
            'factor_100_low': {
                pattern: 'value < reference_min / 100 && value * 100 within reference_range',
                correction: 'multiply by 100',
                confidence: 0.8,
                description: 'Value appears to be 100x too low - possible decimal point error'
            }
        });

        // Digit transposition errors
        this.errorPatterns.set('transposition_errors', {
            'adjacent_digits': {
                description: 'Adjacent digits may be transposed',
                confidence_threshold: 0.7
            },
            'first_last_digits': {
                description: 'First and last digits may be transposed',
                confidence_threshold: 0.6
            },
            'middle_digits': {
                description: 'Middle digits may be transposed',
                confidence_threshold: 0.65
            }
        });

        // Common data entry errors
        this.errorPatterns.set('entry_errors', {
            'extra_zero': {
                pattern: 'ends with multiple zeros',
                correction: 'remove extra zeros',
                confidence: 0.7
            },
            'missing_decimal': {
                pattern: 'integer value outside range but divided by 10/100 within range',
                correction: 'add decimal point',
                confidence: 0.75
            },
            'wrong_decimal_position': {
                pattern: 'decimal in wrong position',
                correction: 'move decimal point',
                confidence: 0.8
            }
        });
    }

    /**
     * Load historical corrections for pattern learning
     */
    loadHistoricalCorrections() {
        // In production, this would load from database
        // For now, initialize with empty learning database
        this.learningDatabase.set('corrections_applied', []);
        this.learningDatabase.set('user_feedback', []);
        this.learningDatabase.set('pattern_success_rates', new Map());
    }

    /**
     * Main entry point for correction suggestions
     */
    async generateCorrectionSuggestions(validationResult, historicalData = [], patientContext = {}) {
        const startTime = performance.now();
        
        try {
            const suggestions = [];

            // Unit conversion corrections
            const unitSuggestions = await this.suggestUnitCorrections(validationResult);
            suggestions.push(...unitSuggestions);

            // Value range corrections
            const valueSuggestions = await this.suggestValueCorrections(validationResult, historicalData);
            suggestions.push(...valueSuggestions);

            // Missing data imputation
            const imputationSuggestions = await this.suggestMissingDataImputation(validationResult, historicalData, patientContext);
            suggestions.push(...imputationSuggestions);

            // Error pattern recognition corrections
            const patternSuggestions = await this.suggestPatternBasedCorrections(validationResult, historicalData);
            suggestions.push(...patternSuggestions);

            // Rank suggestions by confidence and feasibility
            const rankedSuggestions = this.rankSuggestions(suggestions);

            // Generate final correction package
            const correctionPackage = {
                testId: validationResult.testId,
                originalValue: validationResult.value,
                originalUnit: validationResult.unit,
                patientId: validationResult.patientId,
                suggestions: rankedSuggestions,
                suggestionsCount: rankedSuggestions.length,
                highConfidenceSuggestions: rankedSuggestions.filter(s => s.confidence >= 0.8).length,
                overallConfidence: this.calculateOverallConfidence(rankedSuggestions),
                implementationRisk: this.assessImplementationRisk(rankedSuggestions),
                processingTime: performance.now() - startTime,
                timestamp: new Date(),
                recommendations: this.generateImplementationRecommendations(rankedSuggestions)
            };

            // Store for learning
            this.storeCorrectionAttempt(correctionPackage);

            return correctionPackage;

        } catch (error) {
            console.error('Error generating correction suggestions:', error);
            return {
                testId: validationResult.testId,
                error: error.message,
                suggestions: [],
                processingTime: performance.now() - startTime
            };
        }
    }

    /**
     * Suggest unit correction when unit mismatch detected
     */
    async suggestUnitCorrections(validationResult) {
        const suggestions = [];
        
        if (!validationResult.validations?.unit || validationResult.validations.unit.valid) {
            return suggestions;
        }

        const testDef = this.getTestDefinition(validationResult.testId);
        if (!testDef) return suggestions;

        const currentValue = parseFloat(validationResult.value);
        const currentUnit = validationResult.unit;

        // Check each possible valid unit
        const validUnits = [testDef.primary_unit, ...(testDef.alternative_units?.map(u => u.unit) || [])];

        for (const targetUnit of validUnits) {
            if (targetUnit === currentUnit) continue;

            const convertedValue = this.convertUnit(currentValue, currentUnit, targetUnit, testDef);
            if (convertedValue !== null) {
                const isInRange = this.checkValueInBiologicalRange(convertedValue, targetUnit, testDef);
                
                if (isInRange.valid) {
                    const confidence = this.calculateUnitCorrectionConfidence(currentValue, convertedValue, testDef, isInRange);
                    
                    suggestions.push({
                        type: 'unit_conversion',
                        priority: confidence > 0.9 ? 'high' : 'medium',
                        confidence: confidence,
                        description: `Convert ${currentValue} ${currentUnit} to ${convertedValue.toFixed(this.getPrecisionForUnit(targetUnit, testDef))} ${targetUnit}`,
                        originalValue: currentValue,
                        originalUnit: currentUnit,
                        suggestedValue: convertedValue,
                        suggestedUnit: targetUnit,
                        conversionFactor: this.getConversionFactor(currentUnit, targetUnit, testDef),
                        justification: `Converted value ${convertedValue.toFixed(2)} ${targetUnit} falls within expected biological range`,
                        validationImprovement: {
                            before: { valid: false, reason: 'unit_mismatch' },
                            after: { valid: true, reason: 'unit_corrected' }
                        },
                        implementationRisk: confidence > 0.9 ? 'low' : 'medium',
                        userConfirmationRequired: confidence < 0.95,
                        automaticApplicationEligible: confidence >= this.correctionConfidenceThresholds.unit_conversion
                    });
                }
            }
        }

        return suggestions;
    }

    /**
     * Suggest value corrections when out of range
     */
    async suggestValueCorrections(validationResult, historicalData) {
        const suggestions = [];
        
        if (!validationResult.validations?.range || validationResult.validations.range.valid) {
            return suggestions;
        }

        const testDef = this.getTestDefinition(validationResult.testId);
        if (!testDef) return suggestions;

        const currentValue = parseFloat(validationResult.value);
        const currentUnit = validationResult.unit;

        // Check for decimal point errors
        const decimalSuggestions = this.generateDecimalPointCorrections(currentValue, currentUnit, testDef);
        suggestions.push(...decimalSuggestions);

        // Check for digit transposition errors
        const transpositionSuggestions = this.generateTranspositionCorrections(currentValue, currentUnit, testDef);
        suggestions.push(...transpositionSuggestions);

        // Check for extra/missing zeros
        const digitSuggestions = this.generateDigitCorrections(currentValue, currentUnit, testDef);
        suggestions.push(...digitSuggestions);

        // Check against historical patterns
        if (historicalData.length > 0) {
            const historicalSuggestions = this.generateHistoricalBasedCorrections(currentValue, currentUnit, historicalData, testDef);
            suggestions.push(...historicalSuggestions);
        }

        return suggestions;
    }

    /**
     * Generate decimal point correction suggestions
     */
    generateDecimalPointCorrections(value, unit, testDef) {
        const suggestions = [];
        const factors = [0.1, 0.01, 0.001, 10, 100, 1000];

        factors.forEach(factor => {
            const correctedValue = value * factor;
            const isInRange = this.checkValueInBiologicalRange(correctedValue, unit, testDef);
            
            if (isInRange.valid) {
                const confidence = this.calculateDecimalCorrectionConfidence(value, correctedValue, testDef, factor);
                
                suggestions.push({
                    type: 'decimal_point_correction',
                    priority: confidence > 0.8 ? 'high' : 'medium',
                    confidence: confidence,
                    description: `Correct ${value} to ${correctedValue} (${factor < 1 ? 'divide' : 'multiply'} by ${Math.abs(Math.log10(factor))})`,
                    originalValue: value,
                    suggestedValue: correctedValue,
                    correctionFactor: factor,
                    justification: `Corrected value ${correctedValue} falls within ${isInRange.rangeType} range`,
                    errorType: factor < 1 ? 'decimal_too_far_right' : 'decimal_too_far_left',
                    implementationRisk: this.assessDecimalCorrectionRisk(factor, confidence),
                    userConfirmationRequired: confidence < 0.8,
                    automaticApplicationEligible: confidence >= this.correctionConfidenceThresholds.decimal_correction
                });
            }
        });

        return suggestions.sort((a, b) => b.confidence - a.confidence);
    }

    /**
     * Generate digit transposition correction suggestions
     */
    generateTranspositionCorrections(value, unit, testDef) {
        const suggestions = [];
        const valueStr = value.toString();
        
        // Only process reasonable lengths
        if (valueStr.length < 2 || valueStr.length > 6) {
            return suggestions;
        }

        const digits = valueStr.replace('.', '').split('');
        const hasDecimal = valueStr.includes('.');
        const decimalPosition = hasDecimal ? valueStr.indexOf('.') : -1;

        // Generate adjacent digit transpositions
        for (let i = 0; i < digits.length - 1; i++) {
            const transposed = [...digits];
            [transposed[i], transposed[i + 1]] = [transposed[i + 1], transposed[i]];
            
            let transposedValue = parseFloat(transposed.join(''));
            if (hasDecimal && decimalPosition > 0) {
                transposedValue = transposedValue / Math.pow(10, digits.length - decimalPosition);
            }
            
            const isInRange = this.checkValueInBiologicalRange(transposedValue, unit, testDef);
            if (isInRange.valid) {
                const confidence = this.calculateTranspositionConfidence(value, transposedValue, i, testDef);
                
                suggestions.push({
                    type: 'digit_transposition',
                    priority: confidence > 0.7 ? 'medium' : 'low',
                    confidence: confidence,
                    description: `Transpose digits at positions ${i} and ${i + 1}: ${value} → ${transposedValue}`,
                    originalValue: value,
                    suggestedValue: transposedValue,
                    transpositionPositions: [i, i + 1],
                    justification: `Transposed value ${transposedValue} falls within ${isInRange.rangeType} range`,
                    implementationRisk: 'medium',
                    userConfirmationRequired: true,
                    automaticApplicationEligible: confidence >= this.correctionConfidenceThresholds.digit_transposition
                });
            }
        }

        // Generate first-last digit transposition for longer numbers
        if (digits.length >= 3) {
            const transposed = [...digits];
            [transposed[0], transposed[transposed.length - 1]] = [transposed[transposed.length - 1], transposed[0]];
            
            let transposedValue = parseFloat(transposed.join(''));
            if (hasDecimal && decimalPosition > 0) {
                transposedValue = transposedValue / Math.pow(10, digits.length - decimalPosition);
            }
            
            const isInRange = this.checkValueInBiologicalRange(transposedValue, unit, testDef);
            if (isInRange.valid) {
                const confidence = this.calculateTranspositionConfidence(value, transposedValue, 'first_last', testDef);
                
                suggestions.push({
                    type: 'digit_transposition',
                    priority: 'low',
                    confidence: confidence,
                    description: `Transpose first and last digits: ${value} → ${transposedValue}`,
                    originalValue: value,
                    suggestedValue: transposedValue,
                    transpositionPositions: [0, digits.length - 1],
                    justification: `Transposed value ${transposedValue} falls within ${isInRange.rangeType} range`,
                    implementationRisk: 'high',
                    userConfirmationRequired: true,
                    automaticApplicationEligible: false
                });
            }
        }

        return suggestions.sort((a, b) => b.confidence - a.confidence);
    }

    /**
     * Generate digit-based corrections (extra zeros, missing digits)
     */
    generateDigitCorrections(value, unit, testDef) {
        const suggestions = [];
        const valueStr = value.toString();

        // Check for extra trailing zeros
        if (valueStr.endsWith('0')) {
            const zerosCount = valueStr.match(/0+$/)[0].length;
            for (let i = 1; i <= Math.min(zerosCount, 3); i++) {
                const correctedValue = value / Math.pow(10, i);
                const isInRange = this.checkValueInBiologicalRange(correctedValue, unit, testDef);
                
                if (isInRange.valid) {
                    const confidence = this.calculateDigitCorrectionConfidence(value, correctedValue, 'remove_zeros', testDef);
                    
                    suggestions.push({
                        type: 'digit_correction',
                        subtype: 'remove_trailing_zeros',
                        priority: confidence > 0.7 ? 'medium' : 'low',
                        confidence: confidence,
                        description: `Remove ${i} trailing zero${i > 1 ? 's' : ''}: ${value} → ${correctedValue}`,
                        originalValue: value,
                        suggestedValue: correctedValue,
                        zerosRemoved: i,
                        justification: `Value ${correctedValue} without trailing zeros falls within ${isInRange.rangeType} range`,
                        implementationRisk: 'medium',
                        userConfirmationRequired: confidence < 0.8,
                        automaticApplicationEligible: confidence >= 0.75
                    });
                }
            }
        }

        // Check for missing decimal point
        if (!valueStr.includes('.')) {
            for (let position = 1; position < valueStr.length; position++) {
                const beforeDecimal = valueStr.substring(0, position);
                const afterDecimal = valueStr.substring(position);
                const correctedValue = parseFloat(beforeDecimal + '.' + afterDecimal);
                
                const isInRange = this.checkValueInBiologicalRange(correctedValue, unit, testDef);
                if (isInRange.valid) {
                    const confidence = this.calculateDigitCorrectionConfidence(value, correctedValue, 'add_decimal', testDef);
                    
                    suggestions.push({
                        type: 'digit_correction',
                        subtype: 'add_decimal_point',
                        priority: confidence > 0.7 ? 'medium' : 'low',
                        confidence: confidence,
                        description: `Add decimal point at position ${position}: ${value} → ${correctedValue}`,
                        originalValue: value,
                        suggestedValue: correctedValue,
                        decimalPosition: position,
                        justification: `Value ${correctedValue} with decimal point falls within ${isInRange.rangeType} range`,
                        implementationRisk: 'medium',
                        userConfirmationRequired: true,
                        automaticApplicationEligible: confidence >= 0.8
                    });
                }
            }
        }

        return suggestions.sort((a, b) => b.confidence - a.confidence);
    }

    /**
     * Generate corrections based on historical data patterns
     */
    generateHistoricalBasedCorrections(currentValue, unit, historicalData, testDef) {
        const suggestions = [];
        
        if (historicalData.length < 3) return suggestions;

        // Calculate historical statistics
        const historicalValues = historicalData.map(d => parseFloat(d.value));
        const mean = historicalValues.reduce((sum, val) => sum + val, 0) / historicalValues.length;
        const stdDev = Math.sqrt(historicalValues.reduce((sum, val) => sum + Math.pow(val - mean, 2), 0) / historicalValues.length);

        // Check if current value is a significant outlier
        const zScore = Math.abs((currentValue - mean) / stdDev);
        
        if (zScore > 3) { // Significant outlier
            // Suggest the median historical value
            const sortedValues = [...historicalValues].sort((a, b) => a - b);
            const median = sortedValues[Math.floor(sortedValues.length / 2)];
            
            const confidence = this.calculateHistoricalCorrectionConfidence(currentValue, median, zScore, historicalData.length);
            
            suggestions.push({
                type: 'historical_pattern_correction',
                priority: 'low',
                confidence: confidence,
                description: `Current value ${currentValue} is ${zScore.toFixed(1)} standard deviations from historical mean. Consider median value ${median}`,
                originalValue: currentValue,
                suggestedValue: median,
                historicalMean: mean,
                historicalMedian: median,
                zScore: zScore,
                justification: `Value significantly deviates from patient's historical pattern (${historicalData.length} previous results)`,
                implementationRisk: 'high',
                userConfirmationRequired: true,
                automaticApplicationEligible: false,
                requiresClinicalReview: true
            });

            // Also suggest values within 2 standard deviations of mean
            const upperBound = mean + 2 * stdDev;
            const lowerBound = mean - 2 * stdDev;
            
            let suggestedValue;
            if (currentValue > mean) {
                suggestedValue = upperBound;
            } else {
                suggestedValue = lowerBound;
            }

            const isInRange = this.checkValueInBiologicalRange(suggestedValue, unit, testDef);
            if (isInRange.valid) {
                suggestions.push({
                    type: 'statistical_outlier_correction',
                    priority: 'low',
                    confidence: confidence * 0.8,
                    description: `Adjust outlier ${currentValue} to within 2 standard deviations: ${suggestedValue.toFixed(2)}`,
                    originalValue: currentValue,
                    suggestedValue: suggestedValue,
                    statisticalBasis: '2_sigma_rule',
                    justification: `Adjusted value falls within 2 standard deviations of historical mean`,
                    implementationRisk: 'high',
                    userConfirmationRequired: true,
                    automaticApplicationEligible: false,
                    requiresClinicalReview: true
                });
            }
        }

        return suggestions;
    }

    /**
     * Suggest missing data imputation
     */
    async suggestMissingDataImputation(validationResult, historicalData, patientContext) {
        const suggestions = [];
        
        // This would be used when a test result is missing entirely
        // For now, return empty array as this applies to missing results, not invalid ones
        
        if (historicalData.length >= 3) {
            const historicalValues = historicalData.map(d => parseFloat(d.value));
            const median = this.calculateMedian(historicalValues);
            const mean = historicalValues.reduce((sum, val) => sum + val, 0) / historicalValues.length;
            
            // Only suggest imputation if explicitly requested or if dealing with missing values
            // This is a placeholder for missing data scenarios
        }

        return suggestions;
    }

    /**
     * Suggest pattern-based corrections using machine learning patterns
     */
    async suggestPatternBasedCorrections(validationResult, historicalData) {
        const suggestions = [];
        
        // Analyze learned patterns from historical corrections
        const learnedPatterns = this.learningDatabase.get('pattern_success_rates') || new Map();
        const testId = validationResult.testId;
        const currentValue = parseFloat(validationResult.value);
        
        // Check if similar corrections have been successful in the past
        for (const [patternId, pattern] of learnedPatterns) {
            if (pattern.testId === testId && pattern.successRate > 0.7) {
                const applicability = this.checkPatternApplicability(currentValue, pattern, validationResult);
                
                if (applicability.applicable) {
                    suggestions.push({
                        type: 'learned_pattern_correction',
                        priority: 'medium',
                        confidence: pattern.successRate * applicability.confidence,
                        description: `Apply learned pattern: ${pattern.description}`,
                        originalValue: currentValue,
                        suggestedValue: applicability.suggestedValue,
                        patternId: patternId,
                        historicalSuccessRate: pattern.successRate,
                        justification: `Similar correction has ${(pattern.successRate * 100).toFixed(1)}% success rate in historical data`,
                        implementationRisk: 'medium',
                        userConfirmationRequired: pattern.successRate < 0.9,
                        automaticApplicationEligible: pattern.successRate >= this.correctionConfidenceThresholds.pattern_correction
                    });
                }
            }
        }

        return suggestions;
    }

    // =====================================================================
    // UTILITY AND HELPER METHODS
    // =====================================================================

    /**
     * Rank suggestions by confidence, feasibility, and risk
     */
    rankSuggestions(suggestions) {
        return suggestions
            .sort((a, b) => {
                // Primary sort: by confidence
                if (b.confidence !== a.confidence) {
                    return b.confidence - a.confidence;
                }
                
                // Secondary sort: by priority
                const priorityOrder = { high: 3, medium: 2, low: 1 };
                if (priorityOrder[b.priority] !== priorityOrder[a.priority]) {
                    return priorityOrder[b.priority] - priorityOrder[a.priority];
                }
                
                // Tertiary sort: by implementation risk (lower risk first)
                const riskOrder = { low: 3, medium: 2, high: 1 };
                return riskOrder[b.implementationRisk] - riskOrder[a.implementationRisk];
            })
            .map((suggestion, index) => ({
                ...suggestion,
                rank: index + 1
            }));
    }

    /**
     * Calculate overall confidence for all suggestions
     */
    calculateOverallConfidence(suggestions) {
        if (suggestions.length === 0) return 0;
        
        // Weight by confidence and rank
        let weightedSum = 0;
        let weightSum = 0;
        
        suggestions.forEach((suggestion, index) => {
            const weight = 1 / (index + 1); // Higher weight for higher ranked suggestions
            weightedSum += suggestion.confidence * weight;
            weightSum += weight;
        });
        
        return weightSum > 0 ? weightedSum / weightSum : 0;
    }

    /**
     * Assess implementation risk of suggestions
     */
    assessImplementationRisk(suggestions) {
        if (suggestions.length === 0) return 'none';
        
        const highRiskSuggestions = suggestions.filter(s => s.implementationRisk === 'high').length;
        const mediumRiskSuggestions = suggestions.filter(s => s.implementationRisk === 'medium').length;
        const lowRiskSuggestions = suggestions.filter(s => s.implementationRisk === 'low').length;
        
        if (highRiskSuggestions > 0) return 'high';
        if (mediumRiskSuggestions > 0) return 'medium';
        if (lowRiskSuggestions > 0) return 'low';
        
        return 'unknown';
    }

    /**
     * Generate implementation recommendations
     */
    generateImplementationRecommendations(suggestions) {
        const recommendations = [];
        
        const highConfidenceSuggestions = suggestions.filter(s => s.confidence >= 0.8);
        const autoApplicableSuggestions = suggestions.filter(s => s.automaticApplicationEligible);
        const requiresReviewSuggestions = suggestions.filter(s => s.requiresClinicalReview);
        
        if (highConfidenceSuggestions.length > 0) {
            recommendations.push({
                category: 'high_confidence_corrections',
                priority: 'immediate',
                recommendation: `${highConfidenceSuggestions.length} high-confidence correction(s) available`,
                actions: [
                    'Review top-ranked suggestions',
                    'Apply corrections with confidence > 90% if automatic application is enabled',
                    'Validate corrections against clinical context'
                ]
            });
        }
        
        if (autoApplicableSuggestions.length > 0) {
            recommendations.push({
                category: 'automatic_corrections',
                priority: 'routine',
                recommendation: `${autoApplicableSuggestions.length} correction(s) eligible for automatic application`,
                actions: [
                    'Enable automatic correction if confidence thresholds met',
                    'Monitor automatic corrections for accuracy',
                    'Set up audit trail for automatic changes'
                ]
            });
        }
        
        if (requiresReviewSuggestions.length > 0) {
            recommendations.push({
                category: 'clinical_review_required',
                priority: 'urgent',
                recommendation: `${requiresReviewSuggestions.length} correction(s) require clinical review`,
                actions: [
                    'Route to appropriate clinical reviewer',
                    'Provide clinical context and historical data',
                    'Request clinical decision on correction application'
                ]
            });
        }
        
        if (suggestions.length === 0) {
            recommendations.push({
                category: 'no_corrections_available',
                priority: 'review',
                recommendation: 'No automatic corrections identified',
                actions: [
                    'Manual review of test result required',
                    'Consider repeat testing',
                    'Review specimen collection and handling procedures',
                    'Check instrument calibration and maintenance'
                ]
            });
        }
        
        return recommendations;
    }

    /**
     * Get test definition from test definitions
     */
    getTestDefinition(testId) {
        // Search through test definitions to find the test
        if (!this.testDefinitions?.comprehensive_test_panels) return null;
        
        for (const panel of Object.values(this.testDefinitions.comprehensive_test_panels)) {
            if (panel.tests) {
                const test = panel.tests.find(t => t.test_id === testId);
                if (test) return test;
            }
        }
        
        return null;
    }

    /**
     * Convert unit using test definition
     */
    convertUnit(value, fromUnit, toUnit, testDef) {
        if (fromUnit === toUnit) return value;
        
        // Find conversion factor
        const primaryUnit = testDef.primary_unit;
        let conversionFactor = null;
        
        if (fromUnit === primaryUnit) {
            // Converting from primary to alternative
            const altUnit = testDef.alternative_units?.find(u => u.unit === toUnit);
            if (altUnit) {
                conversionFactor = altUnit.conversion_factor;
                return value * conversionFactor;
            }
        } else if (toUnit === primaryUnit) {
            // Converting from alternative to primary
            const altUnit = testDef.alternative_units?.find(u => u.unit === fromUnit);
            if (altUnit) {
                conversionFactor = 1 / altUnit.conversion_factor;
                return value * conversionFactor;
            }
        } else {
            // Converting between alternative units through primary
            const fromAltUnit = testDef.alternative_units?.find(u => u.unit === fromUnit);
            const toAltUnit = testDef.alternative_units?.find(u => u.unit === toUnit);
            
            if (fromAltUnit && toAltUnit) {
                // Convert to primary first, then to target
                const primaryValue = value / fromAltUnit.conversion_factor;
                return primaryValue * toAltUnit.conversion_factor;
            }
        }
        
        return null; // Conversion not possible
    }

    /**
     * Check if value is within biological range
     */
    checkValueInBiologicalRange(value, unit, testDef) {
        const limits = testDef.biological_limits;
        if (!limits) return { valid: false, reason: 'no_limits_defined' };
        
        const unitLimits = this.getLimitsForUnit(limits, unit);
        if (!unitLimits) return { valid: false, reason: 'no_unit_limits' };
        
        // Check ranges in order of specificity
        const ranges = [
            { name: 'physiological', min: 'physiological_minimum', max: 'physiological_maximum' },
            { name: 'absolute', min: 'absolute_minimum', max: 'absolute_maximum' }
        ];
        
        for (const range of ranges) {
            const min = unitLimits[range.min];
            const max = unitLimits[range.max];
            
            const withinMin = min === undefined || value >= min;
            const withinMax = max === undefined || value <= max;
            
            if (withinMin && withinMax) {
                return {
                    valid: true,
                    rangeType: range.name,
                    min: min,
                    max: max,
                    withinCritical: this.isWithinCriticalRange(value, unitLimits),
                    withinPanic: this.isWithinPanicRange(value, unitLimits)
                };
            }
        }
        
        return { valid: false, reason: 'outside_all_ranges' };
    }

    /**
     * Get limits for specific unit
     */
    getLimitsForUnit(limits, unit) {
        const limitCategories = [
            'absolute_minimum', 'absolute_maximum',
            'physiological_minimum', 'physiological_maximum',
            'critical_low', 'critical_high',
            'panic_low', 'panic_high'
        ];
        
        const unitLimits = {};
        limitCategories.forEach(category => {
            if (limits[category] && limits[category][unit] !== undefined) {
                unitLimits[category] = limits[category][unit];
            }
        });
        
        return Object.keys(unitLimits).length > 0 ? unitLimits : null;
    }

    /**
     * Check if value is within critical range
     */
    isWithinCriticalRange(value, unitLimits) {
        const low = unitLimits.critical_low;
        const high = unitLimits.critical_high;
        return (low !== undefined && value <= low) || (high !== undefined && value >= high);
    }

    /**
     * Check if value is within panic range
     */
    isWithinPanicRange(value, unitLimits) {
        const low = unitLimits.panic_low;
        const high = unitLimits.panic_high;
        return (low !== undefined && value <= low) || (high !== undefined && value >= high);
    }

    /**
     * Calculate confidence for unit correction
     */
    calculateUnitCorrectionConfidence(originalValue, convertedValue, testDef, rangeCheck) {
        let baseConfidence = 0.8;
        
        // Higher confidence if converted value is in physiological range
        if (rangeCheck.rangeType === 'physiological') {
            baseConfidence = 0.95;
        }
        
        // Lower confidence if still in critical/panic range
        if (rangeCheck.withinCritical) {
            baseConfidence *= 0.8;
        }
        if (rangeCheck.withinPanic) {
            baseConfidence *= 0.6;
        }
        
        // Consider magnitude of conversion
        const conversionRatio = convertedValue / originalValue;
        if (conversionRatio < 0.01 || conversionRatio > 100) {
            baseConfidence *= 0.7; // Large conversions are less confident
        }
        
        return Math.min(baseConfidence, 0.99);
    }

    /**
     * Calculate confidence for decimal correction
     */
    calculateDecimalCorrectionConfidence(originalValue, correctedValue, testDef, factor) {
        let baseConfidence = 0.75;
        
        // Common factors are more confident
        if ([0.1, 10, 0.01, 100].includes(factor)) {
            baseConfidence = 0.85;
        }
        
        // Very large factors are less confident
        if (factor <= 0.001 || factor >= 1000) {
            baseConfidence *= 0.6;
        }
        
        return Math.min(baseConfidence, 0.95);
    }

    /**
     * Calculate confidence for transposition correction
     */
    calculateTranspositionConfidence(originalValue, transposedValue, positions, testDef) {
        let baseConfidence = 0.65;
        
        // Adjacent transpositions are more likely
        if (typeof positions === 'number' || (Array.isArray(positions) && Math.abs(positions[1] - positions[0]) === 1)) {
            baseConfidence = 0.75;
        }
        
        // First-last transpositions are less likely
        if (positions === 'first_last') {
            baseConfidence = 0.5;
        }
        
        return Math.min(baseConfidence, 0.8);
    }

    /**
     * Calculate confidence for digit correction
     */
    calculateDigitCorrectionConfidence(originalValue, correctedValue, correctionType, testDef) {
        let baseConfidence = 0.7;
        
        if (correctionType === 'remove_zeros') {
            baseConfidence = 0.75;
        } else if (correctionType === 'add_decimal') {
            baseConfidence = 0.65;
        }
        
        return Math.min(baseConfidence, 0.85);
    }

    /**
     * Calculate confidence for historical correction
     */
    calculateHistoricalCorrectionConfidence(currentValue, suggestedValue, zScore, historicalCount) {
        let baseConfidence = 0.3;
        
        // More historical data increases confidence
        if (historicalCount >= 10) {
            baseConfidence = 0.5;
        } else if (historicalCount >= 5) {
            baseConfidence = 0.4;
        }
        
        // Very high z-scores reduce confidence (might be legitimate extreme value)
        if (zScore > 5) {
            baseConfidence *= 0.7;
        }
        
        return Math.min(baseConfidence, 0.6);
    }

    /**
     * Get precision for unit from test definition
     */
    getPrecisionForUnit(unit, testDef) {
        // Check alternative units for precision
        const altUnit = testDef.alternative_units?.find(u => u.unit === unit);
        if (altUnit && altUnit.precision) {
            return altUnit.precision;
        }
        
        // Default precision based on unit type
        const defaultPrecisions = {
            'mmol/L': 1,
            'mg/dL': 0,
            'μmol/L': 0,
            'g/L': 1,
            '%': 1,
            'mmol/mol': 0
        };
        
        return defaultPrecisions[unit] || 2;
    }

    /**
     * Get conversion factor between units
     */
    getConversionFactor(fromUnit, toUnit, testDef) {
        const primaryUnit = testDef.primary_unit;
        
        if (fromUnit === primaryUnit) {
            const altUnit = testDef.alternative_units?.find(u => u.unit === toUnit);
            return altUnit?.conversion_factor || null;
        } else if (toUnit === primaryUnit) {
            const altUnit = testDef.alternative_units?.find(u => u.unit === fromUnit);
            return altUnit ? 1 / altUnit.conversion_factor : null;
        }
        
        return null;
    }

    /**
     * Assess implementation risk for decimal correction
     */
    assessDecimalCorrectionRisk(factor, confidence) {
        if (confidence >= 0.9 && [0.1, 10].includes(factor)) {
            return 'low';
        } else if (confidence >= 0.8) {
            return 'medium';
        } else {
            return 'high';
        }
    }

    /**
     * Check pattern applicability
     */
    checkPatternApplicability(currentValue, pattern, validationResult) {
        // This would implement specific pattern matching logic
        // For now, return a basic implementation
        return {
            applicable: false,
            confidence: 0,
            suggestedValue: currentValue
        };
    }

    /**
     * Calculate median of array
     */
    calculateMedian(values) {
        const sorted = [...values].sort((a, b) => a - b);
        const mid = Math.floor(sorted.length / 2);
        return sorted.length % 2 === 0 ? (sorted[mid - 1] + sorted[mid]) / 2 : sorted[mid];
    }

    /**
     * Store correction attempt for learning
     */
    storeCorrectionAttempt(correctionPackage) {
        this.correctionHistory.push({
            timestamp: correctionPackage.timestamp,
            testId: correctionPackage.testId,
            originalValue: correctionPackage.originalValue,
            suggestions: correctionPackage.suggestions.length,
            highConfidenceSuggestions: correctionPackage.highConfidenceSuggestions,
            overallConfidence: correctionPackage.overallConfidence
        });
        
        // Keep only last 1000 attempts
        if (this.correctionHistory.length > 1000) {
            this.correctionHistory = this.correctionHistory.slice(-1000);
        }
    }

    /**
     * Record correction feedback for learning
     */
    recordCorrectionFeedback(correctionId, applied, successful, feedback = {}) {
        const feedbackRecord = {
            correctionId: correctionId,
            timestamp: new Date(),
            applied: applied,
            successful: successful,
            feedback: feedback
        };
        
        const userFeedback = this.learningDatabase.get('user_feedback') || [];
        userFeedback.push(feedbackRecord);
        this.learningDatabase.set('user_feedback', userFeedback);
        
        // Update pattern success rates
        this.updatePatternSuccessRates(correctionId, successful);
    }

    /**
     * Update pattern success rates for learning
     */
    updatePatternSuccessRates(correctionId, successful) {
        // Implementation would update success rates for specific patterns
        // This helps the system learn which corrections are most reliable
    }

    /**
     * Get correction statistics
     */
    getCorrectionStatistics(timeframe = '30d') {
        const cutoffTime = new Date();
        cutoffTime.setDate(cutoffTime.getDate() - parseInt(timeframe));
        
        const recentCorrections = this.correctionHistory.filter(c => c.timestamp >= cutoffTime);
        
        return {
            totalCorrections: recentCorrections.length,
            averageSuggestions: recentCorrections.reduce((sum, c) => sum + c.suggestions, 0) / recentCorrections.length || 0,
            averageConfidence: recentCorrections.reduce((sum, c) => sum + c.overallConfidence, 0) / recentCorrections.length || 0,
            highConfidenceRate: recentCorrections.filter(c => c.overallConfidence >= 0.8).length / recentCorrections.length * 100 || 0,
            correctionsByType: this.calculateCorrectionTypeDistribution(recentCorrections)
        };
    }

    /**
     * Calculate correction type distribution
     */
    calculateCorrectionTypeDistribution(corrections) {
        // This would analyze the types of corrections being suggested
        // Implementation would depend on storing more detailed correction type data
        return {
            unit_conversion: 0,
            decimal_correction: 0,
            digit_transposition: 0,
            pattern_based: 0,
            historical_based: 0
        };
    }
}

module.exports = { AutomatedCorrectionSystem };