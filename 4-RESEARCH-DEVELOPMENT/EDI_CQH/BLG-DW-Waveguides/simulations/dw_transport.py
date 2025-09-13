import kwant
import numpy as np
from scipy.sparse.linalg import eigsh


class BLG_DW_System:
    """Bilayer graphene domain wall transport simulator"""

    def __init__(self, width=10, length=100, U_bias=0.1, B_field=0):
        self.a = 0.246  # nm, lattice constant
        self.t0 = 2.7    # eV, intralayer hopping
        self.t1 = 0.4    # eV, interlayer hopping
        self.width = width
        self.length = length
        self.U = U_bias
        self.B = B_field

    def make_system(self):
        """Build KWANT system with AB/BA domain wall"""
        lat = kwant.lattice.general(
            [(self.a, 0), (self.a/2, self.a*np.sqrt(3)/2)],
            [(0, 0), (self.a/3, self.a*np.sqrt(3)/3)]  # A1,B1 sublattices
        )

        sys = kwant.Builder()

        # Domain wall profile: tanh transition
        def stacking_phase(x):
            return np.tanh(x / (self.width * self.a))

        def onsite(site):
            x, y = site.pos
            layer = site.family  # 0:A1, 1:B1, 2:A2, 3:B2
            bias = self.U/2 if layer < 2 else -self.U/2
            return bias

        # Define scattering region with DW
        sys[(lat(i, j) for i in range(self.length)
             for j in range(self.width))] = onsite

        # Add magnetic field via Peierls substitution
        if self.B > 0:
            # Implementation of vector potential...
            pass

        return sys.finalized()

    def compute_transport(self, energies):
        """Calculate conductance vs energy"""
        sys = self.make_system()
        conductances = []

        for E in energies:
            smatrix = kwant.smatrix(sys, E)
            G = smatrix.transmission(1, 0)  # Lead 0 to Lead 1
            conductances.append(G)

        return np.array(conductances)

    def extract_modes(self):
        """Find confined and quasi-bound states"""
        # Eigenvalue solver for bound states
        # Returns: energies, wavefunctions, localization_lengths
        pass
