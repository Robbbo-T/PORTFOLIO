#!/usr/bin/env python3
"""
Classify working links into: placeholder | template-structured | contentful-doc | contentful-code.
- Reads Lychee JSON (working links + sources).
- Evaluates only internal repo targets (markdown/html/code under provided roots).
- Uses heuristics first; optionally calls an LLM for borderline/override.
"""
from __future__ import annotations
import os, re, json, argparse
from pathlib import Path

# ---------- Heuristics ----------
PLACEHOLDER_PATTERNS = [
    r"\bTBD\b", r"\bTODO\b", r"\bWIP\b", r"lorem ipsum",
    r"\{\{[A-Z0-9_ -]+\}\}",  # mustache tokens
    r"\$[A-Z0-9_]+",          # $PLACEHOLDER
]
TEMPLATE_SECTION_HINTS = [
    "overview", "purpose", "scope", "interfaces", "usage", "compliance", "standards", "change log", "author"
]

CODE_SIGNS = [
    r"^```[a-zA-Z0-9_+-]*\n",            # fenced code
    r"^\s*(import |from .+ import)",     # imports
    r"^\s*class\s+\w+[:(]",              # classes
    r"^\s*def\s+\w+\(",                   # functions
]

def read_file(path: Path, limit_chars=20000) -> str:
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
        return text[:limit_chars]
    except Exception:
        return ""

def is_probably_code(path: Path, text: str) -> bool:
    if path.suffix in {".py",".rs",".c",".cpp",".h",".hpp",".sv",".vhd",".jl",".go",".ts",".js",".sh",".yml",".yaml"}:
        return True
    if re.search(CODE_SIGNS[0], text, flags=re.M):
        return True
    return False

def heuristics_classify(path: Path, text: str) -> tuple[str, float, list[str]]:
    reasons = []
    words = len(re.findall(r"\w+", text))
    heads = len(re.findall(r"^#{1,6}\s", text, flags=re.M))
    codef = len(re.findall(r"^```", text, flags=re.M))

    # Placeholder?
    ph_hits = sum(bool(re.search(p, text, flags=re.I)) for p in PLACEHOLDER_PATTERNS)
    if ph_hits and words < 250:
        reasons.append(f"placeholder tokens={ph_hits}, words={words}")
        return ("placeholder", 0.9, reasons)

    # Template-structured?
    sec_hits = sum(h in text.lower() for h in TEMPLATE_SECTION_HINTS)
    if sec_hits >= 3 and ph_hits == 0 and words < 800:
        reasons.append(f"template sections={sec_hits}, words={words}")
        return ("template-structured", 0.7, reasons)

    # Code?
    if is_probably_code(path, text):
        reasons.append(f"code fences={codef}, suffix={path.suffix}")
        return ("contentful-code", 0.8, reasons)

    # Contentful doc?
    if words >= 300 and heads >= 2:
        reasons.append(f"words={words}, headings={heads}")
        return ("contentful-doc", 0.8, reasons)

    # Fallback
    reasons.append(f"weak-signal words={words}, heads={heads}, codef={codef}")
    return ("template-structured", 0.5, reasons)

# ---------- Optional LLM refinement ----------
def llm_refine(label: str, path: Path, text: str) -> tuple[str,float,str]:
    if os.getenv("USE_LLM","false").lower() != "true":
        return label, 0.0, "LLM disabled"

    provider = os.getenv("LLM_PROVIDER","openai").lower()
    model = os.getenv("OPENAI_MODEL","gpt-4o-mini")

    snippet = text[:6000]
    prompt = f"""
You are a rigorous aerospace-doc/code auditor. Classify the file into one label:
- placeholder: boilerplate, TODOs, tokens like {{VAR}} or $PLACEHOLDER
- template-structured: sections exist (overview/usage/etc.) but missing domain-specific substance
- contentful-doc: substantial domain-specific prose/specs/interfaces/requirements
- contentful-code: substantial source code/tests/configuration files

Return JSON ONLY: {{"label":"...","confidence":0..1,"reasons":"...","score":0..100}}
Path: {path.as_posix()}
Content:
```

{snippet}

```"""

    try:
        if provider == "openai":
            import requests
            key = os.getenv("OPENAI_API_KEY","")
            if not key: return label, 0.0, "OPENAI_API_KEY missing"
            url = "https://api.openai.com/v1/chat/completions"
            headers = {"Authorization": f"Bearer {key}","Content-Type":"application/json"}
            payload = {"model": model, "messages":[{"role":"user","content":prompt}], "temperature": 0}
            r = requests.post(url, headers=headers, json=payload, timeout=30)
            r.raise_for_status()
            content = r.json()["choices"][0]["message"]["content"]
        elif provider == "anthropic":
            # Minimal example; wire up as needed
            return label, 0.0, "Anthropic provider stub"
        else:
            return label, 0.0, "Unknown provider"
        # parse JSON block
        m = re.search(r"\{.*\}", content, flags=re.S)
        if not m: return label, 0.0, "LLM no JSON"
        out = json.loads(m.group(0))
        return out.get("label",label), float(out.get("confidence",0.0)), out.get("reasons","")
    except Exception as e:
        return label, 0.0, f"LLM error: {e}"

# ---------- Driver ----------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lychee", required=True)
    ap.add_argument("--roots", nargs="+", default=["2-DOMAINS-LEVELS/**/TFA/**"])
    ap.add_argument("--cache", default=".qa_cache/quality.json")
    ap.add_argument("--out", default=".qa_cache/quality_report.json")
    args = ap.parse_args()

    roots = [Path(".")]
    try:
        ly = json.loads(Path(args.lychee).read_text(encoding="utf-8"))
    except Exception as e:
        print(f"Error reading Lychee file: {e}")
        return 1
        
    ok_links = [x["link"] for x in ly.get("ok",[]) if not x.get("error")]
    # Evaluate only repo-internal files
    internal = [Path(u) for u in ok_links if not re.match(r"^[a-z]+://", u)]
    # De-dup and filter existing files
    files = sorted({p.resolve() for p in internal if Path(p).exists() and p.is_file()})

    results = []
    for p in files:
        try:
            txt = read_file(p)
            label, conf, reasons = heuristics_classify(p, txt)
            # only refine ambiguous/template/placeholder with LLM
            if label in {"template-structured","placeholder"}:
                ll_label, ll_conf, ll_reason = llm_refine(label, p, txt)
                if ll_conf > conf: 
                    label, conf = ll_label, ll_conf
                    reasons.append(f"LLM: {ll_reason}")
            results.append({"path": p.as_posix(), "label": label, "confidence": conf, "reasons": reasons})
        except Exception as e:
            results.append({"path": p.as_posix(), "label": "error", "confidence": 0.0, "reasons": [str(e)]})

    counts = {k:0 for k in ["placeholder","template_structured","contentful_doc","contentful_code","error"]}
    for r in results:
        key = r["label"].replace("-","_")
        counts[key] = counts.get(key,0)+1

    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(json.dumps({"results":results,"counts":counts}, indent=2), encoding="utf-8")
    
    print(f"✅ Classified {len(results)} files: {counts}")
    return 0

if __name__ == "__main__":
    exit(main())