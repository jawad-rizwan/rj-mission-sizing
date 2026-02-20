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

| Variant | Payload (lbs) | Range (nm) | Composite Factor |
|---------|--------------|------------|-----------------|
| NA Composite | 18,055 | 1,800 | 0.95 |
| EU Composite | 23,380 | 1,200 | 0.95 |
| NA No Composite | 18,055 | 1,800 | 1.00 |
| EU No Composite | 23,380 | 1,200 | 1.00 |

## Configuration

All configurable parameters are in `configs.py`. Parameters currently using CRJ700/CRJ1000 placeholder values are marked with `*** UPDATE ***` comments. See the engine, aerodynamic, and variant sections in that file.

## Methods

- **Fuel fractions**: Warmup/takeoff (Eq 6.8), climb (Eq 6.9), cruise Breguet (Eq 6.11), loiter Breguet (Eq 6.14), landing (Eq 6.22/6.23)
- **Empty weight**: Refined regression from Table 6.1 (jet transport) with composite factor
- **Mission profile**: FAR 121.645 international — cruise, contingency loiter, attempted landing, go-around, divert to alternate, regulatory hold, land
- **Iteration**: Damped fixed-point iteration on W0 with drag-polar L/D update each step
