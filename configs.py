"""
Aircraft variant configurations for Regional Jet sizing.

Builds AircraftConfig objects from per-aircraft data files in data/.
"""

from sizing import (
    Engine, MissionSegment, AircraftConfig, SegmentType,
    standard_atmosphere, NM_TO_FT, climb_weight_fraction,
)
from data.ZRJ70 import AIRCRAFT as ZRJ70
from data.ZRJ100 import AIRCRAFT as ZRJ100
from data.ZRJ50 import AIRCRAFT as ZRJ50


# ═════════════════════════════════════════════════════════════════
#  HELPERS
# ═════════════════════════════════════════════════════════════════

_PERSON_WEIGHT = 197                    # [lbs] per crew member incl. bag


def _crew_weight(d: dict) -> float:
    return (d["n_pilots"] + d["n_flight_attendants"]) * _PERSON_WEIGHT


def _engine_from(d: dict) -> Engine:
    return Engine(
        name=d["engine_name"],
        tsfc_cruise=d["tsfc_cruise"],
        tsfc_loiter=d["tsfc_loiter"],
        max_thrust_per_engine=d["max_thrust_per_engine"],
        num_engines=d["num_engines"],
        bypass_ratio=d["bypass_ratio"],
    )


def _cruise_velocity_fps(mach: float, altitude_ft: float) -> float:
    atm = standard_atmosphere(altitude_ft)
    return mach * atm["speed_of_sound_fps"]


def international_mission(range_nm: float,
                          alternate_nm: float = 100.0,
                          cruise_mach: float = 0.78,
                          cruise_alt: float = 35_000.0,
                          loiter_2_min: float = 30.0,
                          contingency_frac: float = 0.10) -> list[MissionSegment]:
    """
    FAR 121.645 international mission profile (9 legs).

    Loiter 1 = contingency_frac × cruise time  (10% default)
    Loiter 2 = regulatory hold at alternate     (30 min default)
    """
    v_fps = _cruise_velocity_fps(cruise_mach, cruise_alt)
    cruise_time_s = (range_nm * NM_TO_FT) / v_fps
    loiter_1_min = (cruise_time_s * contingency_frac) / 60.0

    # Climb weight fraction from Raymer Eq 6.9
    climb_wf = climb_weight_fraction(cruise_mach)

    return [
        MissionSegment(
            "Warmup & Takeoff",
            SegmentType.WARMUP_TAKEOFF,
            weight_fraction=0.97,               # Raymer Eq 6.8 (0.97–0.99)
        ),
        MissionSegment(
            "Climb & Accelerate",
            SegmentType.CLIMB,
            weight_fraction=None,               # Will use Eq 6.9
        ),
        MissionSegment(
            f"Cruise to Destination ({range_nm:.0f} nm)",
            SegmentType.CRUISE,
            range_nm=range_nm,
        ),
        MissionSegment(
            f"Loiter 1 ({loiter_1_min:.1f} min contingency)",
            SegmentType.LOITER,
            endurance_min=loiter_1_min,
            use_loiter_sfc=True,
            use_max_ld=True,
        ),
        MissionSegment(
            "Attempt Landing",
            SegmentType.LANDING,
            weight_fraction=0.995,              # Raymer Eq 6.22/6.23
        ),
        MissionSegment(
            "Climb (go-around)",
            SegmentType.CLIMB,
            weight_fraction=climb_wf,           # Same as initial climb
        ),
        MissionSegment(
            f"Divert to Alternate ({alternate_nm:.0f} nm)",
            SegmentType.CRUISE,
            range_nm=alternate_nm,
        ),
        MissionSegment(
            f"Loiter 2 ({loiter_2_min:.0f} min hold)",
            SegmentType.LOITER,
            endurance_min=loiter_2_min,
            use_loiter_sfc=True,
            use_max_ld=True,
        ),
        MissionSegment(
            "Land",
            SegmentType.LANDING,
            weight_fraction=0.995,
        ),
    ]


def _build_config(d: dict, name: str,
                  composite_factor: float | None = None) -> AircraftConfig:
    """Build an AircraftConfig from a data dict."""
    cf = composite_factor if composite_factor is not None else d["composite_factor"]
    return AircraftConfig(
        name=name,
        payload_weight=d["payload_weight"],
        crew_weight=_crew_weight(d),
        cd0=d["cd0"],
        composite_factor=cf,
        engine=_engine_from(d),
        segments=international_mission(
            range_nm=d["design_range_nm"],
            alternate_nm=d["alternate_range_nm"],
            cruise_mach=d["cruise_mach"],
            cruise_alt=d["cruise_altitude_ft"],
        ),
        reserve_after_segment=5,
        aspect_ratio=d["aspect_ratio"],
        oswald_e=d["oswald_e"],
        wing_area_ft2=d["wing_area_ft2"],
        mach_max=d["mach_max"],
        cruise_mach=d["cruise_mach"],
        cruise_altitude_ft=d["cruise_altitude_ft"],
        ew_a=d["ew_a"],
        ew_C1=d["ew_C1"],
        ew_C2=d["ew_C2"],
        ew_C3=d["ew_C3"],
        ew_C4=d["ew_C4"],
        ew_C5=d["ew_C5"],
        Kvs=d["Kvs"],
        trapped_fuel_factor=d["trapped_fuel_factor"],
    )


# ═════════════════════════════════════════════════════════════════
#  AIRCRAFT VARIANTS
# ═════════════════════════════════════════════════════════════════

# ── ZRJ70 (76-seat, NA) ───────────────────────────────────────
na_composite    = _build_config(ZRJ70, "ZRJ70 (Composite)")
na_no_composite = _build_config(ZRJ70, "ZRJ70 (No Composite)", composite_factor=1.0)

# ── ZRJ100 (100-seat, EU) ─────────────────────────────────────
eu_composite    = _build_config(ZRJ100, "ZRJ100 (Composite)")
eu_no_composite = _build_config(ZRJ100, "ZRJ100 (No Composite)", composite_factor=1.0)

# ── ZRJ50 (50-seat, constrained) ──────────────────────────────
na_50seat    = _build_config(ZRJ50, "ZRJ50 (Composite)")
NA_50SEAT_W0 = ZRJ50["fixed_w0"]
NA_50SEAT_REF = na_composite                # Same airframe → use its We


# Collect all variants for easy iteration
ALL_VARIANTS = [na_composite, eu_composite, na_no_composite, eu_no_composite]
CONSTRAINED_VARIANTS = [(na_50seat, NA_50SEAT_W0, NA_50SEAT_REF)]
