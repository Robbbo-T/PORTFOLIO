#!/usr/bin/env python3
"""
Summarize Lychee link check results and generate link status badge.
Reads Lychee JSON output and creates a badge + summary table.
"""
import json
import sys
from pathlib import Path

def create_badge(label, message, color):
    """Create SVG badge"""
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="180" height="20">
<mask id="a"><rect width="180" height="20" rx="3" fill="#fff"/></mask>
<g mask="url(#a)"><rect width="80" height="20" fill="#555"/>
<rect x="80" width="100" height="20" fill="{color}"/></g>
<g fill="#fff" text-anchor="middle" font-family="DejaVu Sans,Verdana" font-size="11">
<text x="40" y="14">{label}</text><text x="130" y="14">{message}</text></g></svg>'''

def main():
    if len(sys.argv) != 2:
        print("Usage: python links_summary.py <lychee_output.json>")
        sys.exit(1)
    
    lychee_file = Path(sys.argv[1])
    if not lychee_file.exists():
        print(f"Error: {lychee_file} not found")
        sys.exit(1)
    
    # Read Lychee JSON output
    try:
        data = json.loads(lychee_file.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"Error reading Lychee output: {e}")
        sys.exit(1)
    
    # Count results
    ok_count = len(data.get("ok", []))
    error_count = len(data.get("error", []))
    total_count = ok_count + error_count
    
    # Determine badge color and message
    if error_count == 0:
        color = "#4c1"  # Green
        message = f"{ok_count} links OK"
    else:
        color = "#df3e3e"  # Red
        message = f"{error_count} broken"
    
    # Create badge
    badge_dir = Path("docs/badges")
    badge_dir.mkdir(parents=True, exist_ok=True)
    badge_svg = create_badge("links", message, color)
    (badge_dir / "links.svg").write_text(badge_svg, encoding="utf-8")
    
    # Create summary table
    rows = [
        "# Links Status",
        "![links](docs/badges/links.svg)",
        "",
        f"**Total Links Checked**: {total_count}",
        f"**Working Links**: {ok_count}",
        f"**Broken Links**: {error_count}",
        ""
    ]
    
    if error_count > 0:
        rows.extend([
            "## Broken Links",
            "| Link | Source | Error |",
            "|------|--------|-------|"
        ])
        
        for error in data.get("error", []):
            link = error.get("link", "")
            source = error.get("source", "")
            err_msg = error.get("message", "Unknown error")
            rows.append(f"| {link} | {source} | {err_msg} |")
    
    if ok_count > 0:
        rows.extend([
            "",
            "## Working Links", 
            "| Link | Source |",
            "|------|--------|"
        ])
        
        for ok in data.get("ok", []):
            link = ok.get("link", "")
            source = ok.get("source", "")
            rows.append(f"| {link} | {source} |")
    
    # Write summary
    Path("LINKS_STATUS.md").write_text("\n".join(rows) + "\n", encoding="utf-8")
    print(f"✅ Links summary written: {ok_count} OK, {error_count} broken")

if __name__ == "__main__":
    main()