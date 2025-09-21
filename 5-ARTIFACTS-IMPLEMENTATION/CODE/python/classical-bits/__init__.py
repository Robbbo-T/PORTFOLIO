"""
Classical Bits (CB) - CQEA Decision Kernel Implementation
Aerospace Super-Intelligence Transformers

This module implements the Classical-Quantum Extensible Aerospace (CQEA) 
decision kernel system for aerospace applications.

Main Components:
- DecisionKernel: Core decision execution engine
- RunConfig: Problem configuration 
- CQEARunner: YAML manifest-driven execution
- Solver implementations: MILP, heuristic, QAOA stub

Usage:
    from classical_bits import create_kernel, CQEARunner
    
    kernel = create_kernel()
    runner = CQEARunner(kernel)
    result = runner.execute_run(Path("manifest.yaml"))
"""

from .cqea_kernel import DecisionKernel, RunConfig, create_kernel
from .cqea_runner import CQEARunner, ManifestConfig

__version__ = "1.0.0"
__author__ = "ASI-T Aerospace Engineering Team"

__all__ = [
    "DecisionKernel",
    "RunConfig", 
    "CQEARunner",
    "ManifestConfig",
    "create_kernel"
]