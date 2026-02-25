"""
Regional Jet Mission Sizing & Weight Estimation
Based on Raymer's Aircraft Design: A Conceptual Approach, 7th Ed. (Chapter 6)

Refined iterative sizing with fixed-engine support.
"""

import copy
import math
from dataclasses import dataclass, field
from enum import Enum, auto


# ── Constants ────────────────────────────────────────────────────

NM_TO_FT = 6076.115      # 1 nautical mile [ft]
KTS_TO_FPS = 1.68781      # 1 knot [ft/s]
GAMMA_AIR = 1.4
R_AIR = 1716.49           # Gas constant for air [ft·lbf/(slug·R)]


# ── Standard Atmosphere ──────────────────────────────────────────

def standard_atmosphere(altitude_ft: float) -> dict[str, float]:
    """
    ISA standard atmosphere properties (valid to ~65,600 ft).

    Returns dict:
        temperature_R, pressure_psf, density_slugft3, speed_of_sound_fps
    """
    T_SL = 518.67       # Sea level temperature [R]
    P_SL = 2116.22      # Sea level pressure [psf]
    RHO_SL = 0.002377   # Sea level density [slug/ft³]
    LAPSE = 0.003566    # Troposphere lapse rate [R/ft]
    TROPO = 36089.0     # Tropopause altitude [ft]

    if altitude_ft <= TROPO:
        T = T_SL - LAPSE * altitude_ft
        P = P_SL * (T / T_SL) ** 5.2561
        rho = RHO_SL * (T / T_SL) ** 4.2561
    else:
        T_trop = T_SL - LAPSE * TROPO
        P_trop = P_SL * (T_trop / T_SL) ** 5.2561
        rho_trop = RHO_SL * (T_trop / T_SL) ** 4.2561
        T = T_trop                          # Isothermal in lower stratosphere
        k = -4.806e-5 * (altitude_ft - TROPO)
        P = P_trop * math.exp(k)
        rho = rho_trop * math.exp(k)

    a = math.sqrt(GAMMA_AIR * R_AIR * T)

    return {
        "temperature_R": T,
        "pressure_psf": P,
        "density_slugft3": rho,
        "speed_of_sound_fps": a,
    }


def dynamic_pressure(mach: float, altitude_ft: float) -> float:
    """Dynamic pressure q = 0.5 * gamma * P * M^2  [psf]."""
    atm = standard_atmosphere(altitude_ft)
    return 0.5 * GAMMA_AIR * atm["pressure_psf"] * mach ** 2


# ── Data Models ──────────────────────────────────────────────────

class SegmentType(Enum):
    WARMUP_TAKEOFF = auto()
    CLIMB = auto()
    CRUISE = auto()
    LOITER = auto()
    LANDING = auto()


@dataclass
class Engine:
    """Fixed engine parameters."""
    name: str
    tsfc_cruise: float              # [lb/(lb·hr)]
    tsfc_loiter: float              # [lb/(lb·hr)]
    max_thrust_per_engine: float    # [lbs] sea level static
    num_engines: int = 2
    bypass_ratio: float = 5.0

    @property
    def total_max_thrust(self) -> float:
        return self.max_thrust_per_engine * self.num_engines


@dataclass
class MissionSegment:
    """Single mission segment definition."""
    name: str
    segment_type: SegmentType
    weight_fraction: float | None = None    # Historical (takeoff, landing)
    range_nm: float | None = None           # Cruise
    endurance_min: float | None = None      # Loiter
    use_loiter_sfc: bool = False            # True → use loiter SFC
    use_max_ld: bool = False                # True → L/D_max (loiter optimal)


@dataclass
class AircraftConfig:
    """
    Complete aircraft configuration for Chapter 6 sizing.

    Parameters marked *** UPDATE *** should be replaced with your actual
    design values when available.
    """
    name: str

    # ── Payload & Crew ──
    payload_weight: float               # [lbs] passengers + cargo
    crew_weight: float                  # [lbs] flight crew + cabin crew (incl. bags)

    # ── Empty weight regression (Table 6.1 – Jet Transport) ──
    # We/W0 = a · W0^C1 · A^C2 · (T/W0)^C3 · (W0/S)^C4 · Mmax^C5 · Kvs
    ew_a: float = 0.869
    ew_C1: float = -0.037
    ew_C2: float = 0.398
    ew_C3: float = 0.100
    ew_C4: float = -0.161
    ew_C5: float = 0.050
    Kvs: float = 1.0                   # 1.00 fixed sweep, 1.04 variable sweep
    composite_factor: float = 0.95     # < 1.0 for composite structure

    # ── Aerodynamics ──
    aspect_ratio: float = 7.8          # *** UPDATE ***
    cd0: float = 0.020                 # *** UPDATE *** zero-lift drag coeff
    oswald_e: float = 0.80             # *** UPDATE *** Oswald efficiency
    wing_area_ft2: float = 520.0       # *** UPDATE *** reference wing area [ft²]
    mach_max: float = 0.85             # *** UPDATE *** max operating Mach

    # ── Cruise conditions ──
    cruise_mach: float = 0.78
    cruise_altitude_ft: float = 41000.0

    # ── Fuel ──
    trapped_fuel_factor: float = 1.06  # 5% reserve + 1% trapped (Raymer §6.3.4)

    # ── Mission ──
    segments: list[MissionSegment] = field(default_factory=list)
    reserve_after_segment: int = 5     # Reserve fuel counted after this leg

    # ── Engine ──
    engine: Engine | None = None

    # ── Derived properties ──

    @property
    def cruise_velocity_fps(self) -> float:
        atm = standard_atmosphere(self.cruise_altitude_ft)
        return self.cruise_mach * atm["speed_of_sound_fps"]

    @property
    def cruise_velocity_kts(self) -> float:
        return self.cruise_velocity_fps / KTS_TO_FPS

    @property
    def cruise_q(self) -> float:
        """Dynamic pressure at cruise [psf]."""
        return dynamic_pressure(self.cruise_mach, self.cruise_altitude_ft)

    def ld_from_drag_polar(self, wing_loading: float) -> float:
        """
        L/D from drag polar at a given wing loading (Raymer Eq 6.13).

        L/D = 1 / (q·CD0/(W/S) + (W/S)/(q·π·A·e))
        """
        q = self.cruise_q
        parasitic = q * self.cd0 / wing_loading
        induced = wing_loading / (q * math.pi * self.aspect_ratio * self.oswald_e)
        return 1.0 / (parasitic + induced)

    @property
    def ld_max(self) -> float:
        """
        Maximum L/D (occurs when parasitic drag = induced drag).

        (L/D)_max = 1 / (2 · sqrt(CD0 / (π·A·e)))
        """
        return 1.0 / (2.0 * math.sqrt(
            self.cd0 / (math.pi * self.aspect_ratio * self.oswald_e)
        ))


@dataclass
class SegmentResult:
    """Result for a single mission segment."""
    name: str
    segment_type: SegmentType
    weight_fraction: float
    fuel_burned: float = 0.0
    cruise_time_s: float | None = None
    ld_used: float | None = None


@dataclass
class SizingResult:
    """Complete sizing output."""
    config_name: str
    converged: bool
    iterations: int
    # Weights
    w0: float               # Takeoff gross weight [lbs]
    we: float               # Empty weight [lbs]
    wf: float               # Total fuel weight [lbs]
    w_crew: float           # Crew weight [lbs]
    w_payload: float        # Payload weight [lbs]
    # Fractions
    we_frac: float
    wf_frac: float
    # Fuel breakdown
    trip_fuel: float
    reserve_fuel: float
    # Mission
    segment_results: list[SegmentResult] = field(default_factory=list)
    # Performance
    thrust_to_weight: float = 0.0
    wing_loading: float = 0.0
    ld_cruise: float = 0.0
    ld_max: float = 0.0
    growth_factor: float = 0.0
    weight_margin: float = 0.0          # For fixed-W0: positive = closes


# ── Weight Fraction Calculations (Raymer Ch 6) ──────────────────

def climb_weight_fraction(mach_end: float) -> float:
    """
    Climb & accelerate weight fraction (Raymer Eq 6.9, subsonic).

    Wi/Wi-1 = 1.0065 - 0.0325·M

    For acceleration from M=0.1 to cruise Mach. If starting from
    a different Mach, divide by the fraction at the starting Mach.
    """
    # From Mach 0.1 (post-takeoff) to mach_end
    frac_end = 1.0065 - 0.0325 * mach_end
    frac_start = 1.0065 - 0.0325 * 0.1     # ~1.003
    return frac_end / frac_start


def cruise_weight_fraction(range_nm: float, tsfc_hr: float,
                           velocity_fps: float, ld_ratio: float) -> tuple[float, float]:
    """
    Breguet range equation for jet cruise (Raymer Eq 6.11).

    Returns: (Wi/Wi-1, cruise_time_seconds)
    """
    R_ft = range_nm * NM_TO_FT
    C_per_s = tsfc_hr / 3600.0
    wf = math.exp(-R_ft * C_per_s / (velocity_fps * ld_ratio))
    cruise_time_s = R_ft / velocity_fps
    return wf, cruise_time_s


def loiter_weight_fraction(endurance_min: float, tsfc_hr: float,
                           ld_ratio: float) -> float:
    """
    Breguet endurance equation for jet loiter (Raymer Eq 6.14).

    Returns Wi/Wi-1.
    """
    E_s = endurance_min * 60.0
    C_per_s = tsfc_hr / 3600.0
    return math.exp(-E_s * C_per_s / ld_ratio)


def empty_weight_fraction_ch3(w0: float, A: float = 1.272,
                               C: float = -0.072,
                               Kvs: float = 1.0,
                               composite_factor: float = 1.0) -> float:
    """
    Simple empty weight fraction (Raymer Table 3.1 – Jet Transport).

    We/W0 = A · W0^C · Kvs · composite_factor
    """
    return A * (w0 ** C) * Kvs * composite_factor


def empty_weight_fraction_ch6(w0: float, config: "AircraftConfig",
                               tw_ratio: float,
                               wing_loading: float) -> float:
    """
    Refined empty weight fraction (Raymer Table 6.1 – Jet Transport).

    We/W0 = a · W0^C1 · A^C2 · (T/W0)^C3 · (W0/S)^C4 · Mmax^C5 · Kvs · composite

    Args:
        w0:           Current W0 guess [lbs]
        config:       Aircraft configuration
        tw_ratio:     Thrust-to-weight ratio (T/W0) at current W0
        wing_loading: Wing loading (W0/S) at current W0 [psf]
    """
    c = config
    we_w0 = (c.ew_a
             * w0 ** c.ew_C1
             * c.aspect_ratio ** c.ew_C2
             * tw_ratio ** c.ew_C3
             * wing_loading ** c.ew_C4
             * c.mach_max ** c.ew_C5
             * c.Kvs
             * c.composite_factor)
    return we_w0


# ── Solver ───────────────────────────────────────────────────────

def compute_segment_results(config: AircraftConfig,
                            w_start: float,
                            ld_cruise: float,
                            ld_loiter: float) -> list[SegmentResult]:
    """
    Step through the mission computing fuel burn per segment (Raymer §6.3.4).

    Rather than just multiplying weight fractions, we track actual weight
    at each point so fuel burned per leg is calculated directly.
    """
    results = []
    w_current = w_start

    for seg in config.segments:
        cruise_time = None
        ld_used = None

        if seg.segment_type == SegmentType.WARMUP_TAKEOFF:
            wf = seg.weight_fraction

        elif seg.segment_type == SegmentType.CLIMB:
            if seg.weight_fraction is not None:
                # Use provided historical value (e.g., for go-around climb)
                wf = seg.weight_fraction
            else:
                # Raymer Eq 6.9
                wf = climb_weight_fraction(config.cruise_mach)

        elif seg.segment_type == SegmentType.CRUISE:
            tsfc = (config.engine.tsfc_loiter if seg.use_loiter_sfc
                    else config.engine.tsfc_cruise)
            ld = ld_loiter if seg.use_max_ld else ld_cruise
            ld_used = ld
            wf, cruise_time = cruise_weight_fraction(
                seg.range_nm, tsfc, config.cruise_velocity_fps, ld
            )

        elif seg.segment_type == SegmentType.LOITER:
            tsfc = (config.engine.tsfc_loiter if seg.use_loiter_sfc
                    else config.engine.tsfc_cruise)
            ld = ld_loiter if seg.use_max_ld else ld_cruise
            ld_used = ld
            wf = loiter_weight_fraction(seg.endurance_min, tsfc, ld)

        elif seg.segment_type == SegmentType.LANDING:
            wf = seg.weight_fraction

        # Fuel burned this segment (Raymer Eq 6.5)
        fuel_burned = w_current * (1.0 - wf)
        w_current = w_current * wf

        results.append(SegmentResult(
            name=seg.name,
            segment_type=seg.segment_type,
            weight_fraction=wf,
            fuel_burned=fuel_burned,
            cruise_time_s=cruise_time,
            ld_used=ld_used,
        ))

    return results


def solve_takeoff_weight(config: AircraftConfig,
                         w0_guess: float = 60000.0,
                         tolerance: float = 0.5,
                         max_iter: int = 200,
                         use_ch6_weights: bool = True) -> SizingResult:
    """
    Iteratively solve for W0 (Raymer §6.3.2 / §6.4).

    For a fixed engine, T/W varies each iteration as W0 changes.
    The L/D is computed from the drag polar at the current wing loading.

    Steps each iteration:
      1. Compute T/W and W/S from current W0
      2. Compute L/D_cruise and L/D_max from drag polar
      3. Step through mission → total fuel
      4. Compute empty weight fraction
      5. Calculate new W0 = (Wcrew + Wpayload) / (1 - Wf/W0 - We/W0)
    """
    w0 = w0_guess
    converged = False
    iterations = 0
    seg_results = []
    ld_cruise = 0.0
    ld_max_val = 0.0
    wf_frac = 0.0
    we_frac = 0.0

    for i in range(max_iter):
        iterations = i + 1

        # Current T/W and W/S (fixed engine → T/W changes with W0)
        tw = config.engine.total_max_thrust / w0
        ws = w0 / config.wing_area_ft2

        # L/D from drag polar (Raymer Eq 6.13)
        ld_cruise = config.ld_from_drag_polar(ws)
        ld_max_val = config.ld_max

        # Step through mission → fuel per segment
        seg_results = compute_segment_results(config, w0, ld_cruise, ld_max_val)

        # Total mission fuel burned (Raymer Eq 6.6)
        mission_fuel = sum(sr.fuel_burned for sr in seg_results)

        # Total fuel with reserve + trapped (Raymer Eq 6.7: Wf = 1.06 × Σ Wfi)
        total_fuel = config.trapped_fuel_factor * mission_fuel
        wf_frac = total_fuel / w0

        # Empty weight fraction
        if use_ch6_weights:
            we_frac = empty_weight_fraction_ch6(w0, config, tw, ws)
        else:
            we_frac = empty_weight_fraction_ch3(
                w0, Kvs=config.Kvs,
                composite_factor=config.composite_factor
            )

        # Sizing equation (Raymer Eq 6.1)
        denom = 1.0 - wf_frac - we_frac
        if denom <= 0:
            break  # No solution possible

        w0_new = (config.crew_weight + config.payload_weight) / denom

        if abs(w0_new - w0) < tolerance:
            converged = True
            w0 = w0_new
            break

        # Damped update (Raymer recommends ~3/4 of the way to new value)
        w0 = 0.75 * w0_new + 0.25 * w0

    # ── Final weight breakdown ──
    tw_final = config.engine.total_max_thrust / w0
    ws_final = w0 / config.wing_area_ft2
    ld_cruise = config.ld_from_drag_polar(ws_final)
    ld_max_val = config.ld_max

    we_frac = (empty_weight_fraction_ch6(w0, config, tw_final, ws_final)
               if use_ch6_weights
               else empty_weight_fraction_ch3(w0, Kvs=config.Kvs,
                                               composite_factor=config.composite_factor))
    we = w0 * we_frac

    # Re-run mission at final W0 for accurate fuel breakdown
    seg_results = compute_segment_results(config, w0, ld_cruise, ld_max_val)
    mission_fuel = sum(sr.fuel_burned for sr in seg_results)
    wf = config.trapped_fuel_factor * mission_fuel
    wf_frac = wf / w0

    # Trip fuel vs reserve fuel
    trip_fuel = sum(sr.fuel_burned for sr in seg_results[:config.reserve_after_segment])
    reserve_fuel = wf - trip_fuel

    # Growth factor (based on payload only)
    growth = w0 / config.payload_weight

    return SizingResult(
        config_name=config.name,
        converged=converged,
        iterations=iterations,
        w0=w0,
        we=we,
        wf=wf,
        w_crew=config.crew_weight,
        w_payload=config.payload_weight,
        we_frac=we_frac,
        wf_frac=wf_frac,
        trip_fuel=trip_fuel,
        reserve_fuel=reserve_fuel,
        segment_results=seg_results,
        thrust_to_weight=tw_final,
        wing_loading=ws_final,
        ld_cruise=ld_cruise,
        ld_max=ld_max_val,
        growth_factor=growth,
    )


def evaluate_fixed_w0(config: AircraftConfig, w0: float) -> SizingResult:
    """
    Evaluate a mission at a fixed W0 (no iteration).

    Instead of solving for W0, we check whether the given W0 can close
    the mission.  Returns a SizingResult with weight_margin showing the
    surplus (positive) or deficit (negative).
    """
    tw = config.engine.total_max_thrust / w0
    ws = w0 / config.wing_area_ft2

    ld_cruise = config.ld_from_drag_polar(ws)
    ld_max_val = config.ld_max

    seg_results = compute_segment_results(config, w0, ld_cruise, ld_max_val)
    mission_fuel = sum(sr.fuel_burned for sr in seg_results)
    wf = config.trapped_fuel_factor * mission_fuel
    wf_frac = wf / w0

    we_frac = empty_weight_fraction_ch6(w0, config, tw, ws)
    we = w0 * we_frac

    trip_fuel = sum(sr.fuel_burned for sr in seg_results[:config.reserve_after_segment])
    reserve_fuel = wf - trip_fuel

    margin = w0 - we - wf - config.crew_weight - config.payload_weight
    closes = margin >= 0.0

    growth = w0 / config.payload_weight

    return SizingResult(
        config_name=config.name,
        converged=closes,
        iterations=0,
        w0=w0,
        we=we,
        wf=wf,
        w_crew=config.crew_weight,
        w_payload=config.payload_weight,
        we_frac=we_frac,
        wf_frac=wf_frac,
        trip_fuel=trip_fuel,
        reserve_fuel=reserve_fuel,
        segment_results=seg_results,
        thrust_to_weight=tw,
        wing_loading=ws,
        ld_cruise=ld_cruise,
        ld_max=ld_max_val,
        growth_factor=growth,
        weight_margin=margin,
    )


def find_max_range(config: AircraftConfig,
                   w0: float,
                   mission_builder,
                   range_lo: float = 100.0,
                   range_hi: float = 5000.0,
                   tolerance_nm: float = 1.0) -> tuple[SizingResult, float]:
    """
    Binary search for the maximum cruise range at which a fixed W0 closes.

    Args:
        config:          Base aircraft config (segments will be rebuilt).
        w0:              Fixed takeoff weight [lbs].
        mission_builder: Callable(range_nm) -> list[MissionSegment].
        range_lo:        Lower bound [nm].
        range_hi:        Upper bound [nm].
        tolerance_nm:    Convergence tolerance [nm].

    Returns:
        (SizingResult at max range, max_range_nm)
    """
    best_result = None
    best_range = range_lo

    while (range_hi - range_lo) > tolerance_nm:
        mid = (range_lo + range_hi) / 2.0
        cfg = copy.deepcopy(config)
        cfg.segments = mission_builder(mid)
        result = evaluate_fixed_w0(cfg, w0)
        if result.weight_margin >= 0:
            best_result = result
            best_range = mid
            range_lo = mid
        else:
            range_hi = mid

    # Final evaluation at converged range
    if best_result is None:
        cfg = copy.deepcopy(config)
        cfg.segments = mission_builder(range_lo)
        best_result = evaluate_fixed_w0(cfg, w0)
        best_range = range_lo

    return best_result, best_range
