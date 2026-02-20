#!/usr/bin/env python3
"""
Regional Jet Mission Sizing & Weight Estimation
Raymer Chapter 6 Methods — Fixed Engine

Usage:
    python main.py
"""

import copy
from sizing import solve_takeoff_weight, SegmentType
from configs import ALL_VARIANTS, international_mission


# ── Formatting helpers ───────────────────────────────────────────

def fmt_weight(w: float) -> str:
    return f"{w:,.0f}"


def print_header():
    print("=" * 72)
    print("  REGIONAL JET MISSION SIZING & WEIGHT ESTIMATION")
    print("  Raymer Chapter 6 Methods  |  Fixed Engine")
    print("=" * 72)


def print_engine_info(config):
    e = config.engine
    print(f"\n  Engine: {e.name}")
    print(f"    {e.num_engines} x {fmt_weight(e.max_thrust_per_engine)} lbs"
          f" = {fmt_weight(e.total_max_thrust)} lbs total SLS thrust")
    print(f"    TSFC cruise: {e.tsfc_cruise:.2f} lb/(lb-hr)"
          f"  |  TSFC loiter: {e.tsfc_loiter:.2f} lb/(lb-hr)")


def print_variant_result(result):
    r = result
    w0 = r.w0

    print(f"\n{'─' * 72}")
    print(f"  {r.config_name}")
    print(f"{'─' * 72}")

    if not r.converged:
        print("  *** DID NOT CONVERGE ***")
        return

    print(f"  Converged in {r.iterations} iterations\n")

    # Weight breakdown
    print("  Weight Breakdown:")
    print(f"    {'Takeoff Weight (W0):':<28} {fmt_weight(w0):>10} lbs  (100.0%)")
    print(f"    {'Empty Weight (We):':<28} {fmt_weight(r.we):>10} lbs  ({r.we_frac*100:5.1f}%)")
    print(f"    {'Fuel Weight (Wf):':<28} {fmt_weight(r.wf):>10} lbs  ({r.wf_frac*100:5.1f}%)")
    print(f"    {'Crew + Payload:':<28} {fmt_weight(r.w_payload):>10} lbs"
          f"  ({r.w_payload/w0*100:5.1f}%)")
    print(f"    {'─' * 50}")
    print(f"    {'Trip Fuel:':<28} {fmt_weight(r.trip_fuel):>10} lbs"
          f"  ({r.trip_fuel/w0*100:5.1f}%)")
    print(f"    {'Reserve Fuel:':<28} {fmt_weight(r.reserve_fuel):>10} lbs"
          f"  ({r.reserve_fuel/w0*100:5.1f}%)")

    # Verify weights add up
    residual = abs(w0 - r.we - r.wf - r.w_payload)
    if residual > 1.0:
        print(f"    [Weight residual: {residual:.1f} lbs]")

    # Mission segment table
    print(f"\n  Mission Segments:")
    print(f"    {'#':<4} {'Segment':<40} {'Wi/Wi-1':>8}  {'Fuel [lbs]':>10}")
    print(f"    {'─' * 66}")
    for j, sr in enumerate(r.segment_results):
        extra = ""
        if sr.cruise_time_s is not None:
            extra = f"  ({sr.cruise_time_s/60:.1f} min)"
        print(f"    {j+1:<4} {sr.name:<40} {sr.weight_fraction:>8.4f}"
              f"  {fmt_weight(sr.fuel_burned):>10}{extra}")

    total_mission_fuel = sum(sr.fuel_burned for sr in r.segment_results)
    print(f"    {'─' * 66}")
    print(f"    {'':4} {'Mission fuel (before reserve/trapped):':<40}"
          f" {'':>8}  {fmt_weight(total_mission_fuel):>10}")

    # Performance & aerodynamics
    print(f"\n  Performance:")
    print(f"    T/W (SLS):           {r.thrust_to_weight:.3f}")
    print(f"    W/S (takeoff):       {r.wing_loading:.1f} psf")
    print(f"    L/D cruise:          {r.ld_cruise:.2f}")
    print(f"    (L/D)_max:           {r.ld_max:.2f}")
    print(f"    Growth Factor:       {r.growth_factor:.2f}"
          f"  (1 lb payload -> {r.growth_factor:.2f} lb W0)")

    # T/W check
    print(f"\n  Fixed Engine Check:")
    if r.thrust_to_weight >= 0.30:
        print(f"    T/W = {r.thrust_to_weight:.3f} >= 0.30  -->  OK for jet transport")
    elif r.thrust_to_weight >= 0.25:
        print(f"    T/W = {r.thrust_to_weight:.3f}  -->  MARGINAL (typical range 0.25-0.40)")
    else:
        print(f"    T/W = {r.thrust_to_weight:.3f}  -->  LOW — engine may be undersized")
        print(f"    Consider: smaller payload, shorter range, or bigger engine")


def print_comparison_table(results):
    print(f"\n{'=' * 72}")
    print("  VARIANT COMPARISON")
    print(f"{'=' * 72}")

    names = [r.config_name for r in results]
    # Truncate names for table
    short_names = []
    for n in names:
        if "NA" in n and "No" in n:
            short_names.append("NA (No Comp)")
        elif "NA" in n:
            short_names.append("NA (Comp)")
        elif "EU" in n:
            short_names.append("EU (Comp)")
        else:
            short_names.append(n[:14])

    header = f"  {'Parameter':<26}"
    for sn in short_names:
        header += f" {sn:>14}"
    print(header)
    print(f"  {'─' * (26 + 15 * len(results))}")

    rows = [
        ("W0 [lbs]",        [f"{r.w0:>14,.0f}" for r in results]),
        ("We [lbs]",        [f"{r.we:>14,.0f}" for r in results]),
        ("Wf [lbs]",        [f"{r.wf:>14,.0f}" for r in results]),
        ("Payload [lbs]",   [f"{r.w_payload:>14,.0f}" for r in results]),
        ("We/W0",           [f"{r.we_frac:>14.4f}" for r in results]),
        ("Wf/W0",           [f"{r.wf_frac:>14.4f}" for r in results]),
        ("Trip Fuel [lbs]", [f"{r.trip_fuel:>14,.0f}" for r in results]),
        ("Reserve [lbs]",   [f"{r.reserve_fuel:>14,.0f}" for r in results]),
        ("T/W (SLS)",       [f"{r.thrust_to_weight:>14.3f}" for r in results]),
        ("W/S [psf]",       [f"{r.wing_loading:>14.1f}" for r in results]),
        ("L/D cruise",      [f"{r.ld_cruise:>14.2f}" for r in results]),
        ("(L/D)_max",       [f"{r.ld_max:>14.2f}" for r in results]),
        ("Growth Factor",   [f"{r.growth_factor:>14.2f}" for r in results]),
    ]

    for label, vals in rows:
        line = f"  {label:<26}"
        for v in vals:
            line += v
        print(line)


def print_range_sensitivity(base_config, range_values):
    """Run sizing at different ranges and show how W0 changes."""
    print(f"\n{'─' * 72}")
    print(f"  RANGE SENSITIVITY — {base_config.name}")
    print(f"{'─' * 72}")
    print(f"    {'Range [nm]':>12}  {'W0 [lbs]':>12}  {'Wf [lbs]':>12}"
          f"  {'T/W':>8}  {'L/D cruise':>10}")
    print(f"    {'─' * 60}")

    for r_nm in range_values:
        cfg = copy.deepcopy(base_config)
        cfg.segments = international_mission(
            range_nm=r_nm, alternate_nm=200,
            cruise_mach=cfg.cruise_mach, cruise_alt=cfg.cruise_altitude_ft,
        )
        result = solve_takeoff_weight(cfg)
        marker = " <-- design" if r_nm == base_config.segments[2].range_nm else ""
        if result.converged:
            print(f"    {r_nm:>12.0f}  {result.w0:>12,.0f}  {result.wf:>12,.0f}"
                  f"  {result.thrust_to_weight:>8.3f}  {result.ld_cruise:>10.2f}{marker}")
        else:
            print(f"    {r_nm:>12.0f}  {'NO SOLN':>12}  {'—':>12}"
                  f"  {'—':>8}  {'—':>10}{marker}")


# ── Main ─────────────────────────────────────────────────────────

def main():
    print_header()
    print_engine_info(ALL_VARIANTS[0])

    results = []
    for config in ALL_VARIANTS:
        result = solve_takeoff_weight(config)
        results.append(result)
        print_variant_result(result)

    print_comparison_table(results)

    # Range sensitivity for the NA composite variant
    na_config = ALL_VARIANTS[0]
    design_range = na_config.segments[2].range_nm
    range_values = [
        design_range - 400,
        design_range - 200,
        design_range,
        design_range + 200,
        design_range + 400,
    ]
    print_range_sensitivity(na_config, range_values)

    print(f"\n{'=' * 72}")
    print("  NOTE: Parameters marked *** UPDATE *** in configs.py are defaults.")
    print("  Replace with your actual design values for accurate results.")
    print(f"{'=' * 72}\n")


if __name__ == "__main__":
    main()
