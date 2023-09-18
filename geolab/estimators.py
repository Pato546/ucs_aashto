"""This module provides functions for estimating soil engineering parameters."""

from geolab import GeotechEng
from geolab.exceptions import EngineerTypeError
from geolab.utils import arctan, round_, sin


class soil_unit_weight:
    """Calculates the moist, saturated and submerged unit weight of a
    soil sample.

    :Example:

        >>> suw = soil_unit_weight(spt_n60=13)
        >>> suw.moist
        17.3
        >>> suw.saturated
        18.75
        >>> suw.submerged
        8.93

    :param spt_n60: spt N-value corrected for 60% hammer efficiency.
    :type spt_n60: float
    """

    def __init__(self, spt_n60: float) -> None:
        self.spt_n60 = spt_n60

    @property
    @round_
    def moist(self) -> float:
        r"""Returns the ``moist`` unit weight for cohesionless soil.

        .. math::

            \gamma_{moist} = 16.0 + 0.1 \cdot N_{60} \rightarrow (kN/m^3)
        """
        return 16.0 + 0.1 * self.spt_n60

    @property
    @round_
    def saturated(self) -> float:
        r"""Returns the ``saturated`` unit weight for cohesive soil.

        .. math::

            \gamma_{sat} = 16.8 + 0.15 \cdot N_{60} \rightarrow (kN/m^3)
        """
        return 16.8 + 0.15 * self.spt_n60

    @property
    @round_
    def submerged(self) -> float:
        r"""Returns the ``submerged`` unit weight of cohesionless soil.

        .. math::
            \gamma_{submerged} = 8.8 + 0.01 \cdot N_{60} \rightarrow (kN/m^3)
        """
        return 8.8 + 0.01 * self.spt_n60


class compression_index:
    r"""The compression index of soil estimated from ``liquid limit``
    or ``void_ratio``.

    The available correlations used are :py:meth:`~compression_index.skempton_1994`,
    :py:meth:`~compression_index.terzaghi_et_al_1967`, and :meth:`~compression_index.hough_1957`.

    :Example:

        >>> c_c = compression_index(liquid_limit=35)
        >>> c_c.skempton_1994()
        0.175
        >>> c_c.terzaghi_et_al_1967()
        0.225
        >>> c_c() # By default it uses SKEMPTON's correlation
        0.175
        >>> c_c = compression_index(liquid_limit=35, eng=GeotechEng.TERZAGHI)
        >>> c_c() # This uses TERZAGHI's correlation
        0.225
        >>> c_c = compression_index(void_ratio=0.78, eng=GeotechEng.HOUGH)
        >>> c_c()
        0.148
        >>> c_c.hough_1957()
        0.148

    :param liquid_limit: water content beyond which soils flows under their own weight (%)
    :type liquid_limit: float
    :param void_ratio: ratio of the volume of voids to the volume of solids (unitless)
    :type void_ratio: float
    :param eng: specifies the type of compression index formula to use. Available
                values are ``GeotechEng.SKEMPTON``, ``GeotechEng.TERZAGHI`` and
                ``GeotechEng.HOUGH``. Defaults to ``GeotechEng.SKEMPTON``.
    :type eng: GeotechEng
    """

    def __init__(
        self,
        *,
        liquid_limit: float = 0.0,
        void_ratio: float = 0.0,
        eng: GeotechEng = GeotechEng.SKEMPTON,
    ) -> None:
        self.liquid_limit = liquid_limit
        self.void_ratio = void_ratio
        self.eng = eng

    @round_
    def __call__(self) -> float:
        """Returns the compression index of the soil sample (unitless)"""

        comp_idx: float  # compression index

        if self.eng is GeotechEng.SKEMPTON:
            comp_idx = self.skempton_1994()

        elif self.eng is GeotechEng.TERZAGHI:
            comp_idx = self.terzaghi_et_al_1967()

        elif self.eng is GeotechEng.HOUGH:
            comp_idx = self.hough_1957()

        else:
            msg = f"{self.eng} is not a valid type for engineer"
            raise EngineerTypeError(msg)

        return comp_idx

    @round_
    def terzaghi_et_al_1967(self) -> float:
        r"""Returns the compression index of the soil using ``Terzaghi's``
        correlation.

        .. math::

            C_c = 0.009 \left(LL - 10 \right) \rightarrow (unitless)

        - :math:`LL` |rarr| liquid limit of soil
        """
        return 0.009 * (self.liquid_limit - 10)

    @round_
    def skempton_1994(self) -> float:
        r"""Returns the compression index of the soil using ``Skempton's``
        correlation.

        .. math::

            C_c = 0.007 \left(LL - 10 \right) \rightarrow (unitless)

        - :math:`LL` |rarr| liquid limit of soil
        """
        return 0.007 * (self.liquid_limit - 10)

    @round_
    def hough_1957(self) -> float:
        r"""Returns the compression index of the soil using ``Hough's``
        correlation.

        .. math::

            C_c = 0.29 \left(e_o - 0.27 \right) \rightarrow (unitless)

        - :math:`e_o` |rarr| void ratio of soil
        """
        return 0.29 * (self.void_ratio - 0.27)


class soil_friction_angle:
    r"""Estimation of the internal angle of friction using spt_n60.

    For cohesionless soils the coefficient of internal friction (:math:`\phi`)
    was determined from the minimum value from :py:meth:`~soil_friction_angle.wolff_1989` 
    and :py:meth:`~soil_friction_angle.kullhawy_mayne_1990`.

    :Example:

        >>> sfa = soil_friction_angle(spt_n60=50)
        >>> sfa.wolff_1989()
        40.75
        >>> sfa() # By default it uses WOLFF's correlation
        40.75
        >>> sfa.spt_n60 = 40
        >>> sfa()
        38.236
        >>> sfa = soil_friction_angle(spt_n60=40, eop=103.8, atm_pressure=101.325,\
        ... eng=GeotechEng.KULLHAWY)
        >>> sfa()
        46.874
        >>> sfa.kullhawy_mayne_1990()
        46.874
        >>> sfa.spt_n60 = 50
        >>> sfa()
        49.035

    :param spt_n60: spt N-value corrected for 60% hammer efficiency
    :type spt_n60: float
    :param eop: effective overburden pressure :math:`kN/m^2`, defaults to 0
    :type eop: float, optional
    :param atm_pressure: atmospheric pressure :math:`kN/m^2`, defaults to 0
    :type atm_pressure: float, optional
    :param eng: specifies the type of soil friction angle formula to use. Available
                values are ``GeotechEng.WOLFF`` and ``GeotechEng.KULLHAWY``. Defaults to 
                ``GeotechEng.WOLFF``.
    :type eng: GeotechEng
    """

    def __init__(
        self,
        *,
        spt_n60: float,
        eop: float = 0,
        atm_pressure: float = 0,
        eng: GeotechEng = GeotechEng.WOLFF,
    ):
        self.spt_n60 = spt_n60
        self.eop = eop
        self.atm_pressure = atm_pressure
        self.eng = eng

    @round_
    def __call__(self) -> float:
        """Returns the internal angle of friction (degrees)."""

        _friction_angle: float

        if self.eng is GeotechEng.WOLFF:
            _friction_angle = self.wolff_1989()

        elif self.eng is GeotechEng.KULLHAWY:
            _friction_angle = self.kullhawy_mayne_1990()

        else:
            msg = f"{self.eng} is not a valid type for engineer"
            raise EngineerTypeError(msg)

        return _friction_angle

    @round_
    def wolff_1989(self) -> float:
        r"""Returns the internal angle of friction using ``Wolff's`` correlation
        for granular soils (degrees).

        .. math::

            \phi = 27.1 + 0.3 \cdot N_{60} - 0.00054 \cdot (N_{60})^2 \rightarrow (degrees)
        """
        return 27.1 + (0.3 * self.spt_n60) - (0.00054 * (self.spt_n60**2))

    @round_
    def kullhawy_mayne_1990(self) -> float:
        r"""Returns the internal angle of friction using ``Kullhawy & Mayne``
        correlation for cohesionless soils (degrees).

        .. math::

            \phi = \tan^{-1}\left[\dfrac{N_{60}}
                    {12.2 + 20.3 \cdot \left(\dfrac{\sigma_o}{P_a}\right)}
                    \right]^{0.34} \rightarrow (degrees)

        - :math:`\sigma_o \rightarrow` effective overburden pressure (:math:`kN/m^3`)
        - :math:`P_a \rightarrow` atmospheric pressure in the same unit as :math:`\sigma_o`
        """
        expr = self.spt_n60 / (12.2 + 20.3 * (self.eop / self.atm_pressure))
        return arctan(expr**0.34)


class undrained_shear_strength:
    r"""Undrained shear strength of soil.

    The available correlations used are defined below;

    .. math::

        Stroud (1974) \, \rightarrow C_u = K \times N_{60}

        Skempton (1957) \, \rightarrow \dfrac{C_u}{\sigma_o} = 0.11 + 0.0037 \times PI

    The ratio :math:`\frac{C_u}{\sigma_o}` is a constant for a given clay. ``Skempton``
    suggested that a similar constant ratio exists between the undrained shear strength
    of normally consolidated natural deposits and the effective overburden pressure.
    It has been established that the ratio :math:`\frac{C_u}{\sigma_o}` is constant provided the
    plasticity index (PI) of the soil remains constant.

    The value of the ratio :math:`\frac{C_u}{\sigma_o}` determined in a consolidated-undrained test on
    undisturbed samples is generally greater than actual value because of anisotropic consolidation
    in the field. The actual value is best determined by `in-situ shear vane test`.
    (:cite:author:`2003:arora`, p. 330)

    :param spt_n60: SPT N-value corrected for 60% hammer efficiency, defaults to None
    :type spt_n60: Optional[float], optional
    :param eop: effective overburden pressure :math:`kN/m^2`, defaults to None
    :type eop: Optional[float], optional
    :param plasticity_index: range of water content over which soil remains in plastic condition, defaults to None
    :type plasticity_index: Optional[float], optional
    :param k: stroud parameter, defaults to 3.5
    :type k: float, optional
    :param eng: specifies the type of undrained shear strength formula to use. Available values are
                geolab.STROUD and geolab.SKEMPTON, defaults to GeotechEng.STROUD
    :type eng: GeotechEng, optional
    """

    def __init__(
        self,
        spt_n60: float = 0,
        eop: float = 0,
        plasticity_index: float = 0,
        k: float = 3.5,
        eng: GeotechEng = GeotechEng.STROUD,
    ) -> None:
        self.spt_n60 = spt_n60
        self.eop = eop
        self.plasticity_index = plasticity_index
        self.k = k
        self.eng = eng

    def __call__(self) -> float:
        und_shr: float  # undrained shear strength

        if self.eng is GeotechEng.STROUD:
            und_shr = self.stroud_1974()

        elif self.eng is GeotechEng.SKEMPTON:
            und_shr = self.skempton_1957()

        else:
            msg = f"{self.eng} is not a valid type for engineer"
            raise EngineerTypeError(msg)

        return und_shr

    def stroud_1974(self):
        if not (3.5 <= self.k <= 6.5):
            msg = f"k should be 3.5 <= k <= 6.5 not {self.k}"
            raise ValueError(msg)

        return self.k * self.spt_n60

    def skempton_1957(self):
        return self.eop * (0.11 + 0.0037 * self.plasticity_index)


@round_(precision=2)
def bowles_soil_elastic_modulus(spt_n60: float) -> float:
    r"""Elastic modulus of soil estimated from ``Joseph Bowles`` correlation.

    .. math::

        E_s = 320\left(N_{60} + 15 \right)

    :Example:
        >>> bowles_soil_elastic_modulus(20)
        11200
        >>> bowles_soil_elastic_modulus(30)
        14400
        >>> bowles_soil_elastic_modulus(10)
        8000

    :param spt_n60: spt N-value corrected for 60% hammer efficiency
    :type spt_n60: float
    :return: Elastic modulus of the soil :math:`kN/m^2`
    :rtype: float
    """
    return 320 * (spt_n60 + 15)


@round_(precision=1)
def rankine_foundation_depth(
    allowable_bearing_capacity: float,
    soil_unit_weight: float,
    friction_angle: float,
) -> float:
    r"""Depth of foundation estimated using ``Rankine's`` formula.

    .. math::

        D_f=\dfrac{Q_{all}}{\gamma}\left(\dfrac{1 - \sin \phi}{1 + \sin \phi}\right)^2

    :param allow_bearing_capacity: allowable bearing capacity
    :type allow_bearing_capaciy: float
    :param unit_weight_of_soil: unit weight of soil :math:`kN/m^3`
    :type unit_weight_of_soil: float
    :param friction_angle: internal angle of friction (degrees)
    :type friction_angle: float
    :return: depth of foundation
    :rtype: float
    """
    x1 = allowable_bearing_capacity / soil_unit_weight
    x2 = (1 - sin(friction_angle)) / (1 + sin(friction_angle))

    return x1 * (x2**2)
