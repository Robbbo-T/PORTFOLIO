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

        # Magnetic field support not yet implemented.

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

    def extract_modes(self, num_modes=5):
        """Find confined and quasi-bound states
        Returns:
            energies: array of eigenvalues
            wavefunctions: array of eigenvectors
            localization_lengths: array of localization lengths
        """
        # Build the system and get the Hamiltonian matrix
        sys = self.make_system()
        ham_mat = sys.hamiltonian_submatrix(sparse=True)

        # Use eigsh to find a few lowest-energy eigenstates
        # (Assume system is particle-hole symmetric, so use sigma=0)
        energies, wavefunctions = eigsh(ham_mat, k=num_modes, sigma=0, which='LM')

        # Calculate localization lengths (e.g., via inverse participation ratio)
        localization_lengths = []
        for psi in wavefunctions.T:
            # Normalize wavefunction
            psi_norm = psi / np.linalg.norm(psi)
            # Inverse participation ratio (IPR)
            ipr = np.sum(np.abs(psi_norm)**4)
            # Localization length estimate: 1/IPR
            loc_length = 1.0 / ipr if ipr > 0 else np.inf
            localization_lengths.append(loc_length)

        return energies, wavefunctions, np.array(localization_lengths)
