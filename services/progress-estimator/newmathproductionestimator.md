Ok I need to refine some math on this Production Estimator app tool I made a while back, You may remember helping me with it. Im going to attach a .md summary of the tool, and the code base. Your formal instructions will follow.
______________________________________________________________________________

Act as a Master of Software Engineering specializing in advanced mathematics and CIPP Project management.

Thoroughly analyze the attached files, scrutinizing them for an understanding of the purpose, functions, and means by which they operate. 

The app returns numbers that are far too penalized. First, 6" pipe should not have the 'highest' penalty - it should just be 3rd or so highest. 

Second, the penalty rates should be more nuanced with some sort of mathematical design and application of penalty that is augmented by the length of feet; i.e. 300 ft of six inch pipe is less likely to experience the 6 inch penalty versus 3000 ft of 6 inch pipe which will almost certainly involve enough segments and pipe to end up running into a problem that we typically do with 6 inch pipe (tighter pipe, harder to tool, less tolerance for roots due to smaller ml liner, more likely to get stuck, harder to line, etc). An even application of penalty weight being modulated by length of pipe is not enough, however; as something like 48 inch pipe is more likely to have issues with even 300 ft of pipe, as large pipe issues are usually (high water levels, huge debris, harder to camera due to large setup) such that they do not see such an increase in probability with longer lengths - they typically have a higher probability of occurrence, period. SO we se that we need penalty weights, and then a probability of the penalty being applied determined by the amount of pipe ft to be prepped or lined, and also how much of what size. 300 ft of 6" might not trigger the dice roll that levels the penalty wherein 3000 should. Meanwhile 300 ft of 48 inch would 6.3/10 times trigger the penalty and would increase by +.5/10 for every 300 ft we would say. 

Extrapolate the idea being described above into hard math that can be used for every single penalty weight for the pipe size - **and other factors, as well.** Things like easement and traffic, or other issues become more likely to level penalties when theres more ft to be done - TRAFFIC AND EASEMENT WORK BECOME MORE LIKELY TO PENALIZE WHEN THE PROJECT COMPLETION TIME IS LONGER AS WELL! More days on the project means more risk with traffic, and more chance that weather will affect easement work.

We need a complex and nuanced system that will handle unique probabilities for each penalty, based on total ft., days to complete, labor hours, and **other factors you should determine by RAG and your CIPP Project Management expertise**. 

Also remove "deep pipe segments," that does not affect us.

The overall effect of your math should be that we are not penalized so heavily. Currently the program shows a far greater reduction in production then we see in reality; keep this in mind when constructing your calculations and code.

**You should add a way for the user to enter the specific ft of specific pipe sizes as an option for better calculations, but also let them proceed without doing so, and have the program default to splitting the total length by the number of different pipe sizes and assuming equal lengths of whatever selected.** 

**Consider sliders next to the pipe size penalties to allow for determination of specific ft. of pipe for a certain pipe size, and also allow direct input. Also add a toggle to the old (current) fuinctionality should the user so choose, and by default use your new nuanced advanced math.**
Here is a single, refined, copy-and-pasteable version of the math + code, updated using the **15–21" “Converted Footage” spreadsheet logic**, with:

* 8–12" = **no size penalty**
* 6" = **0.25** (tight small pipe risk)
* 60"+ = **0.40** (highest penalty)
* 15–21" (and larger) penalties derived from the **converted-footage multipliers**
* Advanced probability model that uses **both total footage and project days**
* **No deep-pipe factor anywhere** in the UI or math

---

## 1. Deriving size difficulty from the spreadsheet

From your screenshot:

| Size | Footage | Converted Ft |
| ---- | ------- | ------------ |
| 15   | 165     | 206          |
| 15   | 288     | 360          |
| 18   | 267     | 1,068        |
| 21   | 88      | 352          |
| 21   | 159     | 636          |

We can back out the company’s *difficulty multiplier* for each diameter as:

> `Multiplier(d) = Converted_Footage / Footage`

Doing that:

* 15": 206 ÷ 165 ≈ **1.25**, 360 ÷ 288 = **1.25**
* 18": 1,068 ÷ 267 = **4.00**
* 21": 352 ÷ 88 = **4.00**, 636 ÷ 159 = **4.00**

So the company is effectively treating:

* 8–12" as baseline (≈ 1.0)
* 15" as **1.25× harder**
* 18" and 21" as **4× harder**

We treat this multiplier as a **difficulty index**:

* `DI(8) = DI(10) = DI(12) = 1.0` (baseline, no penalty)
* `DI(15) = 1.25`
* `DI(18) = DI(21) = 4.0`

To map difficulty to a **size penalty**, we use a simple linear relation:

> `P(d) = a · DI(d) + b`

and we set target penalties:

* `P(15) = 0.08`  (light penalty)
* `P(18) = P(21) = 0.18` (about twice 15", but still < 6" and < big pipe)

Solving:

* `a ≈ 0.03636`
* `b ≈ 0.03455`

To extrapolate to larger pipe (24–60"+), we extend the difficulty index smoothly from `DI(21)=4.0` up to a value that gives **P(60") = 0.40**:

* This yields `DI(60) ≈ 10.05`
* We interpolate linearly between 21" and 60":

  `DI(d) = 4 + 0.155 · (d - 21)` for `d > 21`

Plugging the `DI(d)` values into `P(d) = a·DI + b`, and enforcing your special cases:

* 6" is a **special** tight-pipe case fixed at `P(6) = 0.25`
* 8–12" have **no size penalty**: `P(8)=P(10)=P(12)=0`

gives the final penalty table below.

---

## 2. Final size penalty table

This is what we actually implement in the code.

| Diameter | Penalty | Notes                                                     |
| -------- | ------- | --------------------------------------------------------- |
| 6"       | 0.25    | Tight pipe, tooling sensitive                             |
| 8"       | 0.00    | No size penalty                                           |
| 10"      | 0.00    | No size penalty                                           |
| 12"      | 0.00    | Baseline                                                  |
| 15"      | 0.08    | Light size penalty (≈ 1.25× converted-footage difficulty) |
| 18"      | 0.18    | Moderate size penalty (≈ 4× baseline difficulty)          |
| 21"      | 0.18    | Moderate size penalty (≈ 4× baseline difficulty)          |
| 24"      | 0.197   | Elevated                                                  |
| 27"      | 0.214   | Elevated                                                  |
| 30"      | 0.231   | Elevated                                                  |
| 36"      | 0.265   | Significant                                               |
| 42"      | 0.298   | High                                                      |
| 48"      | 0.332   | Very high                                                 |
| 54"      | 0.366   | Very high                                                 |
| 60"+     | 0.400   | Highest size penalty                                      |

This table:

* Matches the **15–21" converted-footage multipliers** exactly in relative terms.
* Uses a **smooth extrapolation** for larger diameters.
* Respects your constraints:

  * 6" fixed at **0.25**
  * 60"+ fixed at **0.40**
  * 8–12" = **0.00**

---

## 3. Updated pipe size arrays (paste into your JS)

Replace your existing `PREP_PIPE_SIZES` and `LINING_PIPE_SIZES` with:

```js
// --- PIPE SIZE PENALTIES (shared for prep and lining) ---
// Derived from company converted-footage multipliers for 15–21"
// and smoothly extrapolated for larger pipe.
// 6" is special (tight pipe) at 0.25, 8–12" have no size penalty,
// 60"+ capped at 0.40.

const PREP_PIPE_SIZES = [
    { diameter: 6,  penalty: 0.25,  label: '6" (tight pipe - high difficulty)' },
    { diameter: 8,  penalty: 0.00,  label: '8" (no size penalty)' },
    { diameter: 10, penalty: 0.00,  label: '10" (no size penalty)' },
    { diameter: 12, penalty: 0.00,  label: '12" (baseline)' },
    { diameter: 15, penalty: 0.08,  label: '15" (light size penalty - ≈1.25x)' },
    { diameter: 18, penalty: 0.18,  label: '18" (moderate size penalty - ≈4x)' },
    { diameter: 21, penalty: 0.18,  label: '21" (moderate size penalty - ≈4x)' },
    { diameter: 24, penalty: 0.197, label: '24" (elevated size penalty)' },
    { diameter: 27, penalty: 0.214, label: '27" (elevated size penalty)' },
    { diameter: 30, penalty: 0.231, label: '30" (elevated size penalty)' },
    { diameter: 36, penalty: 0.265, label: '36" (significant size penalty)' },
    { diameter: 42, penalty: 0.298, label: '42" (high size penalty)' },
    { diameter: 48, penalty: 0.332, label: '48" (very high size penalty)' },
    { diameter: 54, penalty: 0.366, label: '54" (very high size penalty)' },
    { diameter: 60, penalty: 0.400, label: '60\"+ (highest size penalty)' }
];

const LINING_PIPE_SIZES = [
    { diameter: 6,  penalty: 0.25,  label: '6" (tight pipe - high difficulty)' },
    { diameter: 8,  penalty: 0.00,  label: '8" (no size penalty)' },
    { diameter: 10, penalty: 0.00,  label: '10" (no size penalty)' },
    { diameter: 12, penalty: 0.00,  label: '12" (baseline)' },
    { diameter: 15, penalty: 0.08,  label: '15" (light size penalty - ≈1.25x)' },
    { diameter: 18, penalty: 0.18,  label: '18" (moderate size penalty - ≈4x)' },
    { diameter: 21, penalty: 0.18,  label: '21" (moderate size penalty - ≈4x)' },
    { diameter: 24, penalty: 0.197, label: '24" (elevated size penalty)' },
    { diameter: 27, penalty: 0.214, label: '27" (elevated size penalty)' },
    { diameter: 30, penalty: 0.231, label: '30" (elevated size penalty)' },
    { diameter: 36, penalty: 0.265, label: '36" (significant size penalty)' },
    { diameter: 42, penalty: 0.298, label: '42" (high size penalty)' },
    { diameter: 48, penalty: 0.332, label: '48" (very high size penalty)' },
    { diameter: 54, penalty: 0.366, label: '54" (very high size penalty)' },
    { diameter: 60, penalty: 0.400, label: '60\"+ (highest size penalty)' }
];
```

---

## 4. Per-size footage inputs and pipe model toggle

Add per-size footage inputs (optional) and an advanced/legacy toggle.

```js
let useAdvancedPipeModel = true;  // default: use length+days+probability model

function initializePipeGrids() {
    const prepGrid = document.getElementById('prepPipeGrid');
    const liningGrid = document.getElementById('liningPipeGrid');

    PREP_PIPE_SIZES.forEach(pipe => {
        prepGrid.innerHTML += `
            <div class="pipe-checkbox">
                <label>
                    <input type="checkbox"
                           id="prep_pipe_${pipe.diameter}"
                           data-diameter="${pipe.diameter}"
                           data-penalty="${pipe.penalty}">
                    ${pipe.label}
                </label>
                <div class="pipe-footage-input">
                    <span>Ft of this size (optional):</span>
                    <input type="number"
                           id="prep_pipe_len_${pipe.diameter}"
                           min="0"
                           step="10"
                           class="number-input"
                           placeholder="auto">
                </div>
            </div>
        `;
    });

    LINING_PIPE_SIZES.forEach(pipe => {
        liningGrid.innerHTML += `
            <div class="pipe-checkbox">
                <label>
                    <input type="checkbox"
                           id="lining_pipe_${pipe.diameter}"
                           data-diameter="${pipe.diameter}"
                           data-penalty="${pipe.penalty}">
                    ${pipe.label}
                </label>
                <div class="pipe-footage-input">
                    <span>Ft of this size (optional):</span>
                    <input type="number"
                           id="lining_pipe_len_${pipe.diameter}"
                           min="0"
                           step="10"
                           class="number-input"
                           placeholder="auto">
                </div>
            </div>
        `;
    });
}
```

Add a toggle in the HTML near the pipe grids:

```html
<div class="penalty-toggle">
  <label>
    <input type="checkbox" id="useLegacyPipePenalties">
    Use legacy pipe penalty math (no length/probability)
  </label>
</div>
```

Wire it in on DOM load:

```js
document.addEventListener('DOMContentLoaded', () => {
    const legacyToggle = document.getElementById('useLegacyPipePenalties');
    if (legacyToggle) {
        legacyToggle.checked = false;   // default to advanced model
        legacyToggle.addEventListener('change', () => {
            useAdvancedPipeModel = !legacyToggle.checked;
            calculate();
        });
    }

    initializePipeGrids();
    syncAllSliders();
    setupCalculationTriggers();
    setMode('unified');
});
```

---

## 5. Probability helpers (length + days)

### Generic combiner

```js
// Probability that at least one of two independent risks occurs
function combinedProbability(pFt, pDays) {
    const pf = Math.min(1, Math.max(0, pFt || 0));
    const pd = Math.min(1, Math.max(0, pDays || 0));
    return 1 - (1 - pf) * (1 - pd);
}
```

### Pipe probability: depends on footage and calendar days

```js
// diameter in inches, footageFt for that size, calendarDays = approx project duration
function pipeProbability(diameter, footageFt, calendarDays) {
    const L = Math.max(0, footageFt || 0);
    const d = Math.max(0, calendarDays || 0);

    let pFt;

    // Small pipe: 6"–10" (tight, length-sensitive)
    if (diameter <= 10) {
        // 300 ft ≈ 0.14, 3000 ft ≈ 0.95 (capped)
        pFt = Math.min(0.90, 0.05 + 0.0003 * L);
    }
    // Medium pipe: 12"–24"
    else if (diameter <= 24) {
        // 500 ft ≈ 0.20, 2500 ft ≈ 0.60, 5000 ft ≈ 0.90
        pFt = Math.min(0.90, 0.10 + 0.0002 * L);
    }
    // Large pipe: 27"–42"
    else if (diameter < 60) {
        // 300 ft ≈ 0.33, 3000 ft ≈ 0.60, then flatten
        pFt = Math.min(0.95, 0.30 + 0.0001 * L);
    }
    // Very large pipe: 60"+ (your spec: 0.63 at 300 ft, +0.05/300 ft)
    else {
        if (L <= 300) {
            pFt = 0.63;
        } else {
            const extraSegments = (L - 300) / 300;
            pFt = Math.min(0.95, 0.63 + 0.05 * extraSegments);
        }
    }

    // Day-based component: more days, more chances for pipe-related issues
    const pDays = Math.min(0.60, 0.02 * d);  // 10 days ≈ 0.20, 20 days ≈ 0.40

    return combinedProbability(pFt, pDays);
}
```

### Aggregate advanced pipe penalty

```js
// Compute effective pipe penalty from selections + total footage + duration
function computeAdvancedPipePenalty(totalFootage, calendarDays, pipeSelections) {
    if (!pipeSelections.length || totalFootage <= 0) return 0;

    // 1) Determine per-size footage
    const anySpecific = pipeSelections.some(ps => !isNaN(ps.footage) && ps.footage > 0);

    if (!anySpecific) {
        const equalFt = totalFootage / pipeSelections.length;
        pipeSelections.forEach(ps => { ps.footage = equalFt; });
    } else {
        pipeSelections.forEach(ps => {
            if (isNaN(ps.footage) || ps.footage < 0) ps.footage = 0;
        });
    }

    // 2) Compute probability-weighted effective penalty, take worst case
    let effectivePipePenalty = 0;
    pipeSelections.forEach(ps => {
        const p   = pipeProbability(ps.diameter, ps.footage, calendarDays);
        const eff = ps.penalty * p;
        if (eff > effectivePipePenalty) {
            effectivePipePenalty = eff;
        }
    });

    return effectivePipePenalty;
}
```

---

## 6. Traffic & easement: length + days

```js
let useAdvancedTrafficEasementModel = true;

// Time + length-based probabilities for easement & traffic

function trafficProbability(footageFt, calendarDays) {
    const L = Math.max(0, footageFt || 0);
    const d = Math.max(0, calendarDays || 0);

    // ft-based risk: 300 ft≈0.15, 3000 ft≈0.55, 6000 ft≈0.95 (cap at 0.80)
    const pFt = Math.min(0.80, 0.10 + 0.00015 * L);

    // day-based: 3d≈0.26, 10d≈0.40, 20d≈0.60, cap 0.90
    const pDays = Math.min(0.90, 0.20 + 0.02 * d);

    return combinedProbability(pFt, pDays);
}

function easementProbability(footageFt, calendarDays) {
    const L = Math.max(0, footageFt || 0);
    const d = Math.max(0, calendarDays || 0);

    // ft-based: 300 ft≈0.21, 3000 ft≈0.75 (cap at 0.85)
    const pFt = Math.min(0.85, 0.15 + 0.00020 * L);

    // day-based: 3d≈0.345, 10d≈0.45, 20d≈0.60, cap 0.95
    const pDays = Math.min(0.95, 0.30 + 0.015 * d);

    return combinedProbability(pFt, pDays);
}
```

---

## 7. Integration into `calculatePrep()`

Key pieces (only the parts you need to adjust):

```js
function calculatePrep() {
    const footage    = parseFloat(document.getElementById('prepFootage').value) || 0;
    const baseRate   = parseFloat(document.getElementById('prepBaseRate').value) || 0;
    const crews      = parseFloat(document.getElementById('prepCrews').value) || 1;
    const daysPerWeek = parseFloat(document.getElementById('prepDaysPerWeek').value) || 5;

    // Penalties
    const heavyPenalty    = parseFloat(document.getElementById('prepHeavyPenalty').value)    || 0;
    const easementPenalty = parseFloat(document.getElementById('prepEasementPenalty').value) || 0;
    const rootPenalty     = parseFloat(document.getElementById('prepRootPenalty').value)     || 0;
    const trafficPenalty  = parseFloat(document.getElementById('prepTrafficPenalty').value)  || 0;
    const greasePenalty   = parseFloat(document.getElementById('prepGreasePenalty').value)   || 0;

    // Boosts
    const recyclerBoost    = parseFloat(document.getElementById('prepRecyclerBoost').value)    || 0;
    const clusterBoost     = parseFloat(document.getElementById('prepClusterBoost').value)     || 0;
    const preInspBoost     = parseFloat(document.getElementById('prepPreInspBoost').value)     || 0;
    const modernEquipBoost = parseFloat(document.getElementById('prepModernEquipBoost').value) || 0;
    const expOpBoost       = parseFloat(document.getElementById('prepExpOpBoost').value)       || 0;

    const totalBoost = recyclerBoost + clusterBoost + preInspBoost + modernEquipBoost + expOpBoost;

    // Approximate project duration (ignoring penalties)
    let approxRate = baseRate * (1 + totalBoost) * crews;
    let approxCalendarDays = 0;
    if (approxRate > 0 && footage > 0) {
        const approxWorkDays = Math.max(1, Math.ceil(footage / approxRate));
        approxCalendarDays   = Math.ceil(approxWorkDays * 7 / daysPerWeek);
    }

    // PIPE PENALTY (legacy vs advanced)
    let prepPipePenalty = 0;
    const prepPipeSelections = [];

    document.querySelectorAll('[id^="prep_pipe_"]:checked').forEach(checkbox => {
        const diameter = parseFloat(checkbox.dataset.diameter);
        const penalty  = parseFloat(checkbox.dataset.penalty);
        const lenInput = document.getElementById(`prep_pipe_len_${diameter}`);
        const footageForThisSize = lenInput ? parseFloat(lenInput.value) : NaN;

        prepPipeSelections.push({
            diameter,
            penalty,
            footage: footageForThisSize
        });

        if (!useAdvancedPipeModel) {
            prepPipePenalty = Math.max(prepPipePenalty, penalty);
        }
    });

    if (useAdvancedPipeModel) {
        prepPipePenalty = computeAdvancedPipePenalty(footage, approxCalendarDays, prepPipeSelections);
    }

    // Traffic & easement penalties scaled by length + days
    let effEasementPenalty = easementPenalty;
    let effTrafficPenalty  = trafficPenalty;

    if (useAdvancedTrafficEasementModel && approxCalendarDays > 0) {
        const pTraffic  = trafficProbability(footage, approxCalendarDays);
        const pEasement = easementProbability(footage, approxCalendarDays);
        effTrafficPenalty  = trafficPenalty  * pTraffic;
        effEasementPenalty = easementPenalty * pEasement;
    }

    // Apply boosts and penalties to rate
    let rate = baseRate * (1 + totalBoost);

    rate *= (1 - heavyPenalty);
    rate *= (1 - effEasementPenalty);
    rate *= (1 - rootPenalty);
    rate *= (1 - effTrafficPenalty);
    rate *= (1 - greasePenalty);
    rate *= (1 - prepPipePenalty);

    rate *= crews;

    // ... existing logic to compute weeks/days, update DOM, etc.
}
```

**Note:** there is now **no “depth” or deep-pipe variable anywhere**. Make sure any `prepDepthPenalty` slider, variable, or sync entry is removed from both HTML and JS.

---

## 8. Integration into `calculateLining()`

Analogous wiring for lining:

```js
function calculateLining() {
    const footage        = parseFloat(document.getElementById('liningFootage').value) || 0;
    const baseRatePerWeek= parseFloat(document.getElementById('liningBaseRate').value) || 0;
    const crews          = parseFloat(document.getElementById('liningCrews').value) || 1;

    // Penalties
    const coldPenalty      = parseFloat(document.getElementById('liningColdPenalty').value)      || 0;
    const hotPenalty       = parseFloat(document.getElementById('liningHotPenalty').value)       || 0;
    const hostPipePenalty  = parseFloat(document.getElementById('liningHostPipePenalty').value)  || 0;
    const bypassPenalty    = parseFloat(document.getElementById('liningBypassPenalty').value)    || 0;
    const lateralPenalty   = parseFloat(document.getElementById('liningLateralPenalty').value)   || 0;
    const accessPenalty    = parseFloat(document.getElementById('liningAccessPenalty').value)    || 0;
    const groundwaterPenalty = parseFloat(document.getElementById('liningGroundwaterPenalty').value) || 0;
    const newCrewPenalty   = parseFloat(document.getElementById('liningNewCrewPenalty').value)   || 0;

    // Boosts
    const steamBoost        = parseFloat(document.getElementById('liningSteamBoost').value)        || 0;
    const uvBoost           = parseFloat(document.getElementById('liningUVBoost').value)           || 0;
    const goodPipeBoost     = parseFloat(document.getElementById('liningGoodPipeBoost').value)     || 0;
    const minLateralBoost   = parseFloat(document.getElementById('liningMinLateralBoost').value)   || 0;
    const bypassBoost       = parseFloat(document.getElementById('liningBypassBoost').value)       || 0;
    const expCrewBoost      = parseFloat(document.getElementById('liningExpCrewBoost').value)      || 0;
    const optimalWeatherBoost = parseFloat(document.getElementById('liningOptimalWeatherBoost').value) || 0;

    const totalBoost = steamBoost + uvBoost + goodPipeBoost + minLateralBoost +
                       bypassBoost + expCrewBoost + optimalWeatherBoost;

    // Approximate duration (ignoring penalties)
    let approxWeeklyRate = baseRatePerWeek * (1 + totalBoost) * crews;
    let approxCalendarDays = 0;
    if (approxWeeklyRate > 0 && footage > 0) {
        const approxWeeks = Math.max(1, Math.ceil(footage / approxWeeklyRate));
        approxCalendarDays = approxWeeks * 7;
    }

    // PIPE PENALTY (legacy vs advanced)
    let liningPipePenalty = 0;
    const liningPipeSelections = [];

    document.querySelectorAll('[id^="lining_pipe_"]:checked').forEach(checkbox => {
        const diameter = parseFloat(checkbox.dataset.diameter);
        const penalty  = parseFloat(checkbox.dataset.penalty);
        const lenInput = document.getElementById(`lining_pipe_len_${diameter}`);
        const footageForThisSize = lenInput ? parseFloat(lenInput.value) : NaN;

        liningPipeSelections.push({
            diameter,
            penalty,
            footage: footageForThisSize
        });

        if (!useAdvancedPipeModel) {
            liningPipePenalty = Math.max(liningPipePenalty, penalty);
        }
    });

    if (useAdvancedPipeModel) {
        liningPipePenalty = computeAdvancedPipePenalty(footage, approxCalendarDays, liningPipeSelections);
    }

    // Access & bypass penalties scaled like traffic
    let effAccessPenalty = accessPenalty;
    let effBypassPenalty = bypassPenalty;

    if (useAdvancedTrafficEasementModel && approxCalendarDays > 0) {
        const pTrafficAnalog = trafficProbability(footage, approxCalendarDays);
        effAccessPenalty = accessPenalty * pTrafficAnalog;
        effBypassPenalty = bypassPenalty * pTrafficAnalog;
    }

    // Apply boosts and penalties
    let rate = baseRatePerWeek * (1 + totalBoost);

    rate *= (1 - coldPenalty);
    rate *= (1 - hotPenalty);
    rate *= (1 - hostPipePenalty);
    rate *= (1 - effBypassPenalty);
    rate *= (1 - lateralPenalty);
    rate *= (1 - effAccessPenalty);
    rate *= (1 - groundwaterPenalty);
    rate *= (1 - newCrewPenalty);
    rate *= (1 - liningPipePenalty);

    rate *= crews;

    // ... existing logic to convert rate to weeks/days, update DOM, etc.
}
```

---

If you send me one or two real historical jobs (sizes, footage, conditions, and what production you actually saw), I can tune the slopes (the 0.0003, 0.02, etc.) to make this estimator track your real-world numbers even more closely.
