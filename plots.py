"""
Graphs for Regional Jet Mission Sizing results.

Usage:
    python3 plots.py
"""

import copy
import matplotlib.pyplot as plt
from sizing import solve_takeoff_weight, SegmentType
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

    ax.bar(x, we, label="Empty Weight (We)", color="#4878CF")
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
            range_nm=r_nm, alternate_nm=100,
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


def plot_mission_profile(result, config):
    """Raymer-style schematic mission profile with evenly spaced segments."""
    cruise_alt = config.cruise_altitude_ft
    segs = result.segment_results

    # Schematic x-positions — evenly spaced so every segment is readable.
    # Each segment gets a start and end x position.
    seg_span = 1.0  # unit width per segment
    x_points = [0.0]
    alt_points = [0.0]

    for i, sr in enumerate(segs):
        x_end = x_points[-1] + seg_span
        prev_alt = alt_points[-1]

        if sr.segment_type == SegmentType.WARMUP_TAKEOFF:
            alt_points.append(0)
        elif sr.segment_type == SegmentType.CLIMB:
            alt_points.append(cruise_alt)
        elif sr.segment_type == SegmentType.CRUISE:
            alt_points.append(cruise_alt)
        elif sr.segment_type == SegmentType.LOITER:
            alt_points.append(prev_alt)
        elif sr.segment_type == SegmentType.LANDING:
            alt_points.append(0)

        x_points.append(x_end)

    fig, ax = plt.subplots(figsize=(12, 4.5))

    # Draw the profile line
    ax.plot(x_points, alt_points, "-", color="#333333", linewidth=2, zorder=3)

    # Light fill under the profile
    ax.fill_between(x_points, alt_points, alpha=0.08, color="#4878CF")

    # Numbered circles at segment midpoints
    for i in range(len(segs)):
        x_mid = (x_points[i] + x_points[i + 1]) / 2
        a_mid = (alt_points[i] + alt_points[i + 1]) / 2
        ax.annotate(str(i + 1), (x_mid, a_mid), fontsize=8, fontweight="bold",
                    ha="center", va="center", color="white", zorder=5,
                    bbox=dict(boxstyle="circle,pad=0.25", fc="#4878CF",
                              ec="none"))

    # Segment labels below the x-axis
    for i, sr in enumerate(segs):
        x_mid = (x_points[i] + x_points[i + 1]) / 2
        # Short label
        label = sr.name
        if "Destination" in label:
            label = f"Cruise\n({config.segments[i].range_nm:.0f} nm)"
        elif "Alternate" in label:
            label = f"Divert\n({config.segments[i].range_nm:.0f} nm)"
        elif "Loiter 1" in label:
            label = "Contingency\nLoiter"
        elif "Loiter 2" in label:
            label = "Regulatory\nHold"
        elif "go-around" in label:
            label = "Go-Around\nClimb"
        elif "Attempt" in label:
            label = "Missed\nApproach"
        elif "Climb" in label:
            label = "Climb"
        elif "Warmup" in label:
            label = "Warmup\n& T/O"
        elif "Land" in label:
            label = "Land"

        ax.text(x_mid, -cruise_alt * 0.13, label, ha="center", va="top",
                fontsize=6.5, color="#333333")

    # Range and fuel info above each segment
    for i, sr in enumerate(segs):
        x_mid = (x_points[i] + x_points[i + 1]) / 2
        a_top = max(alt_points[i], alt_points[i + 1])

        # Build info line(s)
        info_parts = []
        if sr.segment_type == SegmentType.CRUISE and sr.cruise_time_s:
            r_nm = sr.cruise_time_s * config.cruise_velocity_fps / 6076.115
            info_parts.append(f"{r_nm:,.0f} nm")
            info_parts.append(f"{sr.cruise_time_s/60:,.0f} min")
        elif sr.segment_type == SegmentType.LOITER:
            # Find matching segment definition for endurance
            info_parts.append(f"{config.segments[i].endurance_min:.0f} min")
        info_parts.append(f"{sr.fuel_burned:,.0f} lb")

        info_text = "\n".join(info_parts)
        ax.text(x_mid, a_top + cruise_alt * 0.05, info_text,
                ha="center", va="bottom", fontsize=5.5, color="#555555",
                linespacing=1.3)

    # Summary box below the profile (bottom-left, outside chart area)
    trip_fuel = result.trip_fuel
    reserve_fuel = result.reserve_fuel
    summary = (f"W0 = {result.w0:,.0f} lb    "
               f"Trip Fuel = {trip_fuel:,.0f} lb    "
               f"Reserve = {reserve_fuel:,.0f} lb    "
               f"Total Fuel = {result.wf:,.0f} lb")
    ax.text(0.5, -0.15, summary, transform=ax.transAxes, fontsize=7,
            va="top", ha="center", family="monospace",
            bbox=dict(boxstyle="round,pad=0.4", fc="#f5f5f5", ec="#cccccc"))

    # Cruise altitude label
    ax.axhline(cruise_alt, color="#999999", linestyle=":", linewidth=0.8,
               alpha=0.5)
    ax.text(x_points[-1] + 0.15, cruise_alt,
            f"FL{int(cruise_alt/100)}", fontsize=7, va="center", color="#999999")

    # Clean up axes
    ax.set_xlim(-0.3, x_points[-1] + 0.8)
    ax.set_ylim(-cruise_alt * 0.28, cruise_alt * 1.35)
    ax.set_ylabel("Altitude [ft]")
    ax.set_title(f"Mission Profile — {result.config_name}", fontweight="bold")

    # Remove x-axis ticks (schematic, not to scale)
    ax.set_xticks([])
    ax.set_xlabel("(not to scale)")

    ax.grid(axis="y", alpha=0.2)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["bottom"].set_visible(False)

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

    # 4. Mission profiles for ZRJ70 and ZRJ100
    plot_mission_profile(results[0], ALL_VARIANTS[0])   # ZRJ70
    plot_mission_profile(results[1], ALL_VARIANTS[1])   # ZRJ100

    # 5. Variant comparison
    plot_variant_comparison(results)

    plt.show()


if __name__ == "__main__":
    main()
