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

| File | Description |
|------|-------------|
| `sizing.py` | Core sizing solver — atmosphere model, Breguet equations, empty weight regression, iterative W0 solver |
| `configs.py` | Engine definition, mission profile builder, and aircraft variant configurations |
| `main.py` | CLI output — per-variant results, comparison table, range sensitivity |
| `plots.py` | Matplotlib visualizations — weight breakdown, range sensitivity, fuel burn profile, variant comparison |

## Variants

| Variant | Payload (lbs) | Range (nm) | CD0 | Composite Factor |
|---------|--------------|------------|-----|-----------------|
| NA Composite | 18,055 | 1,850 | 0.02113 | 0.97 |
| EU Composite | 23,380 | 1,250 | 0.02185 | 0.97 |
| NA No Composite | 18,055 | 1,850 | 0.02113 | 1.00 |
| EU No Composite | 23,380 | 1,250 | 0.02185 | 1.00 |
| NA 50-Seat (Composite) | 11,350 | 1,850* | 0.02113 | 0.97 |

*Fixed W0 = 65,000 lbs, same airframe as NA 75-seat (We = 46,363 lbs). Mission is infeasible — see below.

Composite factor of 0.97 reflects composite wing + tail with metal fuselage. Design ranges include a 50 nm buffer for uncertainty.

## Results

| Parameter | NA (Comp) | EU (Comp) | NA (No Comp) | EU (No Comp) |
|-----------|----------|----------|-------------|-------------|
| W0 [lbs] | 85,913 | 91,421 | 89,927 | 95,158 |
| We [lbs] | 46,363 | 48,430 | 49,354 | 51,352 |
| Wf [lbs] | 20,707 | 18,625 | 21,730 | 19,441 |
| Trip Fuel [lbs] | 15,801 | 13,375 | 16,589 | 13,968 |
| T/W (SLS) | 0.447 | 0.420 | 0.427 | 0.403 |
| W/S [psf] | 108.4 | 115.4 | 113.5 | 120.1 |
| L/D cruise | 14.72 | 14.40 | 14.64 | 14.31 |
| Growth Factor | 4.76 | 3.91 | 4.98 | 4.07 |

### NA 50-Seat (Composite) — Same Airframe, Fixed W0 = 65,000 lbs

CRJ550-style derivative: same airframe as the NA 75-seat (We = 46,363 lbs), reconfigured to 50-seat cabin, constrained to W0 = 65,000 lbs.

**Result: Infeasible at 65,000 lbs.** Even at zero cruise range, overhead weight (We + min fuel + crew + payload = 66,332 lbs) exceeds the cap by 1,332 lbs. The minimum W0 for any useful mission is ~66,500 lbs.

W0 vs. maximum range (same airframe, same payload):

| W0 [lbs] | Max Range [nm] |
|-----------|---------------|
| 65,000 | Infeasible |
| 68,000 | 363 |
| 70,000 | 708 |
| 72,000 | 1,044 |
| 74,000 | 1,372 |
| 76,000 | 1,689 |
| 78,000 | 1,997 |
| 80,000 | 2,296 |

Engine: PW1200G (2 x 19,190 lbf, BPR 9, TSFC 0.48 cruise / 0.38 loiter).

## Configuration

Most parameters in `configs.py` have been set to design values. Remaining estimates marked with `*** UPDATE ***` can be refined as better data becomes available.

## Methods

- **Fuel fractions**: Warmup/takeoff (Eq 6.8), climb (Eq 6.9), cruise Breguet (Eq 6.11), loiter Breguet (Eq 6.14), landing (Eq 6.22/6.23)
- **Empty weight**: Refined regression from Table 6.1 (jet transport) with composite factor
- **Mission profile**: FAR 121.645 international — cruise, contingency loiter, attempted landing, go-around, divert to alternate, regulatory hold, land
- **Iteration**: Damped fixed-point iteration on W0 with drag-polar L/D update each step
