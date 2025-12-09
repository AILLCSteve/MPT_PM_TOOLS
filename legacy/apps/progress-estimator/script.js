// Sewer Jetting Production Estimator - JavaScript Logic

class ProductionCalculator {
    constructor() {
        this.baseProduction = 3100; // ft/day base rate
        this.heavyPenalty = 0.40;   // 40% reduction for heavy cleaning
        this.easementPenalty = 0.30; // 30% reduction for easement work
        this.baseFactor = 0.50;     // Base realization factor
        
        this.initializeElements();
        this.bindEvents();
        this.calculate();
    }

    initializeElements() {
        // Input elements
        this.totalFootage = document.getElementById('totalFootage');
        this.heavySlider = document.getElementById('heavySlider');
        this.heavyPercentage = document.getElementById('heavyPercentage');
        this.easementSlider = document.getElementById('easementSlider');
        this.easementPercentage = document.getElementById('easementPercentage');
        this.recyclerEnabled = document.getElementById('recyclerEnabled');
        this.recyclerSection = document.getElementById('recyclerSection');
        this.boostSlider = document.getElementById('boostSlider');
        this.boostRange = document.getElementById('boostRange');
        this.helpFactors = document.querySelectorAll('.help-factor');
        this.hurtFactors = document.querySelectorAll('.hurt-factor');
        this.calculatedF = document.getElementById('calculatedF');
        this.manualF = document.getElementById('manualF');
        this.manualFValue = document.getElementById('manualFValue');

        // Output elements
        this.prodRateWithout = document.getElementById('prodRateWithout');
        this.daysWithout = document.getElementById('daysWithout');
        this.prodRateWith = document.getElementById('prodRateWith');
        this.daysWith = document.getElementById('daysWith');
        this.timeSavings = document.getElementById('timeSavings');
        this.recyclerRow = document.querySelector('.recycler-row');
    }

    bindEvents() {
        // Sync sliders with number inputs
        this.heavySlider.addEventListener('input', () => {
            this.heavyPercentage.value = this.heavySlider.value;
            this.calculate();
        });
        
        this.heavyPercentage.addEventListener('input', () => {
            this.heavySlider.value = this.heavyPercentage.value;
            this.calculate();
        });

        this.easementSlider.addEventListener('input', () => {
            this.easementPercentage.value = this.easementSlider.value;
            this.calculate();
        });
        
        this.easementPercentage.addEventListener('input', () => {
            this.easementSlider.value = this.easementPercentage.value;
            this.calculate();
        });

        this.boostSlider.addEventListener('input', () => {
            this.boostRange.value = this.boostSlider.value;
            this.calculate();
        });
        
        this.boostRange.addEventListener('input', () => {
            this.boostSlider.value = this.boostRange.value;
            this.calculate();
        });

        // Recycler toggle
        this.recyclerEnabled.addEventListener('change', () => {
            this.recyclerSection.style.display = this.recyclerEnabled.checked ? 'block' : 'none';
            this.recyclerRow.style.display = this.recyclerEnabled.checked ? 'table-row' : 'none';
            this.calculate();
        });

        // Realization factor checkboxes
        this.helpFactors.forEach(checkbox => {
            checkbox.addEventListener('change', () => this.updateRealizationFactor());
        });
        
        this.hurtFactors.forEach(checkbox => {
            checkbox.addEventListener('change', () => this.updateRealizationFactor());
        });

        // Manual F override
        this.manualF.addEventListener('change', () => {
            this.manualFValue.disabled = !this.manualF.checked;
            this.calculate();
        });

        this.manualFValue.addEventListener('input', () => this.calculate());

        // Total footage input
        this.totalFootage.addEventListener('input', () => this.calculate());
    }

    updateRealizationFactor() {
        let f = this.baseFactor;
        
        // Add helps (+0.10 each)
        this.helpFactors.forEach(checkbox => {
            if (checkbox.checked) f += 0.10;
        });
        
        // Subtract hurts (-0.10 each)
        this.hurtFactors.forEach(checkbox => {
            if (checkbox.checked) f -= 0.10;
        });
        
        // Cap between 0 and 1
        f = Math.max(0, Math.min(1, f));
        
        this.calculatedF.textContent = f.toFixed(2);
        this.calculate();
    }

    getRealizationFactor() {
        if (this.manualF.checked) {
            return parseFloat(this.manualFValue.value) || 0.50;
        }
        return parseFloat(this.calculatedF.textContent) || 0.50;
    }

    calculateProduction(useRecycler = false) {
        const heavyPercent = parseFloat(this.heavyPercentage.value) / 100 || 0;
        const easementPercent = parseFloat(this.easementPercentage.value) / 100 || 0;
        
        // Apply penalties: (1 - Heavy% × 0.40) × (1 - Easement% × 0.30)
        const heavyPenaltyFactor = 1 - (heavyPercent * this.heavyPenalty);
        const easementPenaltyFactor = 1 - (easementPercent * this.easementPenalty);
        
        let production = this.baseProduction * heavyPenaltyFactor * easementPenaltyFactor;
        
        // Apply recycler boost if enabled
        if (useRecycler && this.recyclerEnabled.checked) {
            const boostRange = parseFloat(this.boostRange.value) || 0.50;
            const realizationFactor = this.getRealizationFactor();
            const recyclerBoost = 1 + (boostRange * realizationFactor);
            production *= recyclerBoost;
        }
        
        return Math.round(production);
    }

    calculate() {
        const totalFootage = parseFloat(this.totalFootage.value) || 0;
        
        if (totalFootage === 0) {
            this.clearResults();
            return;
        }

        // Calculate without recycler
        const prodWithout = this.calculateProduction(false);
        const daysWithout = Math.ceil(totalFootage / prodWithout);
        
        // Display without recycler results
        this.prodRateWithout.textContent = prodWithout.toLocaleString();
        this.daysWithout.textContent = daysWithout;

        // Calculate with recycler if enabled
        if (this.recyclerEnabled.checked) {
            const prodWith = this.calculateProduction(true);
            const daysWith = Math.ceil(totalFootage / prodWith);
            const savings = daysWithout - daysWith;
            
            this.prodRateWith.textContent = prodWith.toLocaleString();
            this.daysWith.textContent = daysWith;
            this.timeSavings.textContent = savings > 0 ? `${savings} days` : 'No savings';
            this.timeSavings.style.color = savings > 0 ? '#27ae60' : '#e74c3c';
        } else {
            this.prodRateWith.textContent = '-';
            this.daysWith.textContent = '-';
            this.timeSavings.textContent = '-';
            this.timeSavings.style.color = '#333';
        }
    }

    clearResults() {
        this.prodRateWithout.textContent = '-';
        this.daysWithout.textContent = '-';
        this.prodRateWith.textContent = '-';
        this.daysWith.textContent = '-';
        this.timeSavings.textContent = '-';
    }
}

// Initialize the calculator when the page loads
document.addEventListener('DOMContentLoaded', () => {
    new ProductionCalculator();
});

// Add tooltip functionality
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
        });
        
        element.addEventListener('mouseleave', () => {
            const tooltip = document.querySelector('.tooltip');
            if (tooltip) {
                tooltip.remove();
            }
        });
    });
});