from dataclasses import dataclass

ERROR_TOL = 0.01


@dataclass(frozen=True)
class UNITS:
    kilo_pascal = "kPa"
    kilo_newton_per_cubic_metre = "kN/m**3"
    degree = "degree"
    unitless = ""
