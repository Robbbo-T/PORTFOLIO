"""Template for MAL hardware- and software-in-the-loop validation.

Usage:
    * Subclass :class:`BaseMALHarness` with domain-specific wiring that can
      start the controller, inject stimuli, and collect deterministic telemetry.
    * Subclass :class:`MALHilSILTestTemplate` in your test suite and set the
      ``harness_cls`` attribute to your custom harness.
    * Point ``manifest_path`` to the MAL manifest used for the test article.

The default implementation skips the tests until a concrete harness is
provided, making it safe to keep this template in repositories without
immediately executing HIL/SIL runs.
"""
from __future__ import annotations

import abc
import statistics
import unittest
from dataclasses import dataclass
from pathlib import Path
from typing import Any, ClassVar, Mapping, MutableMapping, Optional, Sequence, Type

import yaml


@dataclass
class CycleObservation:
    """Telemetry for a single MAL scan cycle."""

    index: int
    duration_ms: float
    jitter_ms: float
    mode: str
    fences_state: Mapping[str, bool]
    telemetry: Mapping[str, Any]


class BaseMALHarness(abc.ABC):
    """Contract for domain-specific MAL test harnesses."""

    def __init__(self, manifest: Mapping[str, Any]):
        self.manifest = manifest

    @abc.abstractmethod
    def reset(self) -> None:
        """Reset the controller under test to a known state."""

    @abc.abstractmethod
    def collect_cycles(self, count: int) -> Sequence[CycleObservation]:
        """Collect deterministic cycle telemetry for ``count`` iterations."""

    @abc.abstractmethod
    def induce_fence_trip(self, fence_name: str) -> CycleObservation:
        """Trigger the named fence and return the resulting cycle telemetry."""


class MALHilSILTestTemplate(unittest.TestCase):
    """Reusable determinism and safety assertions for MAL controllers."""

    harness_cls: ClassVar[Optional[Type[BaseMALHarness]]] = None
    manifest_path: ClassVar[Path] = Path("manifest.yaml")
    cycles_to_sample: ClassVar[int] = 50
    fence_to_test: ClassVar[Optional[str]] = None

    manifest: ClassVar[Mapping[str, Any]]
    harness: ClassVar[BaseMALHarness]

    @classmethod
    def setUpClass(cls) -> None:  # pylint: disable=missing-function-docstring
        super().setUpClass()
        if cls.harness_cls is None:
            raise unittest.SkipTest("Set MALHilSILTestTemplate.harness_cls to a BaseMALHarness subclass")
        if not cls.manifest_path.exists():
            raise unittest.SkipTest(f"Manifest file not found at {cls.manifest_path}")
        with cls.manifest_path.open("r", encoding="utf-8") as handle:
            manifest = yaml.safe_load(handle)
        if not isinstance(manifest, MutableMapping) or "mal" not in manifest:
            raise unittest.SkipTest("Manifest is not valid or missing 'mal' root")
        cls.manifest = manifest
        cls.harness = cls.harness_cls(cls.manifest)
        cls.harness.reset()

    def test_cycle_duration_within_deadline(self) -> None:
        """All sampled cycles complete within the declared deadline."""

        cycle_cfg = self.manifest["mal"]["cycle"]
        observations = self.harness.collect_cycles(self.cycles_to_sample)
        if not observations:
            self.skipTest("Harness returned no observations")
        deadline = float(cycle_cfg["deadline_ms"])
        overruns = [obs for obs in observations if obs.duration_ms > deadline + 1e-9]
        self.assertFalse(
            overruns,
            msg=f"Found cycle overruns beyond deadline {deadline}ms: {overruns}",
        )

    def test_cycle_jitter_within_bounds(self) -> None:
        """Recorded jitter remains inside the manifest budget."""

        cycle_cfg = self.manifest["mal"]["cycle"]
        observations = self.harness.collect_cycles(self.cycles_to_sample)
        if not observations:
            self.skipTest("Harness returned no observations")
        jitter_bound = float(cycle_cfg["jitter_max_ms"])
        excess = [obs for obs in observations if obs.jitter_ms > jitter_bound + 1e-9]
        self.assertFalse(
            excess,
            msg=f"Observed jitter beyond {jitter_bound}ms: {excess}",
        )

    def test_deterministic_fields_present(self) -> None:
        """Telemetry payload exposes the deterministic contract."""

        required = set(self.manifest["mal"]["telemetry"]["deterministic_fields"])
        observations = self.harness.collect_cycles(max(1, self.cycles_to_sample // 5))
        if not observations:
            self.skipTest("Harness returned no observations")
        missing_per_cycle = []
        for obs in observations:
            missing = required.difference(obs.telemetry.keys())
            if missing:
                missing_per_cycle.append((obs.index, sorted(missing)))
        self.assertFalse(
            missing_per_cycle,
            msg=f"Missing deterministic telemetry fields: {missing_per_cycle}",
        )

    def test_modes_reported_are_known(self) -> None:
        """Harness should only report modes declared in the manifest."""

        allowed_modes = set(self.manifest["mal"]["modes"])
        observations = self.harness.collect_cycles(self.cycles_to_sample)
        if not observations:
            self.skipTest("Harness returned no observations")
        unexpected = [obs for obs in observations if obs.mode not in allowed_modes]
        self.assertFalse(
            unexpected,
            msg=f"Encountered modes outside manifest contract: {unexpected}",
        )

    def test_fence_trip_transitions_to_safe_mode(self) -> None:
        """Trigger one fence and verify the controller enters its trip mode."""

        fences = self.manifest["mal"]["fences"]
        if not fences:
            self.skipTest("Manifest does not declare any fences")
        fence_name = self.fence_to_test or fences[0]["name"]
        fence_cfg = next((f for f in fences if f["name"] == fence_name), None)
        if fence_cfg is None:
            self.skipTest(f"Fence '{fence_name}' not found in manifest")
        observation = self.harness.induce_fence_trip(fence_name)
        self.assertEqual(
            fence_cfg["trip_mode"],
            observation.mode,
            msg=f"Fence '{fence_name}' did not transition to trip mode {fence_cfg['trip_mode']}",
        )
        if observation.fences_state:
            self.assertFalse(
                observation.fences_state.get(fence_name, True),
                msg=f"Fence '{fence_name}' state did not indicate a trip",
            )

    def test_cycle_statistics_recorded(self) -> None:
        """Ensure jitter/latency statistics are available for offline evidence."""

        observations = self.harness.collect_cycles(self.cycles_to_sample)
        if len(observations) < 5:
            self.skipTest("Need at least 5 observations to compute statistics")
        latencies = [obs.duration_ms for obs in observations]
        jitters = [obs.jitter_ms for obs in observations]
        self.assertGreater(statistics.mean(latencies), 0.0, "Mean latency should be positive")
        self.assertGreaterEqual(min(jitters), 0.0, "Jitter cannot be negative")
        self.assertGreaterEqual(max(jitters), 0.0, "Jitter cannot be negative")


__all__ = [
    "CycleObservation",
    "BaseMALHarness",
    "MALHilSILTestTemplate",
]
