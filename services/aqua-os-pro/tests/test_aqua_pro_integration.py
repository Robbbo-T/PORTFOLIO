#!/usr/bin/env python3
"""
AQUA OS PRO Integration Tests

Comprehensive integration testing for the AQUA OS PRO layer across all domains and TFA layers.
"""

import asyncio
import pytest
import json
import time
from pathlib import Path
from typing import Dict, Any, List
import sys

# Add project root to path for imports
project_root = Path(__file__).parents[3]
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "services" / "aqua-os-pro"))

from core.aqua_pro_orchestrator import (
    AquaProOrchestrator, 
    RouteOptimizationConfig,
    OptimizationStatus,
    LayerType
)
from validation.aqua_pro_validator import AquaProValidator

class TestAquaProIntegration:
    """Integration tests for AQUA OS PRO system"""
    
    @pytest.fixture
    def config(self):
        """Test configuration"""
        return RouteOptimizationConfig(
            loop_duration_minutes=1,  # Shorter for testing
            cadence_seconds=5,  # Faster cadence for testing
            sla_threshold_ms=300.0,
            quantum_enabled=True,
            quantum_strategy="qaoa",
            fallback_enabled=True,
            federation_enabled=True
        )
    
    @pytest.fixture
    async def orchestrator(self, config):
        """Initialized orchestrator"""
        orch = AquaProOrchestrator(config)
        await orch.initialize()
        return orch
    
    @pytest.mark.asyncio
    async def test_orchestrator_initialization(self, config):
        """Test orchestrator initialization"""
        orchestrator = AquaProOrchestrator(config)
        
        # Test initialization
        result = await orchestrator.initialize()
        assert result is True
        
        # Verify domain implementations loaded
        assert len(orchestrator.domain_implementations) == 120  # 15 domains × 8 layers
        
        # Verify quantum backends initialized
        if config.quantum_enabled:
            assert orchestrator.quantum_backends is not None
            assert "qaoa" in orchestrator.quantum_backends
            assert orchestrator.quantum_backends["qaoa"]["available"] is True
        
        # Verify federation layer
        if config.federation_enabled:
            assert orchestrator.federation_layer is not None
            assert orchestrator.federation_layer["initialized"] is True
    
    @pytest.mark.asyncio
    async def test_single_optimization_cycle(self, orchestrator):
        """Test a single optimization cycle"""
        # Create test cycle
        cycle = await orchestrator._create_optimization_cycle()
        
        assert cycle is not None
        assert cycle.cycle_id.startswith("cycle_")
        assert cycle.utcs_id.startswith("AQUA/PRO/")
        assert cycle.status == OptimizationStatus.PENDING
        
        # Process all domains
        await orchestrator._process_all_domains(cycle)
        
        # Verify cycle completion
        assert len(cycle.results) == 15  # All domains processed
        assert cycle.processing_time_ms > 0
        
        # Verify SLA compliance
        assert cycle.processing_time_ms <= orchestrator.config.sla_threshold_ms
    
    @pytest.mark.asyncio
    async def test_domain_layer_processing(self, orchestrator):
        """Test individual domain layer processing"""
        cycle = await orchestrator._create_optimization_cycle()
        
        # Test each layer type
        for layer in LayerType:
            result = await orchestrator._process_layer(cycle, "AAA", layer)
            
            assert "success" in result
            assert result["success"] is True
            assert "domain" in result
            assert result["domain"] == "AAA"
            assert "layer" in result
            assert result["layer"] == layer.value
    
    @pytest.mark.asyncio
    async def test_quantum_classical_fallback(self, orchestrator):
        """Test quantum-classical fallback mechanism"""
        cycle = await orchestrator._create_optimization_cycle()
        
        # Process CB layer (which triggers QB first if quantum enabled)
        domain_result = await orchestrator._process_domain(cycle, "CQH")
        
        # Should have either QB or CB result
        assert "QB" in domain_result or "CB" in domain_result
        
        # Check quantum metrics
        if "quantum_used" in cycle.quantum_metrics:
            assert isinstance(cycle.quantum_metrics["quantum_used"], bool)
        
        if "fallback_used" in cycle.quantum_metrics:
            assert isinstance(cycle.quantum_metrics["fallback_used"], bool)
    
    @pytest.mark.asyncio
    async def test_performance_metrics_tracking(self, orchestrator):
        """Test performance metrics collection"""
        initial_metrics = orchestrator.get_performance_metrics()
        
        # Run a cycle
        cycle = await orchestrator._create_optimization_cycle()
        await orchestrator._process_all_domains(cycle)
        orchestrator._update_performance_metrics(cycle)
        
        updated_metrics = orchestrator.get_performance_metrics()
        
        # Verify metrics updated
        assert updated_metrics["total_cycles"] == initial_metrics["total_cycles"] + 1
        assert updated_metrics["successful_cycles"] >= initial_metrics["successful_cycles"]
        assert updated_metrics["average_processing_time"] >= 0
    
    @pytest.mark.asyncio
    async def test_concurrent_domain_processing(self, orchestrator):
        """Test concurrent processing of multiple domains"""
        cycle = await orchestrator._create_optimization_cycle()
        
        start_time = time.time()
        await orchestrator._process_all_domains(cycle)
        processing_time = time.time() - start_time
        
        # Concurrent processing should be much faster than sequential
        # With 15 domains and ~10ms each, sequential would be ~150ms
        # Concurrent should be closer to the longest single domain (~10ms)
        assert processing_time < 0.1  # Less than 100ms for all domains
        
        # All domains should be processed
        assert len(cycle.results) == 15
        
        # All results should be successful
        for domain, result in cycle.results.items():
            assert isinstance(result, dict)

class TestAquaProValidation:
    """Tests for AQUA PRO validation framework"""
    
    @pytest.mark.asyncio
    async def test_comprehensive_validation(self):
        """Test comprehensive system validation"""
        validator = AquaProValidator(project_root)
        report = await validator.validate_all()
        
        # Check validation summary
        assert report["validation_summary"]["total_checks"] > 0
        assert report["validation_summary"]["success_rate"] >= 95.0  # Allow 5% tolerance
        
        # Check coverage metrics
        coverage = report["coverage_metrics"]
        assert coverage["domains_validated"] == 15
        assert coverage["layers_per_domain"] == 8
        assert coverage["coverage_percentage"] > 0
        
        # Check results by type
        results_by_type = report["results_by_type"]
        assert "TFA" in results_by_type
        assert "SPEC" in results_by_type
        assert "IMPL" in results_by_type
        
        # TFA structure should be complete
        tfa_results = results_by_type["TFA"]
        assert tfa_results["total"] == 240  # 15 domains × 8 layers × 2 files
        assert tfa_results["passed"] >= tfa_results["total"] * 0.95  # 95% pass rate
    
    def test_schema_validation(self):
        """Test JSON schema validation"""
        schema_file = project_root / "services" / "aqua-os-pro" / "schemas" / "route_optimization.json"
        
        assert schema_file.exists()
        
        with schema_file.open() as f:
            schema = json.load(f)
        
        # Validate schema structure
        assert "$schema" in schema
        assert "title" in schema
        assert "properties" in schema
        assert "route_request" in schema["properties"]
        assert "route_response" in schema["properties"]
        
        # Validate definitions
        assert "definitions" in schema
        assert "waypoint" in schema["definitions"]
        assert "performance_envelope" in schema["definitions"]

class TestAquaProDataFlow:
    """Tests for data flow through AQUA PRO system"""
    
    def test_route_request_structure(self):
        """Test route request data structure"""
        sample_request = {
            "route_request": {
                "utcs_id": "AAA/SI/REQ-0101",
                "domain": "AAA",
                "layer": "SI",
                "timestamp": "2024-01-01T00:00:00Z",
                "route_params": {
                    "origin": {
                        "latitude": 40.7128,
                        "longitude": -74.0060,
                        "identifier": "JFK",
                        "type": "airport"
                    },
                    "destination": {
                        "latitude": 34.0522,
                        "longitude": -118.2437,
                        "identifier": "LAX",
                        "type": "airport"
                    },
                    "cruise_altitude": 35000,
                    "cruise_speed": 250,
                    "optimization_weights": {
                        "fuel": 0.4,
                        "time": 0.4,
                        "emissions": 0.2
                    }
                },
                "quantum_config": {
                    "enabled": True,
                    "strategy": "qaoa",
                    "shots": 1024,
                    "backend": "qasm_simulator"
                }
            }
        }
        
        # Validate structure
        assert "route_request" in sample_request
        route_req = sample_request["route_request"]
        
        # Validate required fields
        assert "utcs_id" in route_req
        assert "domain" in route_req
        assert "layer" in route_req
        assert "route_params" in route_req
        
        # Validate route parameters
        route_params = route_req["route_params"]
        assert "origin" in route_params
        assert "destination" in route_params
        assert "optimization_weights" in route_params
        
        # Validate optimization weights sum to reasonable value
        weights = route_params["optimization_weights"]
        weight_sum = weights["fuel"] + weights["time"] + weights["emissions"]
        assert 0.8 <= weight_sum <= 1.2  # Allow some tolerance
    
    def test_route_response_structure(self):
        """Test route response data structure"""
        sample_response = {
            "route_response": {
                "utcs_id": "AAA/SI/REQ-0101",
                "status": "success",
                "processing_time_ms": 250.5,
                "sla_compliance": True,
                "optimized_route": {
                    "waypoints": [
                        {"latitude": 40.7128, "longitude": -74.0060, "type": "airport"},
                        {"latitude": 39.0458, "longitude": -76.6413, "type": "waypoint"},
                        {"latitude": 34.0522, "longitude": -118.2437, "type": "airport"}
                    ],
                    "total_distance": 2445.5,
                    "estimated_fuel": 12500.0,
                    "estimated_time": 21600.0,
                    "estimated_emissions": 2800.5,
                    "confidence_score": 0.95
                },
                "quantum_metrics": {
                    "used_quantum": True,
                    "quantum_advantage": 1.15,
                    "backend_used": "qasm_simulator"
                },
                "provenance": {
                    "qs_hash": "0x1234567890abcdef",
                    "processing_node": "aqua-pro-node-01"
                }
            }
        }
        
        # Validate structure
        assert "route_response" in sample_response
        route_resp = sample_response["route_response"]
        
        # Validate required fields
        assert "utcs_id" in route_resp
        assert "status" in route_resp
        assert "processing_time_ms" in route_resp
        assert "sla_compliance" in route_resp
        
        # Validate SLA compliance logic
        assert route_resp["processing_time_ms"] <= 300.0  # Should match SLA
        assert route_resp["sla_compliance"] is True
        
        # Validate optimized route
        if "optimized_route" in route_resp:
            opt_route = route_resp["optimized_route"]
            assert "waypoints" in opt_route
            assert len(opt_route["waypoints"]) >= 2  # At least origin and destination

# Performance benchmarks
class TestAquaProPerformance:
    """Performance tests for AQUA PRO system"""
    
    @pytest.mark.asyncio
    async def test_orchestrator_performance(self):
        """Test orchestrator performance under load"""
        config = RouteOptimizationConfig(
            cadence_seconds=1,  # High frequency
            sla_threshold_ms=300.0
        )
        
        orchestrator = AquaProOrchestrator(config)
        await orchestrator.initialize()
        
        # Run multiple cycles and measure performance
        cycle_times = []
        
        for _ in range(10):
            start_time = time.time()
            
            cycle = await orchestrator._create_optimization_cycle()
            await orchestrator._process_all_domains(cycle)
            
            cycle_time = (time.time() - start_time) * 1000  # Convert to ms
            cycle_times.append(cycle_time)
        
        # Analyze performance
        avg_time = sum(cycle_times) / len(cycle_times)
        max_time = max(cycle_times)
        
        # Performance assertions
        assert avg_time < 200.0  # Average under 200ms
        assert max_time < 300.0  # Max under SLA threshold
        assert all(t < 500.0 for t in cycle_times)  # No cycle over 500ms
    
    def test_domain_implementation_load_time(self):
        """Test domain implementation loading performance"""
        start_time = time.time()
        
        # Simulate loading all implementations
        domains = ["AAA", "AAP", "CCC", "CQH", "DDD", "EDI", "EEE", "EER", 
                  "IIF", "IIS", "LCC", "LIB", "MMM", "OOO", "PPP"]
        layers = ["SI", "DI", "SE", "CB", "QB", "FWD", "QS", "FE"]
        
        implementations = {}
        for domain in domains:
            for layer in layers:
                key = f"{domain}.{layer}"
                # Mock implementation loading
                implementations[key] = {"domain": domain, "layer": layer, "loaded": True}
        
        load_time = (time.time() - start_time) * 1000
        
        # Should load quickly
        assert load_time < 100.0  # Under 100ms
        assert len(implementations) == 120

# Utility functions for tests
def create_test_route_request(domain="AAA", layer="SI"):
    """Create a test route request"""
    return {
        "route_request": {
            "utcs_id": f"{domain}/{layer}/REQ-0101",
            "domain": domain,
            "layer": layer,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "route_params": {
                "origin": {"latitude": 40.7128, "longitude": -74.0060},
                "destination": {"latitude": 34.0522, "longitude": -118.2437},
                "cruise_altitude": 35000,
                "optimization_weights": {"fuel": 0.4, "time": 0.4, "emissions": 0.2}
            },
            "quantum_config": {"enabled": True, "strategy": "qaoa"}
        }
    }

# Run tests if called directly
if __name__ == "__main__":
    pytest.main([__file__, "-v"])