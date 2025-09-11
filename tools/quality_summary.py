#!/usr/bin/env python3
"""
Generate content quality badges and summary tables from quality report.
"""
import json
import sys
from pathlib import Path

def badge(label, message, color):
    """Create SVG badge"""
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="210" height="20">
<mask id="a"><rect width="210" height="20" rx="3" fill="#fff"/></mask>
<g mask="url(#a)"><rect width="120" height="20" fill="#555"/>
<rect x="120" width="90" height="20" fill="{color}"/></g>
<g fill="#fff" text-anchor="middle" font-family="DejaVu Sans,Verdana" font-size="11">
<text x="60" y="14">{label}</text><text x="165" y="14">{message}</text></g></svg>'''

def main():
    if len(sys.argv) != 2:
        print("Usage: python quality_summary.py <quality_report.json>")
        sys.exit(1)
        
    report_file = Path(sys.argv[1])
    if not report_file.exists():
        print(f"Error: {report_file} not found")
        sys.exit(1)
    
    try:
        data = json.loads(report_file.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"Error reading quality report: {e}")
        sys.exit(1)
    
    c = data["counts"]
    msg = f"doc:{c['contentful_doc']} code:{c['contentful_code']} tmpl:{c['template_structured']} ph:{c['placeholder']}"
    color = "#4c1" if c["placeholder"]==0 else "#df3e3e"
    
    # Create badge
    bd = Path("docs/badges")
    bd.mkdir(parents=True, exist_ok=True)
    (bd/"content.svg").write_text(badge("content", msg, color), encoding="utf-8")

    # Create summary table
    rows = [
        "# Content Quality",
        "![content](docs/badges/content.svg)",
        "",
        f"**Total Files Analyzed**: {sum(c.values())}",
        f"**Contentful Documentation**: {c['contentful_doc']}",
        f"**Contentful Code**: {c['contentful_code']}",
        f"**Template Structured**: {c['template_structured']}",
        f"**Placeholder**: {c['placeholder']}",
        "",
        "| Class | File | Confidence | Reasons |",
        "|-------|------|------------|---------|"
    ]
    
    # Sort results by class priority (worst first)
    order = ["error", "placeholder", "template_structured", "contentful_doc", "contentful_code"]
    
    for cls in order:
        cls_key = cls.replace("-", "_")
        for r in data["results"]:
            if r["label"].replace("-","_") == cls_key:
                confidence = f"{r['confidence']:.1f}" if r['confidence'] > 0 else "N/A"
                reasons = "; ".join(r['reasons'][:2])  # Limit length
                if len(reasons) > 50:
                    reasons = reasons[:47] + "..."
                rows.append(f"| `{cls}` | {r['path']} | {confidence} | {reasons} |")
    
    Path("CONTENT_QUALITY.md").write_text("\n".join(rows)+"\n", encoding="utf-8")
    
    print(f"✅ Content quality summary generated")
    print(f"   - Contentful docs: {c['contentful_doc']}")
    print(f"   - Contentful code: {c['contentful_code']}")
    print(f"   - Template structured: {c['template_structured']}")
    print(f"   - Placeholder: {c['placeholder']}")
    print(f"   - Errors: {c.get('error', 0)}")

if __name__ == "__main__":
    main()