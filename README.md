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

Composite factor of 0.97 reflects composite wing + tail with metal fuselage. Design ranges include a 50 nm buffer for uncertainty.

## Configuration

Most parameters in `configs.py` have been set to design values. Remaining estimates marked with `*** UPDATE ***` can be refined as better data becomes available.

## Methods

- **Fuel fractions**: Warmup/takeoff (Eq 6.8), climb (Eq 6.9), cruise Breguet (Eq 6.11), loiter Breguet (Eq 6.14), landing (Eq 6.22/6.23)
- **Empty weight**: Refined regression from Table 6.1 (jet transport) with composite factor
- **Mission profile**: FAR 121.645 international — cruise, contingency loiter, attempted landing, go-around, divert to alternate, regulatory hold, land
- **Iteration**: Damped fixed-point iteration on W0 with drag-polar L/D update each step
