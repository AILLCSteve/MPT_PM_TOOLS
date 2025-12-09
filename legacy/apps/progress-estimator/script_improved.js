// Sewer Jetting Production Estimator - Improved JavaScript with Validation

class ValidationError extends Error {
    constructor(message, field) {
        super(message);
        this.field = field;
        this.name = 'ValidationError';
    }
}

class InputValidator {
    /**
     * Validate numeric input within a range.
     */
    static validateNumber(value, min, max, fieldName) {
        const num = parseFloat(value);

        if (isNaN(num)) {
            throw new ValidationError(`${fieldName} must be a valid number`, fieldName);
        }

        if (num < min) {
            throw new ValidationError(`${fieldName} must be at least ${min}`, fieldName);
        }

        if (num > max) {
            throw new ValidationError(`${fieldName} cannot exceed ${max}`, fieldName);
        }

        return num;
    }

    /**
     * Validate percentage input (0-100).
     */
    static validatePercentage(value, fieldName) {
        return this.validateNumber(value, 0, 100, fieldName);
    }

    /**
     * Validate positive number.
     */
    static validatePositive(value, fieldName) {
        const num = parseFloat(value);

        if (isNaN(num) || num <= 0) {
            throw new ValidationError(`${fieldName} must be a positive number`, fieldName);
        }

        return num;
    }
}

class ProductionCalculator {
    constructor() {
        // Configuration constants
        this.config = {
            baseProduction: 3100,      // ft/day base rate
            heavyPenalty: 0.40,        // 40% reduction for heavy cleaning
            easementPenalty: 0.30,     // 30% reduction for easement work
            baseFactor: 0.50,          // Base realization factor
            factorIncrement: 0.10,     // Per-factor adjustment
            minBoost: 0.30,
            maxBoost: 0.70,
            minFactor: 0,
            maxFactor: 1
        };

        this.initializeElements();
        this.bindEvents();
        this.calculate();
    }

    initializeElements() {
        // Input elements
        this.elements = {
            totalFootage: document.getElementById('totalFootage'),
            heavySlider: document.getElementById('heavySlider'),
            heavyPercentage: document.getElementById('heavyPercentage'),
            easementSlider: document.getElementById('easementSlider'),
            easementPercentage: document.getElementById('easementPercentage'),
            recyclerEnabled: document.getElementById('recyclerEnabled'),
            recyclerSection: document.getElementById('recyclerSection'),
            boostSlider: document.getElementById('boostSlider'),
            boostRange: document.getElementById('boostRange'),
            helpFactors: document.querySelectorAll('.help-factor'),
            hurtFactors: document.querySelectorAll('.hurt-factor'),
            calculatedF: document.getElementById('calculatedF'),
            manualF: document.getElementById('manualF'),
            manualFValue: document.getElementById('manualFValue'),

            // Output elements
            prodRateWithout: document.getElementById('prodRateWithout'),
            daysWithout: document.getElementById('daysWithout'),
            prodRateWith: document.getElementById('prodRateWith'),
            daysWith: document.getElementById('daysWith'),
            timeSavings: document.getElementById('timeSavings'),
            recyclerRow: document.querySelector('.recycler-row')
        };
    }

    bindEvents() {
        // Sync sliders with number inputs
        this.bindSliderSync('heavy');
        this.bindSliderSync('easement');
        this.bindSliderSync('boost');

        // Recycler toggle
        this.elements.recyclerEnabled.addEventListener('change', () => {
            const isEnabled = this.elements.recyclerEnabled.checked;
            this.elements.recyclerSection.style.display = isEnabled ? 'block' : 'none';
            this.elements.recyclerRow.style.display = isEnabled ? 'table-row' : 'none';
            this.calculate();
        });

        // Realization factor checkboxes
        this.elements.helpFactors.forEach(checkbox => {
            checkbox.addEventListener('change', () => this.updateRealizationFactor());
        });

        this.elements.hurtFactors.forEach(checkbox => {
            checkbox.addEventListener('change', () => this.updateRealizationFactor());
        });

        // Manual F override
        this.elements.manualF.addEventListener('change', () => {
            this.elements.manualFValue.disabled = !this.elements.manualF.checked;
            this.calculate();
        });

        this.elements.manualFValue.addEventListener('input', () => this.calculate());

        // Total footage input with validation
        this.elements.totalFootage.addEventListener('input', () => this.calculate());
        this.elements.totalFootage.addEventListener('blur', () => this.validateTotalFootage());
    }

    bindSliderSync(prefix) {
        const slider = this.elements[`${prefix}Slider`];
        const input = prefix === 'boost'
            ? this.elements[`${prefix}Range`]
            : this.elements[`${prefix}Percentage`];

        slider.addEventListener('input', () => {
            input.value = slider.value;
            this.clearError(input);
            this.calculate();
        });

        input.addEventListener('input', () => {
            slider.value = input.value;
            this.clearError(input);
            this.calculate();
        });

        input.addEventListener('blur', () => {
            this.validateInput(input, prefix);
        });
    }

    validateInput(inputElement, type) {
        try {
            const value = inputElement.value;

            switch(type) {
                case 'heavy':
                case 'easement':
                    InputValidator.validatePercentage(value, type + ' percentage');
                    break;
                case 'boost':
                    InputValidator.validateNumber(
                        value,
                        this.config.minBoost,
                        this.config.maxBoost,
                        'Boost range'
                    );
                    break;
            }

            this.clearError(inputElement);
        } catch (error) {
            if (error instanceof ValidationError) {
                this.showError(inputElement, error.message);
            }
        }
    }

    validateTotalFootage() {
        try {
            const value = this.elements.totalFootage.value;
            if (value) {
                InputValidator.validatePositive(value, 'Total footage');
            }
            this.clearError(this.elements.totalFootage);
        } catch (error) {
            if (error instanceof ValidationError) {
                this.showError(this.elements.totalFootage, error.message);
            }
        }
    }

    showError(inputElement, message) {
        inputElement.classList.add('error');

        // Create or update error message
        let errorDiv = inputElement.parentElement.querySelector('.error-message');
        if (!errorDiv) {
            errorDiv = document.createElement('div');
            errorDiv.className = 'error-message';
            inputElement.parentElement.appendChild(errorDiv);
        }

        errorDiv.textContent = message;
        errorDiv.classList.add('show');
    }

    clearError(inputElement) {
        inputElement.classList.remove('error');
        const errorDiv = inputElement.parentElement.querySelector('.error-message');
        if (errorDiv) {
            errorDiv.classList.remove('show');
        }
    }

    updateRealizationFactor() {
        let f = this.config.baseFactor;

        // Add helps (+0.10 each)
        this.elements.helpFactors.forEach(checkbox => {
            if (checkbox.checked) f += this.config.factorIncrement;
        });

        // Subtract hurts (-0.10 each)
        this.elements.hurtFactors.forEach(checkbox => {
            if (checkbox.checked) f -= this.config.factorIncrement;
        });

        // Cap between configured min and max
        f = Math.max(this.config.minFactor, Math.min(this.config.maxFactor, f));

        this.elements.calculatedF.textContent = f.toFixed(2);
        this.calculate();
    }

    getRealizationFactor() {
        if (this.elements.manualF.checked) {
            return parseFloat(this.elements.manualFValue.value) || this.config.baseFactor;
        }
        return parseFloat(this.elements.calculatedF.textContent) || this.config.baseFactor;
    }

    calculateProduction(useRecycler = false) {
        try {
            const heavyPercent = InputValidator.validatePercentage(
                this.elements.heavyPercentage.value || 0,
                'Heavy percentage'
            ) / 100;

            const easementPercent = InputValidator.validatePercentage(
                this.elements.easementPercentage.value || 0,
                'Easement percentage'
            ) / 100;

            // Apply penalties: (1 - Heavy% × 0.40) × (1 - Easement% × 0.30)
            const heavyPenaltyFactor = 1 - (heavyPercent * this.config.heavyPenalty);
            const easementPenaltyFactor = 1 - (easementPercent * this.config.easementPenalty);

            let production = this.config.baseProduction * heavyPenaltyFactor * easementPenaltyFactor;

            // Apply recycler boost if enabled
            if (useRecycler && this.elements.recyclerEnabled.checked) {
                const boostRange = parseFloat(this.elements.boostRange.value) || 0.50;
                const realizationFactor = this.getRealizationFactor();
                const recyclerBoost = 1 + (boostRange * realizationFactor);
                production *= recyclerBoost;
            }

            return Math.round(production);
        } catch (error) {
            console.error('Calculation error:', error);
            return 0;
        }
    }

    calculate() {
        try {
            const totalFootage = parseFloat(this.elements.totalFootage.value) || 0;

            if (totalFootage === 0) {
                this.clearResults();
                return;
            }

            // Validate total footage
            InputValidator.validatePositive(totalFootage, 'Total footage');

            // Calculate without recycler
            const prodWithout = this.calculateProduction(false);
            const daysWithout = Math.ceil(totalFootage / prodWithout);

            // Display without recycler results
            this.elements.prodRateWithout.textContent = prodWithout.toLocaleString();
            this.elements.daysWithout.textContent = daysWithout;

            // Calculate with recycler if enabled
            if (this.elements.recyclerEnabled.checked) {
                const prodWith = this.calculateProduction(true);
                const daysWith = Math.ceil(totalFootage / prodWith);
                const savings = daysWithout - daysWith;

                this.elements.prodRateWith.textContent = prodWith.toLocaleString();
                this.elements.daysWith.textContent = daysWith;
                this.elements.timeSavings.textContent = savings > 0 ? `${savings} days` : 'No savings';
                this.elements.timeSavings.style.color = savings > 0 ? 'var(--success-color)' : 'var(--danger-color)';
            } else {
                this.elements.prodRateWith.textContent = '-';
                this.elements.daysWith.textContent = '-';
                this.elements.timeSavings.textContent = '-';
                this.elements.timeSavings.style.color = 'var(--text-primary)';
            }
        } catch (error) {
            if (error instanceof ValidationError) {
                console.warn('Validation error during calculation:', error.message);
            } else {
                console.error('Unexpected calculation error:', error);
            }
        }
    }

    clearResults() {
        this.elements.prodRateWithout.textContent = '-';
        this.elements.daysWithout.textContent = '-';
        this.elements.prodRateWith.textContent = '-';
        this.elements.daysWith.textContent = '-';
        this.elements.timeSavings.textContent = '-';
    }
}

// Initialize the calculator when the page loads
document.addEventListener('DOMContentLoaded', () => {
    new ProductionCalculator();
});

// Tooltip functionality
document.addEventListener('DOMContentLoaded', () => {
    const tooltipElements = document.querySelectorAll('[data-tooltip]');

    tooltipElements.forEach(element => {
        element.addEventListener('mouseenter', (e) => {
            const tooltip = document.createElement('div');
            tooltip.className = 'tooltip';
            tooltip.textContent = e.target.getAttribute('data-tooltip');
            document.body.appendChild(tooltip);

            const rect = e.target.getBoundingClientRect();
            tooltip.style.left = rect.left + 'px';
            tooltip.style.top = (rect.bottom + 5) + 'px';

            // Store tooltip reference on element for cleanup
            element._tooltip = tooltip;
        });

        element.addEventListener('mouseleave', (e) => {
            if (element._tooltip) {
                element._tooltip.remove();
                element._tooltip = null;
            }
        });
    });
});
