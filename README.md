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
| ZRJ70 (Composite) | 76 | 23,347 | 1,800 | 0.01843 | 0.97 |
| ZRJ100 (Composite) | 100 | 26,092 | 1,200 | 0.01910 | 0.97 |
| ZRJ70 (No Composite) | 76 | 23,347 | 1,800 | 0.01843 | 1.00 |
| ZRJ100 (No Composite) | 100 | 26,092 | 1,200 | 0.01910 | 1.00 |
| ZRJ50 (Composite) | 50 | 11,350 | 1,800* | 0.01843 | 0.97 |

*Fixed W0 = 65,000 lbs, same airframe as ZRJ70 (We = 50,136 lbs). Mission is infeasible — see below.

Composite factor of 0.97 reflects composite wing + tail with metal fuselage.

## Results

| Parameter | ZRJ70 (Comp) | ZRJ100 (Comp) | ZRJ70 (No Comp) | ZRJ100 (No Comp) |
|-----------|-------------|---------------|-----------------|-------------------|
| W0 [lbs] | 103,606 | 100,719 | 107,856 | 104,558 |
| We [lbs] | 55,040 | 53,959 | 58,366 | 57,108 |
| Total Fuel [lbs] | 24,431 | 19,880 | 25,355 | 20,571 |
| Trip Fuel [lbs] | 19,079 | 14,679 | 19,788 | 15,177 |
| Reserve Fuel [lbs] | 5,352 | 5,202 | 5,566 | 5,394 |
| T/W (SLS) | 0.370 | 0.381 | 0.356 | 0.367 |
| W/S [psf] | 101.9 | 99.1 | 106.1 | 102.9 |
| L/D cruise | 15.31 | 14.90 | 15.40 | 15.01 |
| (L/D)_max | 15.55 | 15.27 | 15.55 | 15.27 |
| Growth Factor | 4.44 | 3.86 | 4.62 | 4.01 |

### ZRJ50 (Composite) — Same Airframe, Fixed W0 = 65,000 lbs

CRJ550-style derivative: same airframe as ZRJ70 (We = 55,040 lbs), reconfigured to 50-seat cabin, constrained to W0 = 65,000 lbs.

**Result: Infeasible at 65,000 lbs.** Even at zero cruise range, overhead weight (We + min fuel + crew + payload = 74,777 lbs) exceeds the cap by 9,777 lbs. The minimum W0 for zero useful range (100 nm) is ~75,960 lbs.

W0 vs. maximum range (same airframe, same payload):

| W0 [lbs] | Max Range [nm] |
|-----------|---------------|
| 75,000 | Infeasible |
| 77,000 | 245 |
| 79,000 | 523 |
| 81,000 | 799 |
| 83,000 | 1,071 |
| 85,000 | 1,342 |
| 87,000 | 1,609 |
| 89,000 | 1,872 |

## Methods

- **Fuel fractions**: Warmup/takeoff (Eq 6.8), climb (Eq 6.9), cruise Breguet (Eq 6.11), loiter Breguet (Eq 6.14), landing (Eq 6.22/6.23)
- **Empty weight**: Refined regression from Table 6.1 (jet transport) with composite factor
- **Mission profile**: FAR 121.645 international — cruise, contingency loiter, attempted landing, go-around, divert to alternate (100 nm), regulatory hold (30 min), land
- **Iteration**: Damped fixed-point iteration on W0 with drag-polar L/D update each step
