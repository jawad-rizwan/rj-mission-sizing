"""
ZRJ100 — 100-seat high-wing regional jet sizing data.
All units Imperial (ft, lbs, deg, nm).
"""

AIRCRAFT = {
    "name": "ZRJ100",
    "description": "100-seat high-wing regional jet (EU variant)",

    # --- Mission ---
    "design_range_nm": 1200,            # nm, max design range
    "alternate_range_nm": 100,          # nm, alternate airport distance (Embraer-based)

    # --- Payload & Crew ---
    "payload_weight": 23_380,           # lbs, passengers + cargo (CRJ1000 max payload)
    "n_pilots": 2,
    "n_flight_attendants": 2,

    # --- Aerodynamics ---
    "cd0": 0.01910,                     # zero-lift drag coefficient
    "aspect_ratio": 7.8,               # wing aspect ratio
    "oswald_e": 0.753,                  # Oswald span efficiency
    "wing_area_ft2": 1016.58,          # ft^2, reference wing area (trapezoidal)
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
}
