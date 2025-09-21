# TFA Portfolio Tools

This directory contains tools for automated link checking and content quality assessment.

## Overview

The link and content quality system provides:
- **Link validation** using Lychee to check all markdown/html links
- **Content classification** into quality categories using heuristics + optional LLM
- **Badge generation** for visual status indication  
- **Automated reporting** via GitHub Actions
- **Path drift prevention** to catch merge artifacts automatically

## Tools

### `path_drift_checker.py`
Lightweight path drift detection focused on preventing merge artifacts and broken repository structure.

**Usage:**
```bash
python tools/path_drift_checker.py
```

**What it checks:**
- Merge conflict markers in markdown files
- Backup files (*.backup, *.old, *.orig) that indicate merge issues  
- Critical repository structure integrity
- Broken symbolic links

**Integration:**
Used by `.github/workflows/link-check.yml` for fast path drift prevention.

### `cleanup_backup_files.py`
Utility to clean up backup files and merge artifacts detected by the path drift checker.

**Usage:**
```bash
python tools/cleanup_backup_files.py
```

**What it does:**
- Removes backup files with common patterns (*.backup, *.old, *.orig, *~)
- Reports what was cleaned up
- Helps maintain clean repository state

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

## GitHub Workflows

### `.github/workflows/link-check.yml` (NEW)
Fast path drift prevention workflow that runs on every push/PR:
- Executes in under 5 minutes
- Detects merge artifacts and backup files
- Validates critical repository structure
- Fails fast on path drift issues

### `.github/workflows/link-and-quality.yml`
Comprehensive link and content quality assessment:
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