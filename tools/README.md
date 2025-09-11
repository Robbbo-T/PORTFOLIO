# TFA Portfolio Tools

This directory contains tools for automated link checking and content quality assessment.

## Overview

The link and content quality system provides:
- **Link validation** using Lychee to check all markdown/html links
- **Content classification** into quality categories using heuristics + optional LLM
- **Badge generation** for visual status indication  
- **Automated reporting** via GitHub Actions

## Tools

### `links_summary.py`
Processes Lychee JSON output to generate link status badges and summary tables.

**Usage:**
```bash
python tools/links_summary.py .lychee/out.json
```

**Outputs:**
- `docs/badges/links.svg` - Status badge (green if no broken links)
- `LINKS_STATUS.md` - Detailed link report

### `llm_link_quality.py` 
Classifies repository content into quality categories using heuristics and optional LLM refinement.

**Usage:**
```bash
python tools/llm_link_quality.py \
  --lychee .lychee/out.json \
  --roots "2-DOMAINS-LEVELS/**/TFA/**" \
  --out .qa_cache/quality_report.json
```

**Classification Categories:**
- `placeholder` - Boilerplate/TODO/tokenized stubs
- `template-structured` - Scaffolds with sections but no domain specifics
- `contentful-doc` - Substantive domain-specific documentation
- `contentful-code` - Substantive code/test artifacts

**LLM Configuration (optional):**
- Set `USE_LLM=true` to enable LLM refinement
- Set `LLM_PROVIDER=openai|azure|anthropic`
- Configure API keys via `OPENAI_API_KEY` etc.

### `quality_summary.py`
Generates content quality badges and summary tables.

**Usage:** 
```bash
python tools/quality_summary.py .qa_cache/quality_report.json
```

**Outputs:**
- `docs/badges/content.svg` - Content quality badge  
- `CONTENT_QUALITY.md` - Detailed content classification report

### `quality_rubric.yaml`
Domain-aware content classification rules for TFA layers (CB, QB, SE, SI, etc.).

## GitHub Workflow

The `.github/workflows/link-and-quality.yml` workflow runs automatically on:
- Push to main/develop/copilot branches
- Pull requests
- Daily schedule (3 AM UTC)
- Manual trigger

### Workflow Features:
- Link checking with Lychee
- Content quality assessment
- Badge generation
- Artifact uploads
- PR comments with summaries

### Required Secrets:
- `OPENAI_API_KEY` (or provider-specific) - Only if LLM refinement is enabled

## Integration with TFA Structure

The tools are designed to work with the TFA (Technical Functional Architecture) structure:
- Focuses on `2-DOMAINS-LEVELS/**/TFA/**` content
- Understands domain-specific quality requirements
- Provides aerospace-industry appropriate classifications

## Cost Control

- **Heuristics-first**: Fast, free classification for most content
- **LLM-optional**: Only refines borderline template/placeholder cases  
- **Provider flexibility**: Support for OpenAI, Azure, Anthropic
- **Easy disable**: Set `USE_LLM=false` to skip LLM entirely

## Output Files

Generated files are excluded from git via `.gitignore`:
- `.lychee/` - Link checking cache and results
- `.qa_cache/` - Content quality analysis cache and reports
- `LINKS_STATUS.md` - Link status report (generated for each run)
- `CONTENT_QUALITY.md` - Content quality report (generated for each run)
- `docs/badges/` - Status badges (committed to repo for display)