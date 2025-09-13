"""
Test suite for BLG domain wall physics implementation

Tests valley-Chern properties, interlayer bias calibration,
and basic transport simulation functionality.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'simulations'))

import unittest
import numpy as np
from dw_transport import BLG_DW_System


class TestBLGPhysics(unittest.TestCase):
    """Test bilayer graphene domain wall physics"""
    
    def setUp(self):
        """Set up test system"""
        self.system = BLG_DW_System(width=10, length=100, U_bias=0.1)
    
    def test_valley_chern_properties(self):
        """Test valley-Chern number calculations"""
        props = self.system.calculate_valley_chern_properties()
        
        # Check valley-Chern number per valley
        self.assertEqual(props['valley_chern_number'], 1)
        
        # Check total Chern change across domain wall
        self.assertEqual(props['total_chern_change'], 2)
        
        # Check predicted kink channels  
        self.assertEqual(props['predicted_kink_channels'], 2)
        
        # Check trigonal warping energy scale
        self.assertAlmostEqual(props['trigonal_warping_splitting'], 0.0315, places=4)
    
    def test_gate_voltage_estimation(self):
        """Test interlayer bias calibration"""
        target_bias = 0.1  # eV
        voltages = self.system.estimate_gate_voltages(target_bias)
        
        # Check voltage estimation
        self.assertAlmostEqual(voltages['V_tg'], target_bias / 0.85, places=3)
        self.assertEqual(voltages['V_bg'], 0.0)
        
        # Check efficiency factors
        self.assertAlmostEqual(voltages['efficiency_alpha'], 0.85, places=2)
        self.assertAlmostEqual(voltages['efficiency_beta'], 0.15, places=2)
        
    def test_system_initialization(self):
        """Test basic system parameters"""
        # Check material parameters
        self.assertAlmostEqual(self.system.t0, 2.7, places=1)
        self.assertAlmostEqual(self.system.t1, 0.4, places=1)
        
        # Check device parameters
        self.assertEqual(self.system.width, 10)
        self.assertEqual(self.system.length, 100) 
        self.assertAlmostEqual(self.system.U, 0.1, places=1)
        
    def test_confinement_regime_classification(self):
        """Test classification of confined vs quasi-bound regimes"""
        # Test confined regime (high bias)
        system_confined = BLG_DW_System(U_bias=0.1)
        props_confined = system_confined.calculate_valley_chern_properties()
        self.assertEqual(props_confined['confinement_regime'], 'confined')
        
        # Test quasi-bound regime (low bias)
        system_quasi = BLG_DW_System(U_bias=0.01)
        props_quasi = system_quasi.calculate_valley_chern_properties()
        self.assertEqual(props_quasi['confinement_regime'], 'quasi-bound')
        
    def test_smooth_wall_limit(self):
        """Test smooth wall limit classification"""
        # Wide wall (smooth limit)
        system_wide = BLG_DW_System(width=20)
        props_wide = system_wide.calculate_valley_chern_properties()
        self.assertTrue(props_wide['smooth_wall_limit'])
        
        # Narrow wall (not smooth limit)
        system_narrow = BLG_DW_System(width=5)
        props_narrow = system_narrow.calculate_valley_chern_properties()
        self.assertFalse(props_narrow['smooth_wall_limit'])


class TestConfigurationLoading(unittest.TestCase):
    """Test YAML configuration loading"""
    
    def test_config_file_structure(self):
        """Test that default config file has correct structure"""
        config_path = os.path.join(
            os.path.dirname(__file__), '..', 'config', 'default_device.yaml'
        )
        
        # Check if config file exists
        self.assertTrue(os.path.exists(config_path))
        
        # Test loading with config (requires yaml package)
        try:
            system = BLG_DW_System(config_path=config_path)
            self.assertIsNotNone(system)
        except ImportError:
            # Skip if yaml not available
            self.skipTest("PyYAML not available")


if __name__ == '__main__':
    # Run tests
    unittest.main(verbosity=2)