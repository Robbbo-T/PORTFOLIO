# Link Check System - Path Drift Prevention

This document describes the lightweight link check system designed to prevent path drift and catch merge artifacts automatically.

## Overview

The ASI-T repository now includes a fast, focused GitHub Action that runs on every push and pull request to detect:

- **Merge conflict markers** in markdown files  
- **Backup files** (*.backup, *.old, *.orig) that indicate merge issues
- **Critical repository structure** integrity
- **Broken symbolic links**

## Components

### GitHub Action: `.github/workflows/link-check.yml`

A lightweight workflow that:
- Runs in under 5 minutes
- Executes on push/PR to main, develop, and copilot branches
- Fails fast when path drift issues are detected
- Provides clear error messages for quick resolution

### Tool: `tools/path_drift_checker.py`

The core validation script that checks for:
```bash
python tools/path_drift_checker.py
```

**What it detects:**
- Merge conflict markers (`<<<<<<<`, `=======`, `>>>>>>>`)
- Backup files with common patterns
- Missing critical directories (tools, .github, portfolio)
- Broken symbolic links

### Tool: `tools/cleanup_backup_files.py`  

Utility for cleaning up detected issues:
```bash
python tools/cleanup_backup_files.py
```

**What it does:**
- Removes backup files (*.backup, *.old, *.orig, *~)
- Reports what was cleaned up
- Safe operation (skips .git directory)

## Usage Examples

### When the check fails

If you see a failed check in GitHub Actions:

1. **Check the error message** to see what was detected
2. **For merge artifacts:** Resolve merge conflicts properly
3. **For backup files:** Run the cleanup script:
   ```bash
   python tools/cleanup_backup_files.py
   git add -u
   git commit -m "cleanup: remove backup files"
   ```

### Manual validation

Test your changes locally before pushing:
```bash
python tools/path_drift_checker.py
```

## Integration with Existing Workflows

This system complements the existing comprehensive `link-and-quality.yml` workflow:

- **link-check.yml** - Fast path drift prevention (< 5 min)
- **link-and-quality.yml** - Comprehensive link + content analysis (longer)

Both workflows run automatically, providing layered validation.

## Common Issues and Solutions

| Issue | Cause | Solution |
|-------|-------|----------|
| Merge conflict markers detected | Incomplete merge resolution | Properly resolve conflicts in affected files |
| Backup files found | Editor/merge tool created backups | Run `cleanup_backup_files.py` |
| Critical structure missing | Repository corruption/incorrect checkout | Verify correct branch and complete checkout |
| Broken symbolic links | Links pointing to moved/deleted files | Update or remove broken links |

## Benefits

- **Fast feedback** on path structure issues
- **Prevents accumulation** of merge artifacts  
- **Maintains clean repository** state
- **Catches common mistakes** before they propagate
- **Minimal overhead** - runs quickly on every change

This system ensures the ASI-T repository maintains its rigorous structure standards while providing quick feedback to developers.