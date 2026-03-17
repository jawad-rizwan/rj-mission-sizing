"""
ZRJ50 — 50-seat high-wing regional jet sizing data.
Constrained variant: same airframe as ZRJ70, reduced payload.
All units Imperial (ft, lbs, deg, nm).
"""

AIRCRAFT = {
    "name": "ZRJ50",
    "description": "50-seat high-wing regional jet (NA variant, constrained)",

    # --- Mission ---
    "design_range_nm": 1800,            # nm, same as ZRJ70
    "alternate_range_nm": 100,          # nm, alternate airport distance (Embraer-based)

    # --- Payload & Crew ---
    "payload_weight": 11_350,           # lbs, 50 pax × 197 lbs + 50 bags × 30 lbs
    "n_pilots": 2,
    "n_flight_attendants": 2,

    # --- Aerodynamics (same airframe as ZRJ70) ---
    "cd0": 0.01843,                     # zero-lift drag coefficient (same as ZRJ70)
    "aspect_ratio": 7.8,               # wing aspect ratio
    "oswald_e": 0.753,                  # Oswald span efficiency
    "wing_area_ft2": 1016.58,          # ft^2, reference wing area (same as ZRJ70)
    "mach_max": 0.85,                   # max operating Mach

    # --- Cruise conditions ---
    "cruise_mach": 0.78,
    "cruise_altitude_ft": 35_000.0,     # ft

    # --- Engine (PW1200G) ---
    "engine_name": "PW1200G",
    "tsfc_cruise": 0.50,               # lb/(lb-hr), Raymer Table 3.3 (high-BPR turbofan)
    "tsfc_loiter": 0.40,               # lb/(lb-hr), ~80% of cruise
    "max_thrust_per_engine": 19_190,    # lbf, sea level static
    "num_engines": 2,
    "bypass_ratio": 9.0,

    # --- Structure ---
    "composite_factor": 0.97,          # composite wing + tail, metal fuselage

    # --- Empty weight regression (Raymer Table 6.1 — Jet Transport) ---
    "ew_a": 0.869,
    "ew_C1": -0.037,
    "ew_C2": 0.398,
    "ew_C3": 0.100,
    "ew_C4": -0.161,
    "ew_C5": 0.050,
    "Kvs": 1.0,                        # 1.00 fixed sweep, 1.04 variable sweep

    # --- Fuel ---
    "trapped_fuel_factor": 1.06,       # 5% reserve + 1% trapped (Raymer §6.3.4)

    # --- Constraint ---
    "fixed_w0": 65_000,                # lbs, fixed MTOW (same airframe as ZRJ70)
    "reference_airframe": "ZRJ70",     # use ZRJ70's empty weight
}
