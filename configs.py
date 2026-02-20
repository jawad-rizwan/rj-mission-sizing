"""
Aircraft variant configurations for Regional Jet sizing.

All parameters marked *** UPDATE *** are CRJ700-like defaults.
Replace them with your actual design values when available.
"""

from sizing import (
    Engine, MissionSegment, AircraftConfig, SegmentType,
    standard_atmosphere, NM_TO_FT, climb_weight_fraction,
)


# ═════════════════════════════════════════════════════════════════
#  ENGINE  (fixed – not a rubber engine)
# ═════════════════════════════════════════════════════════════════

engine = Engine(
    name="CF34-8C5",                    # *** UPDATE *** with your selected engine
    tsfc_cruise=0.50,                   # *** UPDATE *** [lb/(lb·hr)] at cruise
    tsfc_loiter=0.40,                   # *** UPDATE *** [lb/(lb·hr)] at loiter
    max_thrust_per_engine=14_510,       # *** UPDATE *** [lbs] sea level static
    num_engines=2,
    bypass_ratio=5.0,
)


# ═════════════════════════════════════════════════════════════════
#  MISSION PROFILE BUILDERS
# ═════════════════════════════════════════════════════════════════

def _cruise_velocity_fps(mach: float, altitude_ft: float) -> float:
    atm = standard_atmosphere(altitude_ft)
    return mach * atm["speed_of_sound_fps"]


def international_mission(range_nm: float,
                          alternate_nm: float = 200.0,
                          cruise_mach: float = 0.78,
                          cruise_alt: float = 41_000.0,
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


# ═════════════════════════════════════════════════════════════════
#  AIRCRAFT VARIANTS
# ═════════════════════════════════════════════════════════════════
#
#  All three share the same engine and cruise conditions.
#  Differences: payload, range, composite vs. non-composite.
#

# ── Common aerodynamic / geometric parameters ───────────────────
# *** UPDATE ALL OF THESE WITH YOUR DESIGN VALUES ***

_COMMON_AERO = dict(
    aspect_ratio=7.8,           # *** UPDATE ***
    cd0=0.020,                  # *** UPDATE ***
    oswald_e=0.80,              # *** UPDATE ***
    wing_area_ft2=520.0,        # *** UPDATE *** [ft²]
    mach_max=0.85,              # *** UPDATE ***
    cruise_mach=0.78,
    cruise_altitude_ft=41_000.0,
)

_CRUISE_MACH = _COMMON_AERO["cruise_mach"]
_CRUISE_ALT = _COMMON_AERO["cruise_altitude_ft"]


# ── 1. North America variant (composite) ────────────────────────

na_composite = AircraftConfig(
    name="NA Variant (Composite)",
    crew_payload_weight=18_055,         # [lbs] CRJ700 ER max payload
    composite_factor=0.95,
    engine=engine,
    segments=international_mission(
        range_nm=1800, alternate_nm=200,
        cruise_mach=_CRUISE_MACH, cruise_alt=_CRUISE_ALT,
    ),
    reserve_after_segment=5,
    **_COMMON_AERO,
)


# ── 2. European variant (composite) ─────────────────────────────

eu_composite = AircraftConfig(
    name="EU Variant (Composite)",
    crew_payload_weight=23_380,         # [lbs] CRJ1000 max payload
    composite_factor=0.95,
    engine=engine,
    segments=international_mission(
        range_nm=1200, alternate_nm=200,
        cruise_mach=_CRUISE_MACH, cruise_alt=_CRUISE_ALT,
    ),
    reserve_after_segment=5,
    **_COMMON_AERO,
)


# ── 3. North America variant (no composite) ─────────────────────

na_no_composite = AircraftConfig(
    name="NA Variant (No Composite)",
    crew_payload_weight=18_055,
    composite_factor=1.0,               # No composite benefit
    engine=engine,
    segments=international_mission(
        range_nm=1800, alternate_nm=200,
        cruise_mach=_CRUISE_MACH, cruise_alt=_CRUISE_ALT,
    ),
    reserve_after_segment=5,
    **_COMMON_AERO,
)


# Collect all variants for easy iteration
ALL_VARIANTS = [na_composite, eu_composite, na_no_composite]
