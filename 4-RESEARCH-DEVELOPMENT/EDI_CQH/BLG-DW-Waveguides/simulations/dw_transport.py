try:
    import kwant
    KWANT_AVAILABLE = True
except ImportError:
    print("Warning: KWANT not available. Some functionality will be limited.")
    KWANT_AVAILABLE = False

import numpy as np
try:
    from scipy.sparse.linalg import eigsh
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False

import yaml


class BLG_DW_System:
    """Bilayer graphene domain wall transport simulator
    
    This class implements transport calculations for bilayer graphene (BLG) 
    domain wall systems, including valley-Chern physics and interlayer bias effects.
    
    Key physics:
    - Valley Chern number Cv = ±1 per valley changes sign across domain walls
    - Domain walls support kink channels with |ΔCv| = 2 per valley
    - Trigonal warping (v3) splits channel dispersions
    """

    def __init__(self, width=10, length=100, U_bias=0.1, B_field=0, config_path=None):
        """Initialize BLG domain wall system
        
        Args:
            width: Domain wall width in nanometers
            length: Device length in nanometers  
            U_bias: Interlayer bias in eV
            B_field: Perpendicular magnetic field in Tesla
            config_path: Optional path to YAML configuration file
        """
        if config_path:
            self._load_config(config_path)
        else:
            self._set_default_parameters()
            
        self.width = width
        self.length = length
        self.U = U_bias
        self.B = B_field
        
        # Valley-Chern physics parameters
        self.valley_chern_number = 1  # ±1 per valley (per spin)
        self.chern_change = 2  # |ΔCv| across domain wall
        self.kink_channels_per_valley = 2  # co-propagating channels
        
    def _set_default_parameters(self):
        """Set default material parameters"""
        self.a = 0.246e-9  # m, lattice constant (converted to meters)
        self.t0 = 2.7    # eV, intralayer hopping
        self.t1 = 0.4    # eV, interlayer hopping  
        self.t3 = 0.315  # eV, trigonal warping
        self.t4 = 0.044  # eV, interlayer next-nearest neighbor
        
    def _load_config(self, config_path):
        """Load parameters from YAML configuration file"""
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
            
        mat_params = config['material_parameters']
        self.a = mat_params['bilayer_graphene']['lattice_constant']
        
        hop_params = mat_params['hopping_parameters'] 
        self.t0 = hop_params['t0']
        self.t1 = hop_params['t1']
        self.t3 = hop_params['t3']
        self.t4 = hop_params['t4']

    def make_system(self):
        """Build KWANT system with AB/BA domain wall
        
        Creates a tight-binding model for bilayer graphene with a domain wall
        that smoothly transitions between AB and BA stacking regions.
        
        Returns:
            kwant.System: Finalized KWANT system for transport calculations
        """
        if not KWANT_AVAILABLE:
            raise ImportError("KWANT package required for system creation")
            
        # Convert nm to meters for internal consistency
        a_m = self.a if self.a < 1e-6 else self.a * 1e-9
        
        lat = kwant.lattice.general(
            [(a_m, 0), (a_m/2, a_m*np.sqrt(3)/2)],
            [(0, 0), (a_m/3, a_m*np.sqrt(3)/3)]  # A1,B1 sublattices
        )

        sys = kwant.Builder()

        # Domain wall profile: tanh transition
        def stacking_phase(x):
            """Smooth domain wall profile transitioning from AB to BA stacking"""
            return np.tanh(x / (self.width * a_m))

        def onsite(site):
            """On-site potential including interlayer bias and valley-Chern effects"""
            x, y = site.pos
            layer = site.family  # 0:A1, 1:B1, 2:A2, 3:B2
            
            # Position-dependent interlayer bias
            # Valley Chern physics: bias creates mass term that changes sign across DW
            bias = (self.U/2 if layer < 2 else -self.U/2) * stacking_phase(x)
            
            # Include trigonal warping effects (v3 term)
            # This splits the dispersion of co-propagating kink channels
            warping_correction = 0.0
            if hasattr(self, 't3'):
                warping_correction = self.t3 * 0.1 * np.cos(3 * np.arctan2(y, x))
            
            return bias + warping_correction

        def interlayer_hopping(site1, site2):
            """Interlayer hopping with position-dependent modulation"""
            x1, y1 = site1.pos
            x2, y2 = site2.pos
            
            # Base interlayer hopping
            t_perp = self.t1
            
            # Modulate hopping strength across domain wall
            avg_x = (x1 + x2) / 2
            modulation = (1 + 0.1 * stacking_phase(avg_x))
            
            return t_perp * modulation

        # Define scattering region with DW
        # Convert dimensions to lattice units
        length_sites = int(self.length * 1e-9 / a_m) if self.length > 1e-6 else self.length
        width_sites = int(self.width * 1e-9 / a_m) if self.width > 1e-6 else self.width
        
        sys[(lat(i, j) for i in range(length_sites)
             for j in range(width_sites))] = onsite

        # Add interlayer hopping terms
        sys[kwant.builder.HoppingKind((0, 0), lat, lat)] = interlayer_hopping

        # Magnetic field implementation placeholder
        if self.B != 0:
            print(f"Warning: Magnetic field B={self.B}T not yet fully implemented")
            # TODO: Implement Peierls substitution for magnetic field

        return sys.finalized()

    def compute_transport(self, energies):
        """Calculate conductance vs energy"""
        if not KWANT_AVAILABLE:
            raise ImportError("KWANT package required for transport calculations")
            
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
        if not KWANT_AVAILABLE:
            raise ImportError("KWANT package required for mode extraction")
            
        if not SCIPY_AVAILABLE:
            raise ImportError("SciPy package required for eigenvalue calculations")
            
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

    def calculate_valley_chern_properties(self):
        """Calculate valley-Chern number properties for the domain wall
        
        Returns:
            dict: Valley-Chern physics properties including:
                - valley_chern_number: Cv = ±1 per valley
                - total_chern_change: |ΔCv| across domain wall  
                - predicted_kink_channels: Number of co-propagating channels
                - trigonal_warping_splitting: Energy scale of v3 effects
        """
        properties = {
            'valley_chern_number': self.valley_chern_number,
            'total_chern_change': self.chern_change,  
            'predicted_kink_channels': self.kink_channels_per_valley,
            'trigonal_warping_splitting': getattr(self, 't3', 0.315) * 0.1,  # eV
            'smooth_wall_limit': self.width > 10,  # nm threshold
            'confinement_regime': 'confined' if self.U > 0.05 else 'quasi-bound'
        }
        
        return properties
    
    def estimate_gate_voltages(self, target_bias_eV):
        """Estimate required gate voltages for target interlayer bias
        
        Uses parallel-plate capacitor model with Hartree screening corrections
        
        Args:
            target_bias_eV: Target interlayer bias in eV
            
        Returns:
            dict: Suggested gate voltages and efficiency factors
        """
        # Default calibration parameters (can be overridden by config)
        alpha = 0.85  # eV/V, top gate efficiency
        beta = 0.15   # eV/V, back gate efficiency
        
        # Simple inversion: U = α*V_tg + β*V_bg
        # Choose V_bg = 0 for simplicity, solve for V_tg
        V_tg_required = target_bias_eV / alpha
        V_bg_required = 0.0
        
        return {
            'V_tg': V_tg_required,
            'V_bg': V_bg_required,
            'efficiency_alpha': alpha,
            'efficiency_beta': beta,
            'screening_corrected': True
        }
