"""
Graphs for Regional Jet Mission Sizing results.

Usage:
    python3 plots.py
"""

import copy
import matplotlib.pyplot as plt
from sizing import solve_takeoff_weight
from configs import ALL_VARIANTS, international_mission


def plot_weight_breakdown(results):
    """Stacked bar chart: OEW, Wf, Crew, Payload for each variant."""
    names = [r.config_name for r in results]
    we = [r.we for r in results]
    wf = [r.wf for r in results]
    wc = [r.w_crew for r in results]
    wp = [r.w_payload for r in results]

    x = range(len(results))
    fig, ax = plt.subplots(figsize=(9, 5))

    bot1 = we
    bot2 = [a + b for a, b in zip(we, wf)]
    bot3 = [a + b for a, b in zip(bot2, wc)]

    ax.bar(x, we, label="OEW", color="#4878CF")
    ax.bar(x, wf, bottom=bot1, label="Fuel Weight (Wf)", color="#D65F5F")
    ax.bar(x, wc, bottom=bot2, label="Crew", color="#F5A623")
    ax.bar(x, wp, bottom=bot3, label="Payload", color="#6ACC65")

    for i, r in enumerate(results):
        ax.text(i, r.w0 + 300, f"{r.w0:,.0f} lbs",
                ha="center", va="bottom", fontsize=9, fontweight="bold")

    ax.set_xticks(x)
    ax.set_xticklabels(names, fontsize=8)
    ax.set_ylabel("Weight [lbs]")
    ax.set_title("Takeoff Weight Breakdown by Variant")
    ax.legend()
    ax.grid(axis="y", alpha=0.3)
    fig.tight_layout()
    return fig


def plot_range_sensitivity(base_config, range_values):
    """W0 and T/W vs. range for a single variant."""
    w0_list = []
    tw_list = []
    valid_ranges = []

    for r_nm in range_values:
        cfg = copy.deepcopy(base_config)
        cfg.segments = international_mission(
            range_nm=r_nm, alternate_nm=200,
            cruise_mach=cfg.cruise_mach, cruise_alt=cfg.cruise_altitude_ft,
        )
        result = solve_takeoff_weight(cfg)
        if result.converged:
            valid_ranges.append(r_nm)
            w0_list.append(result.w0)
            tw_list.append(result.thrust_to_weight)

    fig, ax1 = plt.subplots(figsize=(9, 5))

    color_w0 = "#4878CF"
    ax1.plot(valid_ranges, w0_list, "o-", color=color_w0, linewidth=2,
             markersize=6, label="W0")
    ax1.set_xlabel("Design Range [nm]")
    ax1.set_ylabel("Takeoff Weight W0 [lbs]", color=color_w0)
    ax1.tick_params(axis="y", labelcolor=color_w0)

    ax2 = ax1.twinx()
    color_tw = "#D65F5F"
    ax2.plot(valid_ranges, tw_list, "s--", color=color_tw, linewidth=2,
             markersize=6, label="T/W")
    ax2.set_ylabel("Thrust-to-Weight Ratio (T/W)", color=color_tw)
    ax2.tick_params(axis="y", labelcolor=color_tw)

    # Mark design range
    design_range = base_config.segments[2].range_nm
    ax1.axvline(design_range, color="gray", linestyle=":", alpha=0.7)
    ax1.text(design_range, ax1.get_ylim()[1], " design",
             va="top", ha="left", fontsize=8, color="gray")

    ax1.set_title(f"Range Sensitivity — {base_config.name}")
    ax1.grid(alpha=0.3)

    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper left")

    fig.tight_layout()
    return fig


def plot_fuel_burn_profile(result):
    """Cumulative fuel burn across mission segments."""
    names = [sr.name for sr in result.segment_results]
    fuel_per_seg = [sr.fuel_burned for sr in result.segment_results]
    cumulative = []
    total = 0
    for f in fuel_per_seg:
        total += f
        cumulative.append(total)

    fig, ax = plt.subplots(figsize=(10, 5))

    ax.bar(range(len(names)), fuel_per_seg, color="#4878CF", alpha=0.7,
           label="Segment fuel")
    ax.plot(range(len(names)), cumulative, "o-", color="#D65F5F",
            linewidth=2, markersize=6, label="Cumulative fuel")

    ax.set_xticks(range(len(names)))
    ax.set_xticklabels(names, rotation=35, ha="right", fontsize=7)
    ax.set_ylabel("Fuel [lbs]")
    ax.set_title(f"Mission Fuel Burn — {result.config_name}")
    ax.legend()
    ax.grid(axis="y", alpha=0.3)
    fig.tight_layout()
    return fig


def plot_variant_comparison(results):
    """Side-by-side comparison of key performance parameters."""
    names = [r.config_name for r in results]
    metrics = {
        "T/W (SLS)":       [r.thrust_to_weight for r in results],
        "W/S [psf]":       [r.wing_loading for r in results],
        "L/D cruise":      [r.ld_cruise for r in results],
        "Growth Factor":   [r.growth_factor for r in results],
    }

    fig, axes = plt.subplots(1, 4, figsize=(14, 4))
    colors = ["#4878CF", "#D65F5F", "#6ACC65"]

    for ax, (label, values) in zip(axes, metrics.items()):
        bars = ax.bar(range(len(values)), values, color=colors[:len(values)])
        ax.set_xticks(range(len(names)))
        ax.set_xticklabels(names, fontsize=6, rotation=20, ha="right")
        ax.set_title(label, fontsize=10)
        ax.grid(axis="y", alpha=0.3)
        for i, v in enumerate(values):
            ax.text(i, v, f"{v:.2f}", ha="center", va="bottom", fontsize=8)

    fig.suptitle("Variant Performance Comparison", fontsize=12, fontweight="bold")
    fig.tight_layout()
    return fig


# ── Main ─────────────────────────────────────────────────────────

def main():
    results = []
    for config in ALL_VARIANTS:
        result = solve_takeoff_weight(config)
        results.append(result)

    # 1. Weight breakdown
    plot_weight_breakdown(results)

    # 2. Range sensitivity for NA composite
    na_config = ALL_VARIANTS[0]
    design_range = na_config.segments[2].range_nm
    range_values = list(range(
        int(design_range) - 600,
        int(design_range) + 601,
        100,
    ))
    plot_range_sensitivity(na_config, range_values)

    # 3. Fuel burn profile for NA composite
    plot_fuel_burn_profile(results[0])

    # 4. Variant comparison
    plot_variant_comparison(results)

    plt.show()


if __name__ == "__main__":
    main()
