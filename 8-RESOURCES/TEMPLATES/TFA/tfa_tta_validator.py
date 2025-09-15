from dataclasses import dataclass, field
from typing import Dict, Set, Tuple, List, Callable, Optional
from collections import deque

Layer = str
Domain = str
NodeT = Tuple[Domain, Layer]  # element of T ⊆ D × L

@dataclass(frozen=True)
class ArtifactID:
    raw: str  # UTCS–MI identifier string

@dataclass
class Artifact:
    mu: ArtifactID
    tau: str
    lam: NodeT
    content_score: int = 0  # V5: {0,1,2}
    root: bool = False

@dataclass
class TFARepo:
    D: Set[Domain]
    L: List[Layer]                 # ordered layers (coarse→fine)
    T: Set[NodeT]                  # ⊆ D×L
    A: Dict[str, Artifact]         # key = μ.raw
    E: Set[Tuple[str, str]]        # (b -> a)
    X: Set[Tuple[str, str]]        # threading edges
    need_readme_nodes: Set[NodeT] = field(default_factory=set)
    parse_fn: Optional[Callable[[str], bool]] = None

    def __post_init__(self):
        self.level_index = {layer: i for i, layer in enumerate(self.L)}

    # -------- order ----------
    def preceq(self, t1: NodeT, t2: NodeT) -> bool:
        (d1, l1), (d2, l2) = t1, t2
        if d1 != d2:
            return False   # customize if cross-domain order is desired
        return self.level_index[l1] <= self.level_index[l2]

    # -------- graph ----------
    def neighbors_union(self, aid: str):
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

    # -------- validators ----------
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

    # -------- TTA greedy ----------
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
                break  # no hay progreso (desconexión)
            S.add(best)
            newly = {t for t in list(uncovered) if best in R[t]}
            uncovered -= newly
        return S

    def coverage(self, S: Set[str]):
        def c_one(t): 
            return 1 if any(self.reach(s, t) for s in S) else 0
        return {t: c_one(t) for t in self.T}

# ---------------- Demo mínima ----------------
if __name__ == "__main__":
    D = {"AAA", "PPP"}
    L = ["SYSTEMS", "STATIONS", "COMPONENTS", "BITS"]
    T = {(d, l) for d in D for l in L}
    A = {
        "AAA:SYS:overview": Artifact(ArtifactID("AAA:SYS:overview"), "README", ("AAA", "SYSTEMS"), content_score=2, root=True),
        "AAA:COMP:wing_spec": Artifact(ArtifactID("AAA:COMP:wing_spec"), "SPEC", ("AAA", "COMPONENTS"), content_score=1),
        "AAA:BITS:wing_test": Artifact(ArtifactID("AAA:BITS:wing_test"), "TEST", ("AAA", "BITS"), content_score=2),
        "PPP:STN:pipeline": Artifact(ArtifactID("PPP:STN:pipeline"), "CODE", ("PPP", "STATIONS"), content_score=2, root=True),
        "PPP:BITS:util": Artifact(ArtifactID("PPP:BITS:util"), "CODE", ("PPP", "BITS"), content_score=0),
    }
    E = {
        ("AAA:SYS:overview", "AAA:COMP:wing_spec"),
        ("AAA:COMP:wing_spec", "AAA:BITS:wing_test"),
        ("PPP:STN:pipeline", "PPP:BITS:util"),
    }
    X = {
        ("AAA:COMP:wing_spec", "PPP:STN:pipeline"),
        ("PPP:STN:pipeline", "AAA:BITS:wing_test"),
    }
    need_readme_nodes = {("AAA", "COMPONENTS"), ("PPP", "STATIONS")}

    repo = TFARepo(D, L, T, A, E, X, need_readme_nodes)

    print("Φ components:", repo.phi_components())
    print("Φ =", repo.Phi())
    S = repo.greedy_TTA()
    print("Greedy TTA S:", S)
    print("Coverage:", {str(k): v for k, v in repo.coverage(S).items()})
