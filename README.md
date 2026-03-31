# Regional Jet Mission Sizing

Iterative takeoff weight sizing tool based on Raymer's *Aircraft Design: A Conceptual Approach* (Chapter 6). Uses a fixed engine and refined empty weight regression (Table 6.1) with drag-polar-based L/D.

## Requirements

- Python 3.10+
- `matplotlib` (for plots only)

## Usage

```bash
# Run sizing for all variants
python3 main.py

# Generate plots
python3 plots.py
```

## Project Structure

| File / Dir | Description |
|------------|-------------|
| `sizing.py` | Core sizing solver — atmosphere model, Breguet equations, empty weight regression, iterative W0 solver |
| `configs.py` | Mission profile builder and aircraft variant assembly from data files |
| `data/` | Per-aircraft data files (`ZRJ70.py`, `ZRJ100.py`, `ZRJ50.py`) |
| `main.py` | CLI output — per-variant results, comparison table, range sensitivity |
| `plots.py` | Matplotlib visualizations — weight breakdown, range sensitivity, fuel burn profile, mission profile, variant comparison |
| `plots_output/` | Generated chart images |

## Design Parameters

| Parameter | Value |
|-----------|-------|
| Engine | PW1200G (2 × 19,190 lbf SLS, BPR 9) |
| TSFC | 0.5167 cruise / 0.4134 loiter [lb/(lb·hr)] |
| Cruise | Mach 0.78 at 35,000 ft |
| Wing Area | 1,016.58 ft² |
| Aspect Ratio | 7.8 |
| Oswald e | 0.727 |
| Alternate Range | 100 nm |
| Regulatory Hold | 30 min |
| Contingency | 10% of cruise time |

## Variants

| Variant | Pax | Payload (lbs) | Range (nm) | CD0 | Composite |
|---------|-----|--------------|------------|-----|-----------|
| ZRJ70 (Composite) | 76 | 20,347 | 1,800 | 0.01843 | 0.97 |
| ZRJ100 (Composite) | 100 | 26,092 | 1,200 | 0.01910 | 0.97 |
| ZRJ70 (No Composite) | 76 | 20,347 | 1,800 | 0.01843 | 1.00 |
| ZRJ100 (No Composite) | 100 | 26,092 | 1,200 | 0.01910 | 1.00 |
| ZRJ50 (Composite) | 50 | 11,350 | 1,800* | 0.01843 | 0.97 |

*Fixed W0 = 65,000 lbs, same airframe as ZRJ70 (We = 50,136 lbs). Mission is infeasible — see below.

Composite factor of 0.97 reflects composite wing + tail with metal fuselage.

## Results

| Parameter | ZRJ70 (Comp) | ZRJ100 (Comp) | ZRJ70 (No Comp) | ZRJ100 (No Comp) |
|-----------|-------------|---------------|-----------------|-------------------|
| W0 [lbs] | 96,308 | 100,719 | 100,361 | 104,558 |
| We [lbs] | 52,289 | 53,959 | 55,488 | 57,108 |
| Total Fuel [lbs] | 22,884 | 19,880 | 23,737 | 20,571 |
| Trip Fuel [lbs] | 17,899 | 14,679 | 18,549 | 15,177 |
| Reserve Fuel [lbs] | 4,986 | 5,202 | 5,189 | 5,394 |
| T/W (SLS) | 0.399 | 0.381 | 0.382 | 0.367 |
| W/S [psf] | 94.7 | 99.1 | 98.7 | 102.9 |
| L/D cruise | 15.08 | 14.90 | 15.22 | 15.01 |
| (L/D)_max | 15.55 | 15.27 | 15.55 | 15.27 |
| Growth Factor | 4.73 | 3.86 | 4.93 | 4.01 |

### ZRJ50 (Composite) — Same Airframe, Fixed W0 = 65,000 lbs

CRJ550-style derivative: same airframe as ZRJ70 (We = 52,289 lbs), reconfigured to 50-seat cabin, constrained to W0 = 65,000 lbs.

**Result: Infeasible at 65,000 lbs.** Even at zero cruise range, overhead weight (We + min fuel + crew + payload = 72,026 lbs) exceeds the cap by 7,026 lbs. The minimum W0 for zero useful range (100 nm) is ~72,874 lbs.

W0 vs. maximum range (same airframe, same payload):

| W0 [lbs] | Max Range [nm] |
|-----------|---------------|
| 72,000 | Infeasible |
| 74,000 | 261 |
| 76,000 | 546 |
| 78,000 | 829 |
| 80,000 | 1,110 |
| 82,000 | 1,387 |
| 84,000 | 1,662 |
| 86,000 | 1,933 |

## Methods

- **Fuel fractions**: Warmup/takeoff (Eq 6.8), climb (Eq 6.9), cruise Breguet (Eq 6.11), loiter Breguet (Eq 6.14), landing (Eq 6.22/6.23)
- **Empty weight**: Refined regression from Table 6.1 (jet transport) with composite factor
- **Mission profile**: FAR 121.645 international — cruise, contingency loiter, attempted landing, go-around, divert to alternate (100 nm), regulatory hold (30 min), land
- **Iteration**: Damped fixed-point iteration on W0 with drag-polar L/D update each step
