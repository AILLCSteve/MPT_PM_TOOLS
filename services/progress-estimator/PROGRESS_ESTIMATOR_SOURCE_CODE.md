# CIPP Production Estimator - Complete Source Code

**File**: `legacy/apps/progress-estimator/CIPPEstimator_Comprehensive.html`
**Lines**: 1,583
**Type**: Self-contained HTML with embedded CSS and JavaScript
**Date Extracted**: 2025-12-08

---

## Complete HTML Source

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CIPP Production Estimator - Comprehensive | MPT Tools</title>
    <style>
/* COMPREHENSIVE CIPP PRODUCTION ESTIMATOR */

* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    line-height: 1.6;
    color: #ffffff;
    position: relative;
    min-height: 100vh;
}

body::before {
    content: '';
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background-image: url('/shared/assets/images/bg1.jpg');
    background-size: cover;
    background-position: center center;
    background-repeat: no-repeat;
    background-attachment: fixed;
    filter: brightness(0.75);
    z-index: -2;
}

body::after {
    content: '';
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: linear-gradient(135deg, rgba(91, 127, 204, 0.4) 0%, rgba(30, 58, 138, 0.5) 100%);
    z-index: -1;
}

/* MPT Navbar */
.mpt-navbar {
    background: linear-gradient(135deg, #1E3A8A, #5B7FCC);
    padding: 15px 30px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
    position: sticky;
    top: 0;
    z-index: 1000;
}

.mpt-navbar .logo-container {
    display: flex;
    align-items: center;
    gap: 15px;
}

.mpt-navbar img {
    height: 40px;
    width: auto;
}

.mpt-navbar .app-title {
    color: white;
    font-size: 1.2rem;
    font-weight: 600;
}

.mpt-navbar .home-link {
    color: white;
    text-decoration: none;
    padding: 8px 20px;
    border: 2px solid white;
    border-radius: 5px;
    transition: all 0.3s;
    font-weight: 500;
}

.mpt-navbar .home-link:hover {
    background-color: white;
    color: #1E3A8A;
}

.container {
    max-width: 1600px;
    margin: 0 auto;
    padding: 20px;
}

header {
    text-align: center;
    margin-bottom: 30px;
    padding: 20px;
    background: linear-gradient(135deg, rgba(30, 58, 138, 0.15), rgba(91, 127, 204, 0.15));
    backdrop-filter: blur(2.5px);
    color: white;
    border-radius: 10px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

header h1 {
    font-size: 2.5rem;
    margin-bottom: 10px;
    font-weight: 700;
}

header p {
    font-size: 1.1rem;
    opacity: 0.9;
}

/* Mode Selector */
.mode-selector {
    background: rgba(255, 255, 255, 0.15);
    backdrop-filter: blur(2.5px);
    padding: 25px;
    border-radius: 10px;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
    margin-bottom: 30px;
}

.mode-selector h2 {
    color: #ffffff;
    font-size: 1.8rem;
    margin-bottom: 20px;
    border-bottom: 3px solid #5B7FCC;
    padding-bottom: 10px;
}

.mode-buttons {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: 15px;
}

.mode-btn {
    padding: 20px;
    border: 3px solid rgba(255, 255, 255, 0.3);
    border-radius: 10px;
    background: rgba(255, 255, 255, 0.1);
    color: white;
    cursor: pointer;
    transition: all 0.3s;
    text-align: center;
    font-size: 1.1rem;
    font-weight: 600;
}

.mode-btn:hover {
    background: rgba(255, 255, 255, 0.2);
    border-color: #5B7FCC;
    transform: translateY(-2px);
}

.mode-btn.active {
    background: linear-gradient(135deg, #5B7FCC, #1E3A8A);
    border-color: white;
    box-shadow: 0 4px 15px rgba(91, 127, 204, 0.5);
}

.mode-btn .mode-icon {
    font-size: 2em;
    display: block;
    margin-bottom: 10px;
}

.mode-btn .mode-description {
    font-size: 0.85rem;
    opacity: 0.9;
    font-weight: 400;
    margin-top: 5px;
}

/* Main Grid */
.main-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 30px;
    margin-bottom: 30px;
}

.section {
    background: rgba(255, 255, 255, 0.15);
    backdrop-filter: blur(2.5px);
    padding: 25px;
    border-radius: 10px;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.section.hidden {
    display: none;
}

h2 {
    color: #ffffff;
    font-size: 1.8rem;
    margin-bottom: 20px;
    border-bottom: 3px solid #5B7FCC;
    padding-bottom: 10px;
}

h3 {
    color: #ffffff;
    font-size: 1.4rem;
    margin: 20px 0 15px 0;
}

h4 {
    color: #ffffff;
    font-size: 1.2rem;
    margin: 15px 0 10px 0;
}

h5 {
    color: #1E3A8A;
    font-size: 1rem;
    margin-bottom: 10px;
}

.input-group {
    margin-bottom: 20px;
}

.input-group label {
    display: block;
    margin-bottom: 8px;
    font-weight: 600;
    color: #ffffff;
}

.input-group small {
    display: block;
    margin-top: 5px;
    color: rgba(255, 255, 255, 0.8);
    font-size: 0.85rem;
}

input[type="number"],
select {
    width: 100%;
    padding: 12px 15px;
    border: 2px solid #ddd;
    border-radius: 5px;
    font-size: 16px;
    transition: border-color 0.3s;
}

input[type="number"]:focus,
select:focus {
    outline: none;
    border-color: #5B7FCC;
}

.slider-container {
    display: flex;
    align-items: center;
    gap: 15px;
    margin-top: 8px;
}

.slider {
    flex: 1;
    height: 6px;
    border-radius: 3px;
    background: #ddd;
    outline: none;
}

.slider::-webkit-slider-thumb {
    appearance: none;
    width: 20px;
    height: 20px;
    border-radius: 50%;
    background: #5B7FCC;
    cursor: pointer;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

.slider::-moz-range-thumb {
    width: 20px;
    height: 20px;
    border-radius: 50%;
    background: #5B7FCC;
    cursor: pointer;
    border: none;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

.number-input {
    width: 100px;
    padding: 8px 12px;
    border: 2px solid #ddd;
    border-radius: 5px;
    font-size: 14px;
    text-align: center;
}

.unit {
    font-weight: 600;
    color: #ffffff;
    min-width: 60px;
}

/* Penalty/Boost Sections */
.penalty-section {
    background: rgba(248, 249, 250, 0.95);
    backdrop-filter: blur(5px);
    padding: 20px;
    border-radius: 8px;
    border: 2px solid rgba(233, 236, 239, 0.9);
    margin: 15px 0;
}

.penalty-section h5 {
    color: #1E3A8A;
    font-size: 1.1rem;
    margin-bottom: 15px;
    display: flex;
    align-items: center;
    gap: 10px;
}

.penalty-grid {
    display: grid;
    grid-template-columns: 1fr;
    gap: 15px;
}

.penalty-item {
    display: flex;
    flex-direction: column;
    gap: 8px;
}

.penalty-item label {
    font-size: 0.95rem;
    font-weight: 600;
    color: #333;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.penalty-value {
    color: #5B7FCC;
    font-weight: 700;
}

/* Pipe Size Grid */
.pipe-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
    gap: 10px;
    margin-top: 10px;
}

.pipe-checkbox {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 10px;
    background: rgba(255, 255, 255, 0.9);
    border: 2px solid #ddd;
    border-radius: 6px;
    cursor: pointer;
    transition: all 0.2s;
}

.pipe-checkbox:hover {
    background: rgba(91, 127, 204, 0.1);
    border-color: #5B7FCC;
}

.pipe-checkbox input[type="checkbox"] {
    width: 18px;
    height: 18px;
    cursor: pointer;
}

.pipe-checkbox label {
    cursor: pointer;
    color: #333;
    font-size: 0.9rem;
    font-weight: 500;
    margin: 0;
}

/* Results */
table {
    width: 100%;
    border-collapse: collapse;
    margin-bottom: 20px;
    background: white;
    border-radius: 8px;
    overflow: hidden;
}

th, td {
    padding: 12px 15px;
    text-align: left;
    border-bottom: 1px solid #ddd;
    color: #333;
}

th {
    background: #f8f9fa;
    font-weight: 600;
    color: #1E3A8A;
}

tr:nth-child(even) {
    background: #f8f9fa;
}

.highlight-row {
    background: #DBEAFE !important;
    border-left: 4px solid #5B7FCC;
    font-weight: 600;
}

/* Recommendation Box */
.recommendation-box {
    background: linear-gradient(135deg, rgba(34, 197, 94, 0.1), rgba(16, 185, 129, 0.1));
    border: 2px solid #22c55e;
    border-left: 6px solid #22c55e;
    border-radius: 8px;
    padding: 20px;
    margin: 20px 0;
    color: #333;
}

.recommendation-box h4 {
    color: #15803d;
    font-size: 1.3rem;
    margin-bottom: 15px;
    display: flex;
    align-items: center;
    gap: 10px;
}

.recommendation-box p {
    line-height: 1.8;
    font-size: 1rem;
    color: #1f2937;
}

.warning-box {
    background: linear-gradient(135deg, rgba(239, 68, 68, 0.1), rgba(220, 38, 38, 0.1));
    border: 2px solid #ef4444;
    border-left: 6px solid #ef4444;
    border-radius: 8px;
    padding: 20px;
    margin: 20px 0;
    color: #333;
}

.warning-box h4 {
    color: #991b1b;
    font-size: 1.3rem;
    margin-bottom: 15px;
    display: flex;
    align-items: center;
    gap: 10px;
}

.warning-box p {
    line-height: 1.8;
    font-size: 1rem;
    color: #1f2937;
}

/* Responsive */
@media (max-width: 1200px) {
    .main-grid {
        grid-template-columns: 1fr;
    }
}

@media (max-width: 768px) {
    body::before {
        background-attachment: scroll;
    }

    .mpt-navbar {
        flex-direction: column;
        gap: 15px;
        padding: 15px;
    }

    header h1 {
        font-size: 2rem;
    }

    .pipe-grid {
        grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
    }
}
    </style>
</head>
<body>
    <!-- MPT Navigation Bar -->
    <nav class="mpt-navbar">
        <div class="logo-container">
            <img src="/shared/assets/images/logo.png" alt="Municipal Pipe Tool">
            <span class="app-title">CIPP Production Estimator (Comprehensive)</span>
        </div>
        <a href="/" class="home-link">← Home</a>
    </nav>

    <div class="container">
        <header>
            <h1>🏗️ CIPP Production Estimator</h1>
            <p>Comprehensive fleet-based calculator with detailed penalty/boost analysis and dynamic recommendations</p>
        </header>

        <!-- Mode Selector -->
        <div class="mode-selector">
            <h2>📋 Select Estimation Mode</h2>
            <div class="mode-buttons">
                <div class="mode-btn" id="modePrepOnly" onclick="setMode('prep')">
                    <span class="mode-icon">🚿</span>
                    <div>CIPP Prep Only</div>
                    <div class="mode-description">Sewer Cleaning & CCTV Inspection</div>
                </div>
                <div class="mode-btn" id="modeLiningOnly" onclick="setMode('lining')">
                    <span class="mode-icon">🔧</span>
                    <div>CIPP Lining Only</div>
                    <div class="mode-description">Pipe Lining Installation & Curing</div>
                </div>
                <div class="mode-btn active" id="modeUnified" onclick="setMode('unified')">
                    <span class="mode-icon">🎯</span>
                    <div>Unified (Prep + Lining)</div>
                    <div class="mode-description">Complete CIPP Rehabilitation Project</div>
                </div>
            </div>
        </div>

        <div class="main-grid">
            <!-- PREP SECTION -->
            <div class="section" id="prepSection">
                <h2>🚿 CIPP PREP (Cleaning/CCTV)</h2>

                <div class="input-group">
                    <label for="prepFootage">Total Footage to Clean/TV:</label>
                    <input type="number" id="prepFootage" placeholder="198000" min="0">
                    <span class="unit">ft</span>
                </div>

                <div class="input-group">
                    <label for="prepBaseRate">Base Production Rate:</label>
                    <div class="slider-container">
                        <input type="range" id="prepBaseRateSlider" min="2000" max="5000" step="50" value="3100" class="slider">
                        <input type="number" id="prepBaseRate" min="2000" max="5000" step="50" value="3100" class="number-input">
                        <span class="unit">ft/day</span>
                    </div>
                    <small>Industry standard: 2000-5000 ft/day per crew</small>
                </div>

                <div class="input-group">
                    <label for="prepCrews">Number of Prep Crews:</label>
                    <input type="number" id="prepCrews" min="1" max="10" value="2">
                    <span class="unit">crews</span>
                </div>

                <h3>📏 Pipe Diameter Selection</h3>
                <div class="penalty-section">
                    <h5>⚠️ Select All Pipe Sizes Present in Project:</h5>
                    <small style="color: #666; display: block; margin-bottom: 10px;">Note: 6" pipe has HIGHEST penalty due to equipment access difficulty</small>
                    <div class="pipe-grid" id="prepPipeGrid"></div>
                </div>

                <h3>⚙️ PREP Penalties (User Adjustable)</h3>
                <div class="penalty-section">
                    <h5>🔧 Equipment & Access Penalties</h5>
                    <div class="penalty-grid">
                        <div class="penalty-item">
                            <label>
                                <span>Heavy Cleaning Required:</span>
                                <span class="penalty-value" id="prepHeavyPenaltyVal">0.40</span>
                            </label>
                            <div class="slider-container">
                                <input type="range" id="prepHeavyPenaltySlider" min="0" max="0.70" step="0.05" value="0.40" class="slider">
                                <input type="number" id="prepHeavyPenalty" min="0" max="0.70" step="0.05" value="0.40" class="number-input">
                            </div>
                        </div>
                        <div class="penalty-item">
                            <label>
                                <span>Easement/Off-Road Work:</span>
                                <span class="penalty-value" id="prepEasementPenaltyVal">0.30</span>
                            </label>
                            <div class="slider-container">
                                <input type="range" id="prepEasementPenaltySlider" min="0" max="0.60" step="0.05" value="0.30" class="slider">
                                <input type="number" id="prepEasementPenalty" min="0" max="0.60" step="0.05" value="0.30" class="number-input">
                            </div>
                        </div>
                        <div class="penalty-item">
                            <label>
                                <span>Root Intrusion Severity:</span>
                                <span class="penalty-value" id="prepRootPenaltyVal">0.35</span>
                            </label>
                            <div class="slider-container">
                                <input type="range" id="prepRootPenaltySlider" min="0" max="0.50" step="0.05" value="0.35" class="slider">
                                <input type="number" id="prepRootPenalty" min="0" max="0.50" step="0.05" value="0.35" class="number-input">
                            </div>
                        </div>
                        <div class="penalty-item">
                            <label>
                                <span>Deep Pipe Burial (> 12 ft):</span>
                                <span class="penalty-value" id="prepDepthPenaltyVal">0.20</span>
                            </label>
                            <div class="slider-container">
                                <input type="range" id="prepDepthPenaltySlider" min="0" max="0.40" step="0.05" value="0.20" class="slider">
                                <input type="number" id="prepDepthPenalty" min="0" max="0.40" step="0.05" value="0.20" class="number-input">
                            </div>
                        </div>
                        <div class="penalty-item">
                            <label>
                                <span>Traffic Control Required:</span>
                                <span class="penalty-value" id="prepTrafficPenaltyVal">0.25</span>
                            </label>
                            <div class="slider-container">
                                <input type="range" id="prepTrafficPenaltySlider" min="0" max="0.45" step="0.05" value="0.25" class="slider">
                                <input type="number" id="prepTrafficPenalty" min="0" max="0.45" step="0.05" value="0.25" class="number-input">
                            </div>
                        </div>
                        <div class="penalty-item">
                            <label>
                                <span>Heavy Grease/Sediment Buildup:</span>
                                <span class="penalty-value" id="prepGreasePenaltyVal">0.30</span>
                            </label>
                            <div class="slider-container">
                                <input type="range" id="prepGreasePenaltySlider" min="0" max="0.50" step="0.05" value="0.30" class="slider">
                                <input type="number" id="prepGreasePenalty" min="0" max="0.50" step="0.05" value="0.30" class="number-input">
                            </div>
                        </div>
                    </div>
                </div>

                <h3>⚡ PREP Boosts (User Adjustable)</h3>
                <div class="penalty-section">
                    <h5>🚀 Efficiency Boosts</h5>
                    <div class="penalty-grid">
                        <div class="penalty-item">
                            <label>
                                <span>Recycler Equipment Available:</span>
                                <span class="penalty-value" id="prepRecyclerBoostVal">0.25</span>
                            </label>
                            <div class="slider-container">
                                <input type="range" id="prepRecyclerBoostSlider" min="0" max="0.40" step="0.05" value="0.25" class="slider">
                                <input type="number" id="prepRecyclerBoost" min="0" max="0.40" step="0.05" value="0.25" class="number-input">
                            </div>
                        </div>
                        <div class="penalty-item">
                            <label>
                                <span>Clustered/Contiguous Segments:</span>
                                <span class="penalty-value" id="prepClusterBoostVal">0.15</span>
                            </label>
                            <div class="slider-container">
                                <input type="range" id="prepClusterBoostSlider" min="0" max="0.30" step="0.05" value="0.15" class="slider">
                                <input type="number" id="prepClusterBoost" min="0" max="0.30" step="0.05" value="0.15" class="number-input">
                            </div>
                        </div>
                        <div class="penalty-item">
                            <label>
                                <span>Pre-Inspection Completed:</span>
                                <span class="penalty-value" id="prepPreInspBoostVal">0.10</span>
                            </label>
                            <div class="slider-container">
                                <input type="range" id="prepPreInspBoostSlider" min="0" max="0.25" step="0.05" value="0.10" class="slider">
                                <input type="number" id="prepPreInspBoost" min="0" max="0.25" step="0.05" value="0.10" class="number-input">
                            </div>
                        </div>
                        <div class="penalty-item">
                            <label>
                                <span>Modern Equipment Fleet:</span>
                                <span class="penalty-value" id="prepModernEquipBoostVal">0.12</span>
                            </label>
                            <div class="slider-container">
                                <input type="range" id="prepModernEquipBoostSlider" min="0" max="0.25" step="0.05" value="0.12" class="slider">
                                <input type="number" id="prepModernEquipBoost" min="0" max="0.25" step="0.05" value="0.12" class="number-input">
                            </div>
                        </div>
                        <div class="penalty-item">
                            <label>
                                <span>Experienced Operators (3+ yrs):</span>
                                <span class="penalty-value" id="prepExpOpBoostVal">0.18</span>
                            </label>
                            <div class="slider-container">
                                <input type="range" id="prepExpOpBoostSlider" min="0" max="0.35" step="0.05" value="0.18" class="slider">
                                <input type="number" id="prepExpOpBoost" min="0" max="0.35" step="0.05" value="0.18" class="number-input">
                            </div>
                        </div>
                    </div>
                </div>

                <h3>📊 Project Constraints</h3>
                <div class="input-group">
                    <label for="prepTargetDays">Target Completion (days):</label>
                    <input type="number" id="prepTargetDays" placeholder="Optional" min="1">
                </div>

                <div class="input-group">
                    <label for="prepLaborBudget">Labor Hours Budgeted:</label>
                    <input type="number" id="prepLaborBudget" placeholder="Optional" min="0">
                </div>

                <div class="input-group">
                    <label for="prepLaborOverage">Labor Overage Tolerance:</label>
                    <div class="slider-container">
                        <input type="range" id="prepLaborOverageSlider" min="0" max="50" value="10" class="slider">
                        <input type="number" id="prepLaborOverage" min="0" max="50" value="10" class="number-input">
                        <span class="unit">%</span>
                    </div>
                </div>

                <div class="input-group">
                    <label for="prepHoursPerDay">Hours per Work Day:</label>
                    <input type="number" id="prepHoursPerDay" min="4" max="16" value="8" step="0.5">
                </div>

                <div class="input-group">
                    <label for="prepDaysPerWeek">Days per Work Week:</label>
                    <input type="number" id="prepDaysPerWeek" min="1" max="7" value="5">
                </div>

                <div class="input-group">
                    <label for="prepBudgetConstraint">Budget Constraint ($):</label>
                    <input type="number" id="prepBudgetConstraint" placeholder="Optional" min="0">
                    <small>Total project budget for prep work</small>
                </div>

                <div class="input-group">
                    <label for="prepMobilizationDays">Mobilization Days Allowed:</label>
                    <input type="number" id="prepMobilizationDays" min="0" max="30" value="2">
                    <small>Days allocated for equipment setup/teardown</small>
                </div>

                <div class="input-group">
                    <label for="prepEquipAvailability">Equipment Availability:</label>
                    <select id="prepEquipAvailability">
                        <option value="immediate">Immediate (owned equipment)</option>
                        <option value="1week">1 Week Lead Time</option>
                        <option value="2weeks">2 Weeks Lead Time</option>
                        <option value="1month">1 Month Lead Time</option>
                    </select>
                    <small>Affects project start date and mobilization planning</small>
                </div>
            </div>

            <!-- PREP RESULTS -->
            <div class="section" id="prepResults">
                <h2>📊 PREP Results & Recommendations</h2>

                <table>
                    <thead>
                        <tr>
                            <th>Metric</th>
                            <th>Value</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td>Effective Production Rate</td>
                            <td id="prepProdRate">-</td>
                        </tr>
                        <tr>
                            <td>Work Days Required</td>
                            <td id="prepWorkDays">-</td>
                        </tr>
                        <tr class="highlight-row">
                            <td><strong>Calendar Days</strong></td>
                            <td id="prepCalendarDays"><strong>-</strong></td>
                        </tr>
                        <tr>
                            <td>Labor Hours Estimated</td>
                            <td id="prepLaborHours">-</td>
                        </tr>
                    </tbody>
                </table>

                <div id="prepRecommendation"></div>
                <div id="prepWarning"></div>
            </div>
        </div>

        <div class="main-grid">
            <!-- LINING SECTION -->
            <div class="section hidden" id="liningSection">
                <h2>🔧 CIPP LINING Installation</h2>

                <div class="input-group">
                    <label for="liningFootage">Total Footage to Line:</label>
                    <input type="number" id="liningFootage" placeholder="198000" min="0">
                    <span class="unit">ft</span>
                </div>

                <div class="input-group">
                    <label for="liningBaseRate">Base Production Rate:</label>
                    <div class="slider-container">
                        <input type="range" id="liningBaseRateSlider" min="1500" max="4000" step="50" value="2500" class="slider">
                        <input type="number" id="liningBaseRate" min="1500" max="4000" step="50" value="2500" class="number-input">
                        <span class="unit">ft/week</span>
                    </div>
                    <small>Average: 2000-3000 ft/week per crew | Range: 300-5000 ft/week</small>
                </div>

                <div class="input-group">
                    <label for="liningCrews">Number of Lining Crews:</label>
                    <input type="number" id="liningCrews" min="1" max="10" value="3">
                    <span class="unit">crews</span>
                </div>

                <h3>📏 Pipe Diameter Selection</h3>
                <div class="penalty-section">
                    <h5>⚠️ Select All Pipe Sizes Present in Project:</h5>
                    <small style="color: #666; display: block; margin-bottom: 10px;">Note: 6" pipe has HIGH penalty - difficult liner installation and reinstatement</small>
                    <div class="pipe-grid" id="liningPipeGrid"></div>
                </div>

                <h3>⚙️ LINING Penalties (User Adjustable)</h3>
                <div class="penalty-section">
                    <h5>🌡️ Environmental & Condition Penalties</h5>
                    <div class="penalty-grid">
                        <div class="penalty-item">
                            <label>
                                <span>Cold Weather (< 50°F):</span>
                                <span class="penalty-value" id="liningColdPenaltyVal">0.30</span>
                            </label>
                            <div class="slider-container">
                                <input type="range" id="liningColdPenaltySlider" min="0" max="0.50" step="0.05" value="0.30" class="slider">
                                <input type="number" id="liningColdPenalty" min="0" max="0.50" step="0.05" value="0.30" class="number-input">
                            </div>
                        </div>
                        <div class="penalty-item">
                            <label>
                                <span>Hot Weather (> 85°F):</span>
                                <span class="penalty-value" id="liningHotPenaltyVal">0.20</span>
                            </label>
                            <div class="slider-container">
                                <input type="range" id="liningHotPenaltySlider" min="0" max="0.35" step="0.05" value="0.20" class="slider">
                                <input type="number" id="liningHotPenalty" min="0" max="0.35" step="0.05" value="0.20" class="number-input">
                            </div>
                        </div>
                        <div class="penalty-item">
                            <label>
                                <span>Host Pipe Deterioration:</span>
                                <span class="penalty-value" id="liningHostPipePenaltyVal">0.25</span>
                            </label>
                            <div class="slider-container">
                                <input type="range" id="liningHostPipePenaltySlider" min="0" max="0.45" step="0.05" value="0.25" class="slider">
                                <input type="number" id="liningHostPipePenalty" min="0" max="0.45" step="0.05" value="0.25" class="number-input">
                            </div>
                        </div>
                        <div class="penalty-item">
                            <label>
                                <span>Complex Bypass Requirements:</span>
                                <span class="penalty-value" id="liningBypassPenaltyVal">0.35</span>
                            </label>
                            <div class="slider-container">
                                <input type="range" id="liningBypassPenaltySlider" min="0" max="0.55" step="0.05" value="0.35" class="slider">
                                <input type="number" id="liningBypassPenalty" min="0" max="0.55" step="0.05" value="0.35" class="number-input">
                            </div>
                        </div>
                        <div class="penalty-item">
                            <label>
                                <span>High Lateral Count (> 10 per segment):</span>
                                <span class="penalty-value" id="liningLateralPenaltyVal">0.30</span>
                            </label>
                            <div class="slider-container">
                                <input type="range" id="liningLateralPenaltySlider" min="0" max="0.50" step="0.05" value="0.30" class="slider">
                                <input type="number" id="liningLateralPenalty" min="0" max="0.50" step="0.05" value="0.30" class="number-input">
                            </div>
                        </div>
                        <div class="penalty-item">
                            <label>
                                <span>Difficult Installation Access:</span>
                                <span class="penalty-value" id="liningAccessPenaltyVal">0.25</span>
                            </label>
                            <div class="slider-container">
                                <input type="range" id="liningAccessPenaltySlider" min="0" max="0.45" step="0.05" value="0.25" class="slider">
                                <input type="number" id="liningAccessPenalty" min="0" max="0.45" step="0.05" value="0.25" class="number-input">
                            </div>
                        </div>
                        <div class="penalty-item">
                            <label>
                                <span>Heavy Groundwater Infiltration:</span>
                                <span class="penalty-value" id="liningGroundwaterPenaltyVal">0.28</span>
                            </label>
                            <div class="slider-container">
                                <input type="range" id="liningGroundwaterPenaltySlider" min="0" max="0.50" step="0.05" value="0.28" class="slider">
                                <input type="number" id="liningGroundwaterPenalty" min="0" max="0.50" step="0.05" value="0.28" class="number-input">
                            </div>
                        </div>
                        <div class="penalty-item">
                            <label>
                                <span>New/Inexperienced Crew:</span>
                                <span class="penalty-value" id="liningNewCrewPenaltyVal">0.30</span>
                            </label>
                            <div class="slider-container">
                                <input type="range" id="liningNewCrewPenaltySlider" min="0" max="0.50" step="0.05" value="0.30" class="slider">
                                <input type="number" id="liningNewCrewPenalty" min="0" max="0.50" step="0.05" value="0.30" class="number-input">
                            </div>
                        </div>
                    </div>
                </div>

                <h3>⚡ LINING Boosts (User Adjustable)</h3>
                <div class="penalty-section">
                    <h5>🚀 Efficiency Boosts</h5>
                    <div class="penalty-grid">
                        <div class="penalty-item">
                            <label>
                                <span>Steam Curing Method:</span>
                                <span class="penalty-value" id="liningSteamBoostVal">0.15</span>
                            </label>
                            <div class="slider-container">
                                <input type="range" id="liningSteamBoostSlider" min="0" max="0.30" step="0.05" value="0.15" class="slider">
                                <input type="number" id="liningSteamBoost" min="0" max="0.30" step="0.05" value="0.15" class="number-input">
                            </div>
                        </div>
                        <div class="penalty-item">
                            <label>
                                <span>UV Light Curing Method:</span>
                                <span class="penalty-value" id="liningUVBoostVal">0.40</span>
                            </label>
                            <div class="slider-container">
                                <input type="range" id="liningUVBoostSlider" min="0" max="0.60" step="0.05" value="0.40" class="slider">
                                <input type="number" id="liningUVBoost" min="0" max="0.60" step="0.05" value="0.40" class="number-input">
                            </div>
                        </div>
                        <div class="penalty-item">
                            <label>
                                <span>Good Host Pipe Condition:</span>
                                <span class="penalty-value" id="liningGoodPipeBoostVal">0.18</span>
                            </label>
                            <div class="slider-container">
                                <input type="range" id="liningGoodPipeBoostSlider" min="0" max="0.35" step="0.05" value="0.18" class="slider">
                                <input type="number" id="liningGoodPipeBoost" min="0" max="0.35" step="0.05" value="0.18" class="number-input">
                            </div>
                        </div>
                        <div class="penalty-item">
                            <label>
                                <span>Minimal Laterals (< 5 per segment):</span>
                                <span class="penalty-value" id="liningMinLateralBoostVal">0.15</span>
                            </label>
                            <div class="slider-container">
                                <input type="range" id="liningMinLateralBoostSlider" min="0" max="0.30" step="0.05" value="0.15" class="slider">
                                <input type="number" id="liningMinLateralBoost" min="0" max="0.30" step="0.05" value="0.15" class="number-input">
                            </div>
                        </div>
                        <div class="penalty-item">
                            <label>
                                <span>Efficient Bypass Available:</span>
                                <span class="penalty-value" id="liningBypassBoostVal">0.20</span>
                            </label>
                            <div class="slider-container">
                                <input type="range" id="liningBypassBoostSlider" min="0" max="0.40" step="0.05" value="0.20" class="slider">
                                <input type="number" id="liningBypassBoost" min="0" max="0.40" step="0.05" value="0.20" class="number-input">
                            </div>
                        </div>
                        <div class="penalty-item">
                            <label>
                                <span>Experienced Lining Crew (3+ yrs):</span>
                                <span class="penalty-value" id="liningExpCrewBoostVal">0.22</span>
                            </label>
                            <div class="slider-container">
                                <input type="range" id="liningExpCrewBoostSlider" min="0" max="0.40" step="0.05" value="0.22" class="slider">
                                <input type="number" id="liningExpCrewBoost" min="0" max="0.40" step="0.05" value="0.22" class="number-input">
                            </div>
                        </div>
                        <div class="penalty-item">
                            <label>
                                <span>Optimal Weather Conditions:</span>
                                <span class="penalty-value" id="liningOptimalWeatherBoostVal">0.12</span>
                            </label>
                            <div class="slider-container">
                                <input type="range" id="liningOptimalWeatherBoostSlider" min="0" max="0.25" step="0.05" value="0.12" class="slider">
                                <input type="number" id="liningOptimalWeatherBoost" min="0" max="0.25" step="0.05" value="0.12" class="number-input">
                            </div>
                        </div>
                    </div>
                </div>

                <h3>📊 Project Constraints</h3>
                <div class="input-group">
                    <label for="liningTargetDays">Target Completion (days):</label>
                    <input type="number" id="liningTargetDays" placeholder="Optional" min="1">
                </div>

                <div class="input-group">
                    <label for="liningLaborBudget">Labor Hours Budgeted:</label>
                    <input type="number" id="liningLaborBudget" placeholder="Optional" min="0">
                </div>

                <div class="input-group">
                    <label for="liningLaborOverage">Labor Overage Tolerance:</label>
                    <div class="slider-container">
                        <input type="range" id="liningLaborOverageSlider" min="0" max="50" value="10" class="slider">
                        <input type="number" id="liningLaborOverage" min="0" max="50" value="10" class="number-input">
                        <span class="unit">%</span>
                    </div>
                </div>

                <div class="input-group">
                    <label for="liningHoursPerDay">Hours per Work Day:</label>
                    <input type="number" id="liningHoursPerDay" min="4" max="16" value="8" step="0.5">
                </div>

                <div class="input-group">
                    <label for="liningDaysPerWeek">Days per Work Week:</label>
                    <input type="number" id="liningDaysPerWeek" min="1" max="7" value="5">
                </div>

                <div class="input-group">
                    <label for="liningBudgetConstraint">Budget Constraint ($):</label>
                    <input type="number" id="liningBudgetConstraint" placeholder="Optional" min="0">
                    <small>Total project budget for lining work</small>
                </div>

                <div class="input-group">
                    <label for="liningMobilizationDays">Mobilization Days Allowed:</label>
                    <input type="number" id="liningMobilizationDays" min="0" max="30" value="3">
                    <small>Days allocated for equipment setup/teardown</small>
                </div>

                <div class="input-group">
                    <label for="liningEquipAvailability">Equipment Availability:</label>
                    <select id="liningEquipAvailability">
                        <option value="immediate">Immediate (owned equipment)</option>
                        <option value="1week">1 Week Lead Time</option>
                        <option value="2weeks">2 Weeks Lead Time</option>
                        <option value="1month">1 Month Lead Time</option>
                    </select>
                    <small>Affects project start date and mobilization planning</small>
                </div>
            </div>

            <!-- LINING RESULTS -->
            <div class="section hidden" id="liningResults">
                <h2>📊 LINING Results & Recommendations</h2>

                <table>
                    <thead>
                        <tr>
                            <th>Metric</th>
                            <th>Value</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td>Effective Production Rate</td>
                            <td id="liningProdRate">-</td>
                        </tr>
                        <tr>
                            <td>Weeks Required</td>
                            <td id="liningWeeks">-</td>
                        </tr>
                        <tr class="highlight-row">
                            <td><strong>Calendar Days</strong></td>
                            <td id="liningDays"><strong>-</strong></td>
                        </tr>
                        <tr>
                            <td>Labor Hours Estimated</td>
                            <td id="liningLaborHours">-</td>
                        </tr>
                    </tbody>
                </table>

                <div id="liningRecommendation"></div>
                <div id="liningWarning"></div>
            </div>
        </div>

        <!-- UNIFIED RESULTS -->
        <div class="section" id="unifiedResults" style="display: none;">
            <h2>🎯 Unified Project Timeline & Recommendations</h2>

            <table>
                <thead>
                    <tr>
                        <th>Phase</th>
                        <th>Duration</th>
                        <th>Production Rate</th>
                        <th>Labor Hours</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td><strong>Phase 1: CIPP Prep</strong></td>
                        <td id="unifiedPrepDays">-</td>
                        <td id="unifiedPrepRate">-</td>
                        <td id="unifiedPrepLabor">-</td>
                    </tr>
                    <tr>
                        <td><strong>Phase 2: CIPP Lining</strong></td>
                        <td id="unifiedLiningDays">-</td>
                        <td id="unifiedLiningRate">-</td>
                        <td id="unifiedLiningLabor">-</td>
                    </tr>
                    <tr class="highlight-row">
                        <td><strong>TOTAL PROJECT</strong></td>
                        <td id="unifiedTotalDays"><strong>-</strong></td>
                        <td colspan="2" id="unifiedTotalLabor"><strong>-</strong></td>
                    </tr>
                </tbody>
            </table>

            <div id="unifiedRecommendation"></div>
            <div id="unifiedWarning"></div>
        </div>
    </div>

    <script>
// ============================================================================
// COMPREHENSIVE CIPP ESTIMATOR - Full Implementation
// ============================================================================

let currentMode = 'unified';

// Pipe size definitions (COMPREHENSIVE)
const PREP_PIPE_SIZES = [
    { diameter: 6, penalty: 0.45, label: '6" (HIGHEST penalty - difficult access)' },
    { diameter: 8, penalty: 0.10, label: '8" (minor penalty)' },
    { diameter: 10, penalty: 0.05, label: '10" (minimal penalty)' },
    { diameter: 12, penalty: 0.00, label: '12" (baseline)' },
    { diameter: 15, penalty: 0.15, label: '15" (moderate penalty)' },
    { diameter: 18, penalty: 0.20, label: '18" (moderate penalty)' },
    { diameter: 21, penalty: 0.30, label: '21" (high penalty)' },
    { diameter: 24, penalty: 0.35, label: '24" (high penalty)' },
    { diameter: 27, penalty: 0.38, label: '27" (very high penalty)' },
    { diameter: 30, penalty: 0.40, label: '30" (very high penalty)' },
    { diameter: 36, penalty: 0.45, label: '36" (extreme penalty)' },
    { diameter: 42, penalty: 0.50, label: '42"+ (extreme penalty)' }
];

const LINING_PIPE_SIZES = [
    { diameter: 6, penalty: 0.40, label: '6" (HIGH penalty - liner installation difficult)' },
    { diameter: 8, penalty: 0.08, label: '8" (minor penalty)' },
    { diameter: 10, penalty: 0.05, label: '10" (minimal penalty)' },
    { diameter: 12, penalty: 0.00, label: '12" (baseline)' },
    { diameter: 15, penalty: 0.20, label: '15" (moderate penalty)' },
    { diameter: 18, penalty: 0.25, label: '18" (moderate penalty)' },
    { diameter: 21, penalty: 0.40, label: '21" (high penalty)' },
    { diameter: 24, penalty: 0.45, label: '24" (high penalty)' },
    { diameter: 27, penalty: 0.48, label: '27" (very high penalty)' },
    { diameter: 30, penalty: 0.50, label: '30" (very high penalty)' },
    { diameter: 36, penalty: 0.55, label: '36" (extreme penalty)' },
    { diameter: 42, penalty: 0.60, label: '42"+ (extreme penalty)' }
];

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    initializePipeGrids();
    syncAllSliders();
    setupCalculationTriggers();
    setMode('unified');
});

function initializePipeGrids() {
    const prepGrid = document.getElementById('prepPipeGrid');
    const liningGrid = document.getElementById('liningPipeGrid');

    PREP_PIPE_SIZES.forEach(pipe => {
        prepGrid.innerHTML += `
            <div class="pipe-checkbox">
                <input type="checkbox" id="prep_pipe_${pipe.diameter}" data-diameter="${pipe.diameter}" data-penalty="${pipe.penalty}">
                <label for="prep_pipe_${pipe.diameter}">${pipe.label}</label>
            </div>
        `;
    });

    LINING_PIPE_SIZES.forEach(pipe => {
        liningGrid.innerHTML += `
            <div class="pipe-checkbox">
                <input type="checkbox" id="lining_pipe_${pipe.diameter}" data-diameter="${pipe.diameter}" data-penalty="${pipe.penalty}">
                <label for="lining_pipe_${pipe.diameter}">${pipe.label}</label>
            </div>
        `;
    });
}

function syncAllSliders() {
    const sliderPairs = [
        ['prepBaseRateSlider', 'prepBaseRate'],
        ['prepHeavyPenaltySlider', 'prepHeavyPenalty'],
        ['prepEasementPenaltySlider', 'prepEasementPenalty'],
        ['prepRootPenaltySlider', 'prepRootPenalty'],
        ['prepDepthPenaltySlider', 'prepDepthPenalty'],
        ['prepTrafficPenaltySlider', 'prepTrafficPenalty'],
        ['prepGreasePenaltySlider', 'prepGreasePenalty'],
        ['prepRecyclerBoostSlider', 'prepRecyclerBoost'],
        ['prepClusterBoostSlider', 'prepClusterBoost'],
        ['prepPreInspBoostSlider', 'prepPreInspBoost'],
        ['prepModernEquipBoostSlider', 'prepModernEquipBoost'],
        ['prepExpOpBoostSlider', 'prepExpOpBoost'],
        ['prepLaborOverageSlider', 'prepLaborOverage'],
        ['liningBaseRateSlider', 'liningBaseRate'],
        ['liningColdPenaltySlider', 'liningColdPenalty'],
        ['liningHotPenaltySlider', 'liningHotPenalty'],
        ['liningHostPipePenaltySlider', 'liningHostPipePenalty'],
        ['liningBypassPenaltySlider', 'liningBypassPenalty'],
        ['liningLateralPenaltySlider', 'liningLateralPenalty'],
        ['liningAccessPenaltySlider', 'liningAccessPenalty'],
        ['liningGroundwaterPenaltySlider', 'liningGroundwaterPenalty'],
        ['liningNewCrewPenaltySlider', 'liningNewCrewPenalty'],
        ['liningSteamBoostSlider', 'liningSteamBoost'],
        ['liningUVBoostSlider', 'liningUVBoost'],
        ['liningGoodPipeBoostSlider', 'liningGoodPipeBoost'],
        ['liningMinLateralBoostSlider', 'liningMinLateralBoost'],
        ['liningBypassBoostSlider', 'liningBypassBoost'],
        ['liningExpCrewBoostSlider', 'liningExpCrewBoost'],
        ['liningOptimalWeatherBoostSlider', 'liningOptimalWeatherBoost'],
        ['liningLaborOverageSlider', 'liningLaborOverage']
    ];

    sliderPairs.forEach(([sliderId, inputId]) => {
        const slider = document.getElementById(sliderId);
        const input = document.getElementById(inputId);
        const valDisplay = document.getElementById(inputId + 'Val');

        if (slider && input) {
            slider.addEventListener('input', () => {
                input.value = slider.value;
                if (valDisplay) valDisplay.textContent = slider.value;
                calculate();
            });

            input.addEventListener('input', () => {
                slider.value = input.value;
                if (valDisplay) valDisplay.textContent = input.value;
                calculate();
            });
        }
    });
}

function setupCalculationTriggers() {
    document.querySelectorAll('input, select').forEach(el => {
        if (!el.id.includes('Slider')) {
            el.addEventListener('change', calculate);
            el.addEventListener('input', calculate);
        }
    });
}

function setMode(mode) {
    currentMode = mode;

    // Update buttons
    document.querySelectorAll('.mode-btn').forEach(btn => btn.classList.remove('active'));
    if (mode === 'prep') {
        document.getElementById('modePrepOnly').classList.add('active');
        document.getElementById('prepSection').classList.remove('hidden');
        document.getElementById('prepResults').classList.remove('hidden');
        document.getElementById('liningSection').classList.add('hidden');
        document.getElementById('liningResults').classList.add('hidden');
        document.getElementById('unifiedResults').style.display = 'none';
    } else if (mode === 'lining') {
        document.getElementById('modeLiningOnly').classList.add('active');
        document.getElementById('prepSection').classList.add('hidden');
        document.getElementById('prepResults').classList.add('hidden');
        document.getElementById('liningSection').classList.remove('hidden');
        document.getElementById('liningResults').classList.remove('hidden');
        document.getElementById('unifiedResults').style.display = 'none';
    } else {
        document.getElementById('modeUnified').classList.add('active');
        document.getElementById('prepSection').classList.remove('hidden');
        document.getElementById('prepResults').classList.remove('hidden');
        document.getElementById('liningSection').classList.remove('hidden');
        document.getElementById('liningResults').classList.remove('hidden');
        document.getElementById('unifiedResults').style.display = 'block';
    }

    calculate();
}

function calculate() {
    if (currentMode === 'prep' || currentMode === 'unified') calculatePrep();
    if (currentMode === 'lining' || currentMode === 'unified') calculateLining();
    if (currentMode === 'unified') calculateUnified();
}

function calculatePrep() {
    const footage = parseFloat(document.getElementById('prepFootage').value) || 0;
    if (footage === 0) {
        document.getElementById('prepProdRate').textContent = '-';
        document.getElementById('prepWorkDays').textContent = '-';
        document.getElementById('prepCalendarDays').textContent = '-';
        document.getElementById('prepLaborHours').textContent = '-';
        document.getElementById('prepRecommendation').innerHTML = '';
        document.getElementById('prepWarning').innerHTML = '';
        return;
    }

    const baseRate = parseFloat(document.getElementById('prepBaseRate').value) || 3100;
    const crews = parseFloat(document.getElementById('prepCrews').value) || 2;

    // Get penalties
    const heavyPenalty = parseFloat(document.getElementById('prepHeavyPenalty').value) || 0;
    const easementPenalty = parseFloat(document.getElementById('prepEasementPenalty').value) || 0;
    const rootPenalty = parseFloat(document.getElementById('prepRootPenalty').value) || 0;
    const depthPenalty = parseFloat(document.getElementById('prepDepthPenalty').value) || 0;
    const trafficPenalty = parseFloat(document.getElementById('prepTrafficPenalty').value) || 0;
    const greasePenalty = parseFloat(document.getElementById('prepGreasePenalty').value) || 0;

    // Get boosts
    const recyclerBoost = parseFloat(document.getElementById('prepRecyclerBoost').value) || 0;
    const clusterBoost = parseFloat(document.getElementById('prepClusterBoost').value) || 0;
    const preInspBoost = parseFloat(document.getElementById('prepPreInspBoost').value) || 0;
    const modernEquipBoost = parseFloat(document.getElementById('prepModernEquipBoost').value) || 0;
    const expOpBoost = parseFloat(document.getElementById('prepExpOpBoost').value) || 0;

    // Get pipe penalties
    let pipePenalty = 0;
    document.querySelectorAll('[id^="prep_pipe_"]:checked').forEach(checkbox => {
        pipePenalty = Math.max(pipePenalty, parseFloat(checkbox.dataset.penalty));
    });

    // Calculate effective rate
    let rate = baseRate;

    // Apply penalties (multiplicative)
    rate *= (1 - heavyPenalty);
    rate *= (1 - easementPenalty);
    rate *= (1 - rootPenalty);
    rate *= (1 - depthPenalty);
    rate *= (1 - trafficPenalty);
    rate *= (1 - greasePenalty);
    rate *= (1 - pipePenalty);

    // Apply boosts (additive)
    const totalBoost = recyclerBoost + clusterBoost + preInspBoost + modernEquipBoost + expOpBoost;
    rate *= (1 + totalBoost);

    // Apply crew multiplier
    rate *= crews;

    const workDays = Math.ceil(footage / rate);
    const daysPerWeek = parseFloat(document.getElementById('prepDaysPerWeek').value) || 5;
    const calendarDays = Math.ceil(workDays * 7 / daysPerWeek);
    const hoursPerDay = parseFloat(document.getElementById('prepHoursPerDay').value) || 8;
    const laborHours = workDays * hoursPerDay * crews;

    // Display results
    document.getElementById('prepProdRate').textContent = `${Math.round(rate).toLocaleString()} ft/day`;
    document.getElementById('prepWorkDays').textContent = `${workDays} work days`;
    document.getElementById('prepCalendarDays').textContent = `${calendarDays} calendar days`;
    document.getElementById('prepLaborHours').textContent = `${Math.round(laborHours).toLocaleString()} hours`;

    // Generate recommendations
    generatePrepRecommendations(workDays, calendarDays, laborHours, crews, hoursPerDay, daysPerWeek);
}

function calculateLining() {
    const footage = parseFloat(document.getElementById('liningFootage').value) || 0;
    if (footage === 0) {
        document.getElementById('liningProdRate').textContent = '-';
        document.getElementById('liningWeeks').textContent = '-';
        document.getElementById('liningDays').textContent = '-';
        document.getElementById('liningLaborHours').textContent = '-';
        document.getElementById('liningRecommendation').innerHTML = '';
        document.getElementById('liningWarning').innerHTML = '';
        return;
    }

    const baseRatePerWeek = parseFloat(document.getElementById('liningBaseRate').value) || 2500;
    const crews = parseFloat(document.getElementById('liningCrews').value) || 3;

    // Get all penalties
    const coldPenalty = parseFloat(document.getElementById('liningColdPenalty').value) || 0;
    const hotPenalty = parseFloat(document.getElementById('liningHotPenalty').value) || 0;
    const hostPipePenalty = parseFloat(document.getElementById('liningHostPipePenalty').value) || 0;
    const bypassPenalty = parseFloat(document.getElementById('liningBypassPenalty').value) || 0;
    const lateralPenalty = parseFloat(document.getElementById('liningLateralPenalty').value) || 0;
    const accessPenalty = parseFloat(document.getElementById('liningAccessPenalty').value) || 0;
    const groundwaterPenalty = parseFloat(document.getElementById('liningGroundwaterPenalty').value) || 0;
    const newCrewPenalty = parseFloat(document.getElementById('liningNewCrewPenalty').value) || 0;

    // Get all boosts
    const steamBoost = parseFloat(document.getElementById('liningSteamBoost').value) || 0;
    const uvBoost = parseFloat(document.getElementById('liningUVBoost').value) || 0;
    const goodPipeBoost = parseFloat(document.getElementById('liningGoodPipeBoost').value) || 0;
    const minLateralBoost = parseFloat(document.getElementById('liningMinLateralBoost').value) || 0;
    const bypassBoost = parseFloat(document.getElementById('liningBypassBoost').value) || 0;
    const expCrewBoost = parseFloat(document.getElementById('liningExpCrewBoost').value) || 0;
    const optimalWeatherBoost = parseFloat(document.getElementById('liningOptimalWeatherBoost').value) || 0;

    // Get pipe penalties
    let pipePenalty = 0;
    document.querySelectorAll('[id^="lining_pipe_"]:checked').forEach(checkbox => {
        pipePenalty = Math.max(pipePenalty, parseFloat(checkbox.dataset.penalty));
    });

    // Calculate effective rate
    let rate = baseRatePerWeek;

    // Apply penalties (multiplicative)
    rate *= (1 - coldPenalty);
    rate *= (1 - hotPenalty);
    rate *= (1 - hostPipePenalty);
    rate *= (1 - bypassPenalty);
    rate *= (1 - lateralPenalty);
    rate *= (1 - accessPenalty);
    rate *= (1 - groundwaterPenalty);
    rate *= (1 - newCrewPenalty);
    rate *= (1 - pipePenalty);

    // Apply boosts (additive)
    const totalBoost = steamBoost + uvBoost + goodPipeBoost + minLateralBoost + bypassBoost + expCrewBoost + optimalWeatherBoost;
    rate *= (1 + totalBoost);

    // Apply crew multiplier
    rate *= crews;

    const weeks = Math.ceil(footage / rate);
    const days = weeks * 7;
    const hoursPerDay = parseFloat(document.getElementById('liningHoursPerDay').value) || 8;
    const daysPerWeek = parseFloat(document.getElementById('liningDaysPerWeek').value) || 5;
    const workDays = Math.ceil(days * daysPerWeek / 7);
    const laborHours = workDays * hoursPerDay * crews;

    // Display results
    document.getElementById('liningProdRate').textContent = `${Math.round(rate).toLocaleString()} ft/week`;
    document.getElementById('liningWeeks').textContent = `${weeks} weeks`;
    document.getElementById('liningDays').textContent = `${days} days`;
    document.getElementById('liningLaborHours').textContent = `${Math.round(laborHours).toLocaleString()} hours`;

    // Generate recommendations
    generateLiningRecommendations(weeks, days, laborHours, crews, hoursPerDay, daysPerWeek);
}

function calculateUnified() {
    const prepFootage = parseFloat(document.getElementById('prepFootage').value) || 0;
    const liningFootage = parseFloat(document.getElementById('liningFootage').value) || 0;

    if (prepFootage === 0 || liningFootage === 0) {
        document.getElementById('unifiedRecommendation').innerHTML = '';
        return;
    }

    const prepDays = parseInt(document.getElementById('prepCalendarDays').textContent) || 0;
    const liningDays = parseInt(document.getElementById('liningDays').textContent) || 0;
    const prepLabor = parseInt(document.getElementById('prepLaborHours').textContent.replace(/,/g, '')) || 0;
    const liningLabor = parseInt(document.getElementById('liningLaborHours').textContent.replace(/,/g, '')) || 0;

    const totalDays = prepDays + liningDays;
    const totalLabor = prepLabor + liningLabor;

    document.getElementById('unifiedPrepDays').textContent = `${prepDays} days`;
    document.getElementById('unifiedPrepRate').textContent = document.getElementById('prepProdRate').textContent;
    document.getElementById('unifiedPrepLabor').textContent = `${prepLabor.toLocaleString()} hrs`;
    document.getElementById('unifiedLiningDays').textContent = `${liningDays} days`;
    document.getElementById('unifiedLiningRate').textContent = document.getElementById('liningProdRate').textContent;
    document.getElementById('unifiedLiningLabor').textContent = `${liningLabor.toLocaleString()} hrs`;
    document.getElementById('unifiedTotalDays').textContent = `${totalDays} days (${Math.ceil(totalDays / 7)} weeks)`;
    document.getElementById('unifiedTotalLabor').textContent = `Total Labor: ${totalLabor.toLocaleString()} hours`;

    generateUnifiedRecommendations(prepDays, liningDays, totalDays, totalLabor);
}

function generatePrepRecommendations(workDays, calendarDays, laborHours, crews, hoursPerDay, daysPerWeek) {
    const targetDays = parseFloat(document.getElementById('prepTargetDays').value) || 0;
    const laborBudget = parseFloat(document.getElementById('prepLaborBudget').value) || 0;
    const laborOverage = parseFloat(document.getElementById('prepLaborOverage').value) || 10;
    const maxLaborAllowed = laborBudget * (1 + laborOverage / 100);

    let recommendations = [];
    let warnings = [];

    if (targetDays && calendarDays > targetDays) {
        const overrun = calendarDays - targetDays;
        const ratio = calendarDays / targetDays;
        const neededCrews = Math.ceil(crews * ratio);
        const neededHours = Math.min(16, Math.ceil(hoursPerDay * ratio));
        const neededDaysPerWeek = Math.min(7, Math.ceil(daysPerWeek * ratio));

        recommendations.push(`Schedule overrun: ${overrun} days beyond ${targetDays}-day target. Recommend adding ${neededCrews - crews} crew(s) (total: ${neededCrews}), increasing to ${neededHours} hrs/day, or working ${neededDaysPerWeek} days/week to meet deadline. Adjust penalty sliders if conditions improve or enable available boosts.`);
    }

    if (laborBudget && laborHours > maxLaborAllowed) {
        const overrun = Math.round(laborHours - maxLaborAllowed);
        warnings.push(`Labor hours exceed budget by ${overrun} hrs. Consider reducing crew count to ${Math.max(1, crews - 1)} (extends timeline), limiting overtime, or negotiating ${Math.ceil((laborHours / laborBudget - 1) * 100)}% overage allowance.`);
    }

    if (!targetDays && !laborBudget) {
        recommendations.push(`Project estimated at ${calendarDays} calendar days with ${crews} crew(s) at ${hoursPerDay} hrs/day. Consider utilizing available efficiency boosts (recycler, modern equipment, experienced operators) to reduce timeline. Adjust penalty sliders based on actual site conditions for more accurate estimates.`);
    }

    const recBox = document.getElementById('prepRecommendation');
    const warnBox = document.getElementById('prepWarning');

    if (recommendations.length > 0) {
        recBox.innerHTML = `<div class="recommendation-box"><h4>💡 Recommendations</h4><p>${recommendations.join(' ')}</p></div>`;
    } else {
        recBox.innerHTML = '';
    }

    if (warnings.length > 0) {
        warnBox.innerHTML = `<div class="warning-box"><h4>⚠️ Warnings</h4><p>${warnings.join(' ')}</p></div>`;
    } else {
        warnBox.innerHTML = '';
    }
}

function generateLiningRecommendations(weeks, days, laborHours, crews, hoursPerDay, daysPerWeek) {
    const targetDays = parseFloat(document.getElementById('liningTargetDays').value) || 0;
    const laborBudget = parseFloat(document.getElementById('liningLaborBudget').value) || 0;
    const laborOverage = parseFloat(document.getElementById('liningLaborOverage').value) || 10;
    const maxLaborAllowed = laborBudget * (1 + laborOverage / 100);

    let recommendations = [];
    let warnings = [];

    if (targetDays && days > targetDays) {
        const overrun = days - targetDays;
        const ratio = days / targetDays;
        const neededCrews = Math.ceil(crews * ratio);

        recommendations.push(`Lining phase exceeds target by ${overrun} days. Recommend deploying ${neededCrews - crews} additional crew(s) (total: ${neededCrews}), utilizing UV curing (+40% boost), or improving host pipe prep. Consider enabling efficiency boosts like minimal laterals or experienced crew factors.`);
    }

    if (laborBudget && laborHours > maxLaborAllowed) {
        const overrun = Math.round(laborHours - maxLaborAllowed);
        warnings.push(`Labor budget exceeded by ${overrun} hrs. Optimize by reducing crew count to ${Math.max(1, crews - 1)}, extending work schedule, or negotiating ${Math.ceil((laborHours / laborBudget - 1) * 100)}% budget increase. Review applied penalties for accuracy.`);
    }

    if (!targetDays && !laborBudget) {
        recommendations.push(`Lining estimated at ${weeks} weeks (${days} days) with ${crews} crew(s). Maximize efficiency with UV curing (+40%), experienced crews (+22%), and optimal weather conditions (+12%). Minimize delays by ensuring good bypass availability (+20%) and reducing lateral reinstatement count.`);
    }

    const recBox = document.getElementById('liningRecommendation');
    const warnBox = document.getElementById('liningWarning');

    if (recommendations.length > 0) {
        recBox.innerHTML = `<div class="recommendation-box"><h4>💡 Recommendations</h4><p>${recommendations.join(' ')}</p></div>`;
    } else {
        recBox.innerHTML = '';
    }

    if (warnings.length > 0) {
        warnBox.innerHTML = `<div class="warning-box"><h4>⚠️ Warnings</h4><p>${warnings.join(' ')}</p></div>`;
    } else {
        warnBox.innerHTML = '';
    }
}

function generateUnifiedRecommendations(prepDays, liningDays, totalDays, totalLabor) {
    const prepTarget = parseFloat(document.getElementById('prepTargetDays').value) || 0;
    const liningTarget = parseFloat(document.getElementById('liningTargetDays').value) || 0;
    const combinedTarget = prepTarget + liningTarget;

    let recommendations = [];
    let warnings = [];

    if (combinedTarget && totalDays > combinedTarget) {
        const overrun = totalDays - combinedTarget;
        recommendations.push(`Unified project runs ${overrun} days over combined target (${combinedTarget} days). Prep phase: ${prepDays} days, Lining phase: ${liningDays} days. Critical path optimization: accelerate prep completion to enable earlier lining start. Deploy additional crews to both phases or extend work schedules. Consider UV curing in lining phase for significant time savings.`);
    } else {
        recommendations.push(`Comprehensive rehabilitation timeline: ${totalDays} days total (${Math.ceil(totalDays / 7)} weeks). Sequential workflow ensures quality: complete prep phase (${prepDays} days) before lining installation (${liningDays} days). Total labor investment: ${totalLabor.toLocaleString()} hours. Optimize both phases independently using penalty/boost adjustments for most accurate project forecasting.`);
    }

    const recBox = document.getElementById('unifiedRecommendation');
    recBox.innerHTML = `<div class="recommendation-box"><h4>🎯 Unified Project Strategy</h4><p>${recommendations.join(' ')}</p></div>`;

    if (warnings.length > 0) {
        const warnBox = document.getElementById('unifiedWarning');
        warnBox.innerHTML = `<div class="warning-box"><h4>⚠️ Project Warnings</h4><p>${warnings.join(' ')}</p></div>`;
    }
}
    </script>
</body>
</html>
```

---

**End of Source Code**

**File Information**:
- Original Location: `legacy/apps/progress-estimator/CIPPEstimator_Comprehensive.html`
- Served by Flask Route: `/progress-estimator` (app.py line 440-443)
- Total Lines: 1,583
- CSS: Lines 7-510 (embedded)
- HTML: Lines 512-1124
- JavaScript: Lines 1125-1582
- Self-contained: No external dependencies except shared images

**Usage**: This file is served as-is by Flask. All calculations happen client-side in the browser.
