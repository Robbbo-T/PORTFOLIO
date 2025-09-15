#!/usr/bin/env python3
from dataclasses import dataclass, field
from typing import Dict, Set, Tuple, List, Callable, Optional, Iterable
from collections import deque, defaultdict
import json
import sys
import re

Layer = str
Domain = str
NodeT = Tuple[Domain, Layer]

STRICT_TFA_REGEX = re.compile(
    r"^2-DOMAINS-LEVELS/(?P<dom>[A-Z]{3})-[A-Z0-9-]+/TFA/(?P<group>[A-Z]+)/(?P<llc>[A-Z0-9-]+)/"
)

@dataclass(frozen=True)
class ArtifactID:
    raw: str  # UTCS–MI identifier string

@dataclass
class Artifact:
    mu: ArtifactID
    tau: str
    lam: NodeT
    content_score: int = 0
    root: bool = False
    path: Optional[str] = None  # optional: actual repo path for STRICT TFA-ONLY

@dataclass
class TFARepo:
    D: Set[Domain]
    L: List[Layer]
    T: Set[NodeT]
    A: Dict[str, Artifact]
    E: Set[Tuple[str, str]]
    X: Set[Tuple[str, str]]
    need_readme_nodes: Set[NodeT] = field(default_factory=set)
    parse_fn: Optional[Callable[[str], bool]] = None
    quantum_layers_required: List[str] = field(default_factory=lambda: ["CB","QB","UE","FE","FWD","QS"])

    def __post_init__(self):
        self.level_index = {layer: i for i, layer in enumerate(self.L)}

    # ---------- orden ----------
    def preceq(self, t1: NodeT, t2: NodeT) -> bool:
        (d1, l1), (d2, l2) = t1, t2
        return (d1 == d2) and (self.level_index[l1] <= self.level_index[l2])

    # ---------- grafos ----------
    def neighbors_union(self, aid: str) -> Iterable[str]:
        for u, v in self.E:
            if u == aid:
                yield v
        for u, v in self.X:
            if u == aid:
                yield v

    def reach(self, src_id: str, target_t: NodeT) -> bool:
        goals = {aid for aid, a in self.A.items() if a.lam == target_t}
        if not goals:
            return False
        seen = {src_id}
        q = deque([src_id])
        while q:
            u = q.popleft()
            if u in goals:
                return True
            for v in self.neighbors_union(u):
                if v not in seen:
                    seen.add(v)
                    q.append(v)
        return False

    # ---------- validadores V1..V5 ----------
    def V1(self, a: Artifact) -> bool:
        if self.parse_fn is None:
            s = a.mu.raw
            return bool(s) and all(ch.isalnum() or ch in "-_:.#/" for ch in s)
        return bool(self.parse_fn(a.mu.raw))

    def V2(self, a: Artifact) -> bool:
        return a.lam in self.T

    def V3(self, a: Artifact) -> bool:
        if a.root:
            return True
        for b_id, a_id in self.E:
            if a_id == a.mu.raw and b_id != a.mu.raw:
                b = self.A.get(b_id)
                if b and self.preceq(b.lam, a.lam):
                    return True
        return False

    def V4(self, a: Artifact) -> bool:
        aid = a.mu.raw
        for u, v in self.X:
            if (u == aid and v != aid) or (v == aid and u != aid):
                return True
        return False

    def V5(self, a: Artifact) -> int:
        return int(max(0, min(2, a.content_score)))

    # ---------- métrica Φ ----------
    def phi_components(self):
        orph = sum(1 for a in self.A.values() if not self.V3(a))
        nox = sum(1 for a in self.A.values() if not self.V4(a))
        badID = sum(1 for a in self.A.values() if not self.V1(a))
        empties = sum(1 for a in self.A.values() if self.V5(a) == 0)
        partials = sum(1 for a in self.A.values() if self.V5(a) == 1)
        return dict(orph=orph, nox=nox, badID=badID, empties=empties, partials=partials)

    def Phi(self, alpha=1000, beta=200, gamma=40, delta=5, epsilon=1):
        c = self.phi_components()
        return alpha*c["orph"] + beta*c["nox"] + gamma*c["badID"] + delta*c["empties"] + epsilon*c["partials"]

    # ---------- TTA ----------
    def greedy_TTA(self) -> Set[str]:
        R = {t: set() for t in self.T}
        for aid in self.A:
            for t in self.T:
                if self.reach(aid, t):
                    R[t].add(aid)
        uncovered = {t for t in self.T if R[t]}
        S: Set[str] = set()
        while uncovered:
            best, gain = None, -1
            for aid in self.A:
                g = sum(1 for t in uncovered if aid in R[t])
                if g > gain:
                    best, gain = aid, g
            if best is None or gain <= 0:
                break
            S.add(best)
            uncovered = {t for t in uncovered if best not in R[t]}
        return S

    def coverage(self, S: Set[str]):
        def c_one(t):
            return 1 if any(self.reach(s, t) for s in S) else 0
        return {t: c_one(t) for t in self.T}

    # ---------- checks extra ----------
    def strict_tfa_only_check(self) -> List[str]:
        """Si los artifacts tienen 'path', verificamos el patrón canónico y consistencia dom=λ.dom."""
        errors = []
        for a in self.A.values():
            if not a.path:
                continue
            m = STRICT_TFA_REGEX.match(a.path)
            if not m:
                errors.append(f"STRICT-TFA: path inválido para μ={a.mu.raw}: {a.path}")
                continue
            dom_from_path = m.group("dom")
            if dom_from_path != a.lam[0]:
                errors.append(f"STRICT-TFA: dom(path)={dom_from_path} != dom(λ)={a.lam[0]} for μ={a.mu.raw}")
        return errors

    def quantum_layers_check(self) -> List[str]:
        """Exige presencia de al menos un artifact por capa requerida."""
        present = defaultdict(int)
        for a in self.A.values():
            d, l = a.lam
            present[l] += 1
        missing = [layer for layer in self.layer_aliases_to_L(self.quantum_layers_required) if present[layer] == 0]
        return [f"Quantum layer missing: {m}" for m in missing]

    def layer_aliases_to_L(self, req: List[str]) -> List[str]:
        alias = {
            "CB": "BITS",
            "QB": "QUBITS",
            "UE": "ELEMENTS",
            "FE": "ELEMENTS",
            "FWD": "WAVES",
            "QS": "STATES"
        }
        mapped = []
        for r in req:
            Lr = alias.get(r, r)
            if Lr in self.level_index:
                mapped.append(Lr)
        return list(dict.fromkeys(mapped))  # unique, keep order

# ----------- CLI -----------
def load_repo_from_json(json_path: str) -> TFARepo:
    with open(json_path, "r", encoding="utf-8") as f:
        J = json.load(f)
    D = set(J["D"])
    L = list(J["L"])
    T = set(tuple(x) for x in J["T"])
    A = {}
    for obj in J["A"]:
        A[obj["mu"]] = Artifact(
            mu=ArtifactID(obj["mu"]),
            tau=obj["tau"],
            lam=tuple(obj["lambda"]),  # type: ignore
            content_score=obj.get("content_score", 0),
            root=obj.get("root", False),
            path=obj.get("path")
        )
    E = set(tuple(x) for x in J["E"])
    X = set(tuple(x) for x in J["X"])
    need = set(tuple(x) for x in J.get("need_readme_nodes", []))
    quantum_req = J.get("R", {}).get("quantum_layers_required", ["CB","QB","UE","FE","FWD","QS"])
    return TFARepo(D, L, T, A, E, X, need, None, quantum_req)

def main():
    if len(sys.argv) < 2:
        print("usage: tfa_tta_validator.py <tfa.repo.json> [--fail-nonzero]")
        sys.exit(2)
    repo = load_repo_from_json(sys.argv[1])

    # V-reports
    v_counts = defaultdict(int)
    for a in repo.A.values():
        v_counts["V1_ok"] += int(repo.V1(a))
        v_counts["V2_ok"] += int(repo.V2(a))
        v_counts["V3_ok"] += int(repo.V3(a))
        v_counts["V4_ok"] += int(repo.V4(a))
        v_counts[f"V5_{repo.V5(a)}"] += 1

    phi_comp = repo.phi_components()
    phi_val = repo.Phi()

    # TTA
    S = repo.greedy_TTA()
    cov = repo.coverage(S)
    cov_ratio = sum(cov.values()) / max(1, len(cov))

    # Extra checks
    strict_errors = repo.strict_tfa_only_check()
    q_errors = repo.quantum_layers_check()

    # Need README
    missing_readmes = []
    by_node = defaultdict(list)
    for a in repo.A.values():
        by_node[a.lam].append(a)
    for t in repo.need_readme_nodes:
        if not any(a.tau == "README" for a in by_node.get(t, [])):
            missing_readmes.append(t)

    # Report
    print("=== TFA/TTA REPORT ===")
    print(f"|A|={len(repo.A)} |T|={len(repo.T)} layers={repo.L}")
    print("Validators:", dict(v_counts))
    print("Phi components:", phi_comp)
    print("Phi:", phi_val)
    print("TTA greedy |S|:", len(S), "S=", sorted(S))
    print("Coverage ratio:", f"{cov_ratio:.3f}")
    if strict_errors:
        print("STRICT-TFA violations:")
        for e in strict_errors: print(" -", e)
    if q_errors:
        print("Quantum layers check:")
        for e in q_errors: print(" -", e)
    if missing_readmes:
        print("Missing READMEs at nodes:", [str(t) for t in missing_readmes])

    fail = ("--fail-nonzero" in sys.argv)
    exit_code = 0
    if phi_comp["orph"] or strict_errors or q_errors or missing_readmes:
        exit_code = 1 if fail else 0
    sys.exit(exit_code)

if __name__ == "__main__":
    main()
