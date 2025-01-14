import enum
from abc import abstractmethod
from dataclasses import dataclass
from typing import Final, Protocol, Sequence

from geolysis.utils import isclose, log10, mean, round_, sqrt

__all__ = [
    "weighted_spt_n_design",
    "average_spt_n_design",
    "minimum_spt_n_design",
    "EnergyCorrection",
    "GibbsHoltzOPC",
    "BazaraaPeckOPC",
    "PeckOPC",
    "LiaoWhitmanOPC",
    "SkemptonOPC",
    "DilatancyCorrection",
]

DP: Final[int] = 1


class OPCError(ValueError):
    pass


class SPTCorrection(Protocol):
    @property
    @abstractmethod
    def corrected_spt_number(self) -> float: ...


class OPC(Protocol):
    std_spt_number: float
    eop: int | float

    @abstractmethod
    def correction(self) -> float: ...

    @round_(DP)
    def corrected_spt_number(self) -> float:
        """Corrected SPT N-value."""
        corrected_spt = self.correction() * self.std_spt_number
        return min(corrected_spt, 2 * self.std_spt_number)


@round_(DP)
def average_spt_n_design(spt_numbers: Sequence[float]):
    r"""Calculates the average of the corrected SPT N-values within the
    foundation influence zone.

    :param Sequence[float] spt_numbers: SPT N-values within the foundation
        influence zone. ``spt_numbers`` can either be **corrected** or
        **uncorrected** SPT N-values.

    Examples
    --------
    >>> from geolysis.spt import average_spt_n_design
    >>> average_spt_n_design([7.0, 15.0, 18.0])
    13.3
    """
    return mean(spt_numbers)


@round_(DP)
def minimum_spt_n_design(spt_numbers: Sequence[float]):
    """The lowest N-value within the influence zone can be taken as the
    :math:`N_{design}` as suggested by ``Terzaghi & Peck (1948)``.

    :param Sequence[float] spt_numbers: SPT N-values within the foundation
        influence zone. i.e. ``spt_numbers`` can either be **corrected** or
        **uncorrected** SPT N-values.

    Examples
    --------
    >>> from geolysis.spt import minimum_spt_n_design
    >>> minimum_spt_n_design([7.0, 15.0, 18.0])
    7.0
    """
    return min(spt_numbers)


@round_(DP)
def weighted_spt_n_design(spt_numbers: Sequence[float]):
    r"""Calculates the weighted average of the corrected SPT N-values within the
    foundation influence zone.

    Due to uncertainty in field procedure in standard penetration test and also
    to consider all the N-value in the influence zone of a foundation, a method
    was suggested to calculate the design N-value which should be used in
    calculating the allowable bearing capacity of shallow foundation rather than
    using a particular N-value. All the N-value from the influence zone is taken
    under consideration by giving the highest weightage to the closest N-value
    from the base.

    :param Sequence[float] spt_numbers: SPT N-values within the foundation
        influence zone. ``spt_numbers`` can either be **corrected** or
        **uncorrected** SPT N-values.

    Notes
    -----
    Weighted average is given by the formula:

    .. math::

        N_{design} = \dfrac{\sum_{i=1}^{n} \frac{N_i}{i^2}}
                      {\sum_{i=1}^{n}\frac{1}{i^2}}

    Examples
    --------
    >>> from geolysis.spt import weighted_spt_n_design
    >>> weighted_spt_n_design([7.0, 15.0, 18.0])
    9.4
    """

    sum_total = 0.0
    sum_wgts = 0.0

    for i, corrected_spt in enumerate(spt_numbers, start=1):
        wgt = 1 / i**2
        sum_total += wgt * corrected_spt
        sum_wgts += wgt

    return sum_total / sum_wgts


#: TODO: document this
class HammerType(enum.StrEnum):
    AUTOMATIC = enum.auto()
    DONUT_1 = enum.auto()
    DONUT_2 = enum.auto()
    SAFETY = enum.auto()
    DROP = PIN = enum.auto()


class SamplerType(enum.StrEnum):
    STANDARD = enum.auto()
    NON_STANDARD = enum.auto()


@dataclass
class EnergyCorrection:
    r"""SPT N-value standardized for field procedures.

    On the basis of field observations, it appears reasonable to standardize the
    field SPT N-value as a function of the input driving energy and its
    dissipation around the sampler around the surrounding soil. The variations
    in testing procedures may be at least partially compensated by converting
    the measured N-value to :math:`N_{60}` assuming 60% hammer energy being
    transferred to the tip of the standard split spoon.

    :param int recorded_spt_number: Recorded SPT N-value from field.
    :param int | float energy_percentage: Energy percentage reaching the tip of
        the sampler, defaults to 0.6
    :param int | float hammer_efficiency: Hammer efficiency, defaults to 0.6
    :param int | float borehole_diameter_correction: Borehole diameter
        correction, defaults to 1.0
    :param int | float sampler_correction: Sampler correction, defaults to 1.0
    :param int | float rod_length_correction: Rod length correction,
        defaults to 0.75

    Notes
    -----
    Energy correction is given by the formula:

    .. math::

        N_{ENERGY} = \dfrac{E_H \cdot C_B \cdot C_S \cdot C_R \cdot N}{ENERGY}

    ``ENERGY``: 0.6, 0.55, etc

    Examples
    --------
    >>> from geolysis.spt import EnergyCorrection
    >>> energy_cor = EnergyCorrection(recorded_spt_number=30)
    >>> energy_cor.corrected_spt_number()
    22.5
    """

    recorded_spt_number: int
    energy_percentage: float
    borehole_diameter: float
    rod_length: float
    hammer_type: HammerType
    sampler_type: SamplerType

    # recorded_spt_number: int = field(
    #     validator=[validators.gt(0), validators.le(100)]
    # )
    # energy_percentage: int | float = field(
    #     default=0.6,
    #     validator=[validators.gt(0), validators.le(1.00)],
    # )
    # borehole_diameter: int | float = field(
    #     default=65.0,
    #     validator=[validators.ge(65.0), validators.le(200.0)],
    #     kw_only=True,
    # )
    # rod_length: int | float = field(
    #     default=3.0,
    #     validator=validators.gt(0.0),
    #     kw_only=True,
    # )
    # hammer_type: HammerType = field(default=HammerType.DONUT_1, kw_only=True)
    # sampler_type: SamplerType = attrs.field(
    #     default=SamplerType.STANDARD,
    #     kw_only=True,
    # )

    HAMMER_EFFICIENCY_FACTOR = {
        HammerType.AUTOMATIC: 0.70,
        HammerType.DONUT_1: 0.60,
        HammerType.DONUT_2: 0.50,
        HammerType.SAFETY: 0.55,
        HammerType.DROP: 0.45,
        HammerType.PIN: 0.45,
    }
    SAMPLER_CORRECTION_FACTORS = {
        SamplerType.STANDARD: 1.00,
        SamplerType.NON_STANDARD: 1.20,
    }

    @property
    def hammer_efficiency(self) -> int | float:
        return self.HAMMER_EFFICIENCY_FACTORS[self.hammer_type]

    @property
    def borehole_diameter_correction(self) -> int | float:
        if 65 <= self.borehole_diameter <= 115:
            corr = 1.00
        elif 115 < self.borehole_diameter <= 150:
            corr = 1.05
        else:
            corr = 1.15

        return corr

    @property
    def sampler_correction(self) -> int | float:
        return self.SAMPLER_CORRECTION_FACTORS[self.sampler_type]

    @property
    def rod_length_correction(self) -> float:
        if 3.0 <= self.rod_length <= 4.0:
            corr = 0.75
        elif 4.0 < self.rod_length <= 6.0:
            corr = 0.85
        elif 6.0 < self.rod_length <= 10.0:
            corr = 0.95
        else:
            corr = 1.00

        return corr

    def correction(self) -> float:
        """SPT Correction."""
        return (
            self.hammer_efficiency
            * self.borehole_diameter_correction
            * self.sampler_correction
            * self.rod_length_correction
        ) / self.energy_percentage

    @round_(DP)
    def corrected_spt_number(self) -> float:
        """Corrected SPT N-value."""
        return self.correction() * self.recorded_spt_number


@dataclass
class GibbsHoltzOPC(OPC):
    r"""Overburden Pressure Correction according to ``Gibbs & Holtz (1957)``.

    :param float std_spt_number: SPT N-value standardized for field
        procedures.
    :param int | float eop: Effective overburden pressure (:math:`kN/m^2`)

    Notes
    -----
    Overburden Pressure Correction is given by the formula:

    .. math:: C_N = \dfrac{350}{\sigma_o + 70} \, \sigma_o \le 280kN/m^2

    :math:`\frac{N_c}{N_{60}}` should lie between 0.45 and 2.0, if
    :math:`\frac{N_c}{N_{60}}` is greater than 2.0, :math:`N_c` should be
    divided by 2.0 to obtain the design value used in finding the bearing
    capacity of the soil.

    Examples
    --------
    >>> from geolysis.spt import GibbsHoltzOPC
    >>> opc_cor = GibbsHoltzOPC(std_spt_number=22.5, eop=100.0)
    >>> opc_cor.corrected_spt_number()
    23.2
    """

    std_spt_number: float
    eop: float

    # std_spt_number: float = field(validator=validators.gt(0))
    # eop: int | float = field(
    #     validator=[validators.gt(0.0), validators.le(280.0)]
    # )

    def correction(self) -> float:
        """SPT Correction."""
        corr = 350.0 / (self.eop + 70.0)
        if corr > 2.0:
            corr /= 2.0
        return corr


@dataclass
class BazaraaPeckOPC(OPC):
    r"""Overburden Pressure Correction according to ``Bazaraa (1967)``, and
    also by ``Peck and Bazaraa (1969)``.

    :param float std_spt_number: SPT N-value standardized for field
        procedures.
    :param int | float eop: Effective overburden pressure. (:math:`kN/m^2`)

    Notes
    -----
    Overburden Pressure Correction is given by the formula:

    .. math::

        C_N &= \dfrac{4}{1 + 0.0418 \cdot \sigma_o}, \, \sigma_o \lt 71.8kN/m^2

        C_N &= \dfrac{4}{3.25 + 0.0104 \cdot \sigma_o},
            \, \sigma_o \gt 71.8kN/m^2

        C_N &= 1 \, , \, \sigma_o = 71.8kN/m^2

    Examples
    --------
    >>> from geolysis.spt import BazaraaPeckOPC
    >>> opc_cor = BazaraaPeckOPC(std_spt_number=22.5, eop=100.0)
    >>> opc_cor.corrected_spt_number()
    21.0
    """

    std_spt_number: float
    eop: float

    # std_spt_number: float = field(validator=validators.gt(0))
    # eop: int | float = field(validator=validators.ge(0))

    #: Maximum effective overburden pressure. |rarr| :math:`kN/m^2`
    STD_PRESSURE: Final = 71.8

    def correction(self) -> float:
        """SPT Correction."""
        if isclose(self.eop, self.STD_PRESSURE, rel_tol=0.01):
            corr = 1.0
        elif self.eop < self.STD_PRESSURE:
            corr = 4 / (1 + 0.0418 * self.eop)
        else:
            corr = 4 / (3.25 + 0.0104 * self.eop)
        return corr


@dataclass
class PeckOPC(OPC):
    r"""Overburden Pressure Correction according to ``Peck et al (1974)``.

    :param float std_spt_number: SPT N-value standardized for field
        procedures.
    :param int | float eop: Effective overburden pressure (:math:`kN/m^2`)

    Notes
    -----
    Overburden Pressure Correction is given by the formula:

    .. math:: C_N = 0.77 \log \left( \dfrac{2000}{\sigma_o} \right)

    Examples
    --------
    >>> from geolysis.spt import PeckOPC
    >>> opc_cor = PeckOPC(std_spt_number=23.0, eop=100.0)
    >>> opc_cor.corrected_spt_number()
    23.0
    """

    std_spt_number: float
    eop: float

    # std_spt_number: float = field(validator=validators.gt(0))
    # eop: int | float = field(validator=validators.ge(24.0))

    def correction(self) -> float:
        """SPT Correction."""
        return 0.77 * log10(2000.0 / self.eop)


@dataclass
class LiaoWhitmanOPC(OPC):
    r"""Overburden Pressure Correction according to ``Liao & Whitman (1986)``.

    :param float std_spt_number: SPT N-value standardized for field
        procedures.
    :param int | float eop: Effective overburden pressure. (:math:`kN/m^2`)

    Notes
    -----
    Overburden Pressure Correction is given by the formula:

    .. math:: C_N = \sqrt{\dfrac{100}{\sigma_o}}

    Examples
    --------
    >>> from geolysis.spt import LiaoWhitmanOPC
    >>> opc_cor = LiaoWhitmanOPC(std_spt_number=23.0, eop=100.0)
    >>> opc_cor.corrected_spt_number()
    23.0
    """

    std_spt_number: float
    eop: float

    # std_spt_number: float = field(validator=validators.gt(0.0))
    # eop: int | float = field(validator=attrs.validators.gt(0.0))

    def correction(self) -> float:
        """SPT Correction."""
        return sqrt(100.0 / self.eop)


@dataclass
class SkemptonOPC(OPC):
    r"""Overburden Pressure Correction according to ``Skempton (1986)``.

    :param float std_spt_number: SPT N-value standardized for field
        procedures.
    :param int | float eop: Effective overburden pressure (:math:`kN/m^2`)

    Notes
    -----
    Overburden Pressure Correction is given by the formula:

    .. math:: C_N = \dfrac{2}{1 + 0.01044 \cdot \sigma_o}

    Examples
    --------
    >>> from geolysis.spt import SkemptonOPC
    >>> opc_cor = SkemptonOPC(std_spt_number=22.5, eop=100.0)
    >>> opc_cor.corrected_spt_number()
    22.0
    """

    std_spt_number: float
    eop: float

    # std_spt_number: float = field(validator=validators.gt(0))
    # eop: int | float = field()

    def correction(self) -> float:
        """SPT Correction."""
        return 2.0 / (1.0 + 0.01044 * self.eop)


@dataclass
class DilatancyCorrection:
    r"""Dilatancy SPT Correction according to ``Terzaghi & Peck (1948)``.

    For coarse sand, this correction is not required. In applying this
    correction, overburden pressure correction is applied first and then
    dilatancy correction is applied.

    :param float std_spt_number: SPT N-value standardized for field
        procedures and/or corrected for overburden pressure.

    Notes
    -----
    Dilatancy correction is given by the formula:

    .. math::

        (N_1)_{60} &= 15 + \dfrac{1}{2}((N_1)_{60} - 15) \, , \,
                      (N_1)_{60} \gt 15

        (N_1)_{60} &= (N_1)_{60} \, , \, (N_1)_{60} \le 15

    Examples
    --------
    >>> from geolysis.spt import DilatancyCorrection
    >>> dil_cor = DilatancyCorrection(std_spt_number=23.0)
    >>> dil_cor.corrected_spt_number()
    19.0
    """

    std_spt_number: float

    # std_spt_number: float = field(validator=validators.gt(0))

    @round_(DP)
    def corrected_spt_number(self) -> float:
        """Corrected SPT N-value."""
        if self.std_spt_number <= 15.0:
            return self.std_spt_number

        return 15.0 + 0.5 * (self.std_spt_number - 15.0)
