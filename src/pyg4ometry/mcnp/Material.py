class M:
    """
    Material Card
    """

    def __init__(
        self,
        zk,
        fk,
        GAS=None,
        ESTEP=None,
        HSTEP=None,
        NLIB=None,
        PLIB=None,
        PNLIB=None,
        ELIB=None,
        HLIB=None,
        ALIB=None,
        SLIB=None,
        TLIB=None,
        DLIB=None,
        COND=None,
        REFI=None,
        REFIs=None,
        REFS=None,
        reg=None,
        materialNumber=None,
    ):

        self.zk = []
        self.fk = []

        self.materialNumber = materialNumber
        if reg:
            reg.addMaterial(self)
            self.reg = reg


class MT:
    """
    Thermal Neutron Scattering
    """

    def __init__(self):
        pass


class MT0:
    """
    Thermal Neutron Scattering
    """

    def __init__(self):
        pass


class MX:
    """
    Material Card Nuclide Substitution
    """

    def __init__(self):
        pass


class MPN:
    """
    Photonuclear Nuclide Selector
    """

    def __init__(self):
        pass


class OTFDB:
    """
    On-the-fly-Doppler Broadening
    """

    def __init__(self):
        pass


class TOTNU:
    """
    Total Fission
    """

    def __init__(self):
        pass
