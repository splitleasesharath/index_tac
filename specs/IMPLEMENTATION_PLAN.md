# Index Lite Agentic Layer Integration - Implementation Plan

**Project**: Index Lite with Multi-Agent Task Orchestration
**Date**: October 18, 2025
**Version**: 1.0
**Status**: Ready for Implementation

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Current State Analysis](#current-state-analysis)
3. [Target Architecture](#target-architecture)
4. [Prerequisites](#prerequisites)
5. [Phase 1: Repository Setup](#phase-1-repository-setup)
6. [Phase 2: Trigger System Modernization](#phase-2-trigger-system-modernization)
7. [Phase 3: Environment Configuration](#phase-3-environment-configuration)
8. [Phase 4: Development Scripts](#phase-4-development-scripts)
9. [Phase 5: Testing & Validation](#phase-5-testing--validation)
10. [Phase 6: Deployment Automation](#phase-6-deployment-automation)
11. [Usage Guide](#usage-guide)
12. [Troubleshooting](#troubleshooting)
13. [Future Enhancements](#future-enhancements)

---

## Executive Summary

### Objective

Deeply integrate the **Index Lite** static website (Split Lease clone) into the **Multi-Agent Task Orchestration** (Todone) agentic layer, creating a production-ready development environment where AI agents can autonomously work on Index Lite features via:

- Webhook-triggered GitHub issue workflows
- Automated task distribution from tasks.md
- Parallel development in git worktrees
- Automated building, testing, and deployment to Cloudflare Pages

### What's Being Built

A sophisticated agentic development system that wraps around the Index Lite static website, enabling:

1. **AI-Driven Development**: Agents process tasks from tasks.md or GitHub issues
2. **Parallel Experimentation**: Multiple agents work simultaneously in isolated git worktrees
3. **Automated Deployment**: Changes automatically tested and deployed to Cloudflare Pages
4. **GitHub Integration**: Full PR creation, commenting, and status updates

### Key Decisions

| Decision Point | Choice | Rationale |
|----------------|--------|-----------|
| Git Strategy | Fresh repo with new remote | Clean slate, avoid history conflicts |
| Trigger System | Webhook + Cron hybrid | GitHub issues + local task.md support |
| App Structure | Keep apps/ folder | Allows future app additions |
| Deployment | Cloudflare Pages | User's existing infrastructure |
| Agentic Scope | Full capabilities | Preserve all TAC-7 features, adapt for static site |

---

## Current State Analysis

### What We Have Now

#### 1. **Agentic Layer** (`C:\Users\igor\My Drive (splitleaseteam@gmail.com)\!Agent Context and Tools\SL1\index_lite`)

```
index_lite/
├── .claude/                     # Slash commands for Claude Code
│   └── commands/
│       ├── build.md
│       ├── implement.md
│       ├── plan.md
│       ├── process_tasks.md
│       ├── mark_in_progress.md
│       ├── update_task.md
│       └── init_worktree.md
├── adws/                        # AI Developer Workflows
│   ├── adw_build_update_task.py
│   ├── adw_plan_implement_update_task.py
│   ├── adw_chore_implement.py
│   ├── adw_prompt.py
│   ├── adw_slash_command.py
│   ├── adw_modules/
│   │   ├── agent.py
│   │   ├── data_models.py
│   │   └── utils.py
│   └── adw_triggers/
│       └── adw_trigger_cron_todone.py    # OLD: Cron-based trigger
├── specs/
│   └── plan-adw01-multi-agent-task-list.md
├── tasks.md                     # Task tracking file
├── .env.sample                  # Minimal env vars
├── .gitignore
└── README.md
```

**Current Trigger**: Cron-based polling of tasks.md using `schedule` library

#### 2. **Index Lite Page** (`apps/index_lite/` - newly moved)

```
apps/index_lite/
├── .git/                        # Existing git repo
├── assets/images/
│   ├── logo.png
│   ├── hero-left.png
│   └── hero-right.png
├── index.html                   # 28KB main page
├── styles.css                   # 79KB styling
├── script.js                    # 79KB functionality
├── worker.js                    # Service worker
├── all_split_lease_links.json
├── footer_links.json
├── package.json                 # Build scripts
├── README.md                    # Index lite docs
├── CLAUDE.md                    # AI guidance for index lite
└── [9+ other .md docs]
```

**Current State**: Fully functional static site, previously deployed to GitHub Pages

---

## Target Architecture

### Final Directory Structure

```
index_lite/                                      # Root: Agentic layer repository
├── .env                                         # Environment variables (gitignored)
├── .env.sample                                  # Template with all required vars
├── .gitignore                                   # Comprehensive ignores
├── README.md                                    # Updated for Index Lite
├── tasks.md                                     # Multi-agent task tracking
│
├── .claude/                                     # Claude Code slash commands
│   └── commands/                                # Preserved from agentic layer
│
├── adws/                                        # AI Developer Workflows
│   ├── adw_build_update_task.py
│   ├── adw_plan_implement_update_task.py
│   ├── adw_modules/
│   │   ├── agent.py
│   │   ├── data_models.py
│   │   ├── utils.py
│   │   └── github.py                            # NEW: GitHub API helpers
│   ├── adw_triggers/
│   │   ├── trigger_webhook.py                   # NEW: GitHub webhook endpoint
│   │   └── trigger_cron.py                      # RENAMED: Cron trigger (optional)
│   └── adw_tests/
│       └── health_check.py                      # NEW: System health validation
│
├── specs/                                       # Feature specifications
│   ├── IMPLEMENTATION_PLAN.md                   # This document
│   └── plan-adw01-multi-agent-task-list.md
│
├── scripts/                                     # NEW: Development & deployment scripts
│   ├── start_dev.sh                             # Launch local dev server
│   ├── build.sh                                 # Build for production
│   ├── deploy.sh                                # Deploy to Cloudflare Pages
│   └── start_webhook.sh                         # Launch webhook listener
│
└── apps/                                        # Application layer
    └── index_lite/                              # Index Lite static website
        ├── .git/                                # Submodule or merged history
        ├── assets/
        ├── index.html
        ├── styles.css
        ├── script.js
        ├── package.json
        └── [all other index_lite files]
```

### System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                      GitHub Repository                          │
│              (New repo to be created by user)                   │
└────────────┬─────────────────────────────────────┬──────────────┘
             │                                     │
             │ Webhook Events                      │ git push
             │ (issues, comments)                  │
             ▼                                     ▼
┌────────────────────────┐              ┌─────────────────────┐
│   trigger_webhook.py    │              │  Cloudflare Pages   │
│   (FastAPI on :8001)    │              │  (Static Deploy)    │
└────────┬───────────────┘              └─────────────────────┘
         │
         │ Spawns workflows
         ▼
┌────────────────────────────────────────────────────────────────┐
│              ADW Workflows (Background Processes)               │
│  ┌──────────────────┐  ┌──────────────────┐                    │
│  │ adw_build_update │  │ adw_plan_impl    │  ...               │
│  └────────┬─────────┘  └────────┬─────────┘                    │
│           │                     │                               │
│           └─────────┬───────────┘                               │
└─────────────────────┼─────────────────────────────────────────┘
                      │
                      │ Executes slash commands
                      ▼
         ┌────────────────────────────┐
         │   Claude Code CLI          │
         │   (Anthropic API)          │
         └────────────────────────────┘
                      │
                      │ Modifies files in
                      ▼
         ┌────────────────────────────┐
         │  Git Worktree              │
         │  (apps/index_lite/...)     │
         └────────────────────────────┘
                      │
                      │ git commit, push, PR
                      ▼
         ┌────────────────────────────┐
         │  GitHub PR Created         │
         │  (Auto-comments status)    │
         └────────────────────────────┘
```

### Parallel Trigger Systems

The system supports **two concurrent triggering mechanisms**:

1. **GitHub Webhook Trigger** (`trigger_webhook.py`)
   - Listens for GitHub issue opened/commented events
   - Extracts ADW workflow commands from issue body/comments
   - Spawns workflows in background via subprocess
   - Posts status updates back to GitHub issues

2. **Cron-based Task Trigger** (`trigger_cron.py`)
   - Polls tasks.md every N seconds
   - Processes pending tasks `[]` or scheduled tasks `[⏰]`
   - Creates worktrees if needed
   - Updates task status to `[🟡, adw-id]` when started

**Both can run simultaneously** without conflict.

---

## Prerequisites

### Required Software

| Tool | Version | Purpose | Installation Check |
|------|---------|---------|-------------------|
| **Python** | 3.10+ | Run ADW scripts | `python --version` |
| **uv** | Latest | Python package runner | `uv --version` |
| **Claude Code CLI** | Latest | AI agent execution | `claude --version` |
| **Git** | 2.30+ | Version control, worktrees | `git --version` |
| **GitHub CLI** | 2.0+ | PR creation, issue management | `gh --version` |
| **Node.js** | 18+ | Optional: Local dev server | `node --version` |
| **Python http.server** | Built-in | Alternative dev server | `python -m http.server --help` |

### Required Accounts & Keys

1. **Anthropic API Key**
   - Get from: https://console.anthropic.com/
   - Required for Claude Code execution

2. **GitHub Personal Access Token (PAT)**
   - Scopes needed: `repo`, `workflow`, `write:packages`, `read:org`
   - Generate at: GitHub Settings → Developer settings → Personal access tokens

3. **GitHub Repository** (to be created)
   - User will create this and provide the URL
   - Will become the `GITHUB_REPO_URL` in .env

4. **Cloudflare Account** (optional for tunnel)
   - For exposing webhook endpoint publicly
   - Get tunnel token from Cloudflare Zero Trust

### Local Environment Setup

```bash
# 1. Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 2. Authenticate GitHub CLI
gh auth login

# 3. Verify Claude Code CLI
claude --version
# If not found, install from: https://claude.com/claude-code
```

---

## Phase 1: Repository Setup

### Step 1.1: Initialize Git Repository

**Objective**: Set up fresh git repository for the integrated project

**Actions**:

```bash
# Navigate to project root
cd "C:\Users\igor\My Drive (splitleaseteam@gmail.com)\!Agent Context and Tools\SL1\index_lite"

# Initialize git if not already done
git init

# Create .gitignore
cat > .gitignore << 'EOF'
# Environment
.env
*.env.local

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/
.venv

# Agent outputs
agents/
*.log
*.jsonl

# OS
.DS_Store
Thumbs.db
desktop.ini

# IDE
.vscode/
.idea/
*.swp
*.swo

# Build outputs
dist/
build/
*.egg-info/

# Node (from index_lite)
node_modules/
package-lock.json
EOF

# Initial commit
git add .
git commit -m "Initial commit: Agentic layer with Index Lite integration"
```

### Step 1.2: Create GitHub Repository

**Manual Action Required**: User creates the GitHub repository

1. Go to GitHub: https://github.com/new
2. Repository name: `index-lite-agentic` (or user's choice)
3. Description: "Index Lite with Multi-Agent Task Orchestration"
4. Visibility: Private or Public (user's choice)
5. DO NOT initialize with README, .gitignore, or license
6. Click "Create repository"

**Output**: Note the repository URL (e.g., `https://github.com/USERNAME/index-lite-agentic.git`)

### Step 1.3: Connect Local to Remote

```bash
# Add remote (replace with actual URL from Step 1.2)
git remote add origin https://github.com/USERNAME/index-lite-agentic.git

# Push initial commit
git branch -M main
git push -u origin main
```

### Step 1.4: Handle Index Lite Git History

**Decision**: The index_lite app has its own .git directory. Two options:

**Option A: Keep as Git Submodule** (Recommended if index_lite updates independently)

```bash
cd apps/index_lite
# Remove the copied .git directory
rm -rf .git

# Add as submodule from original repo
cd ../..
git submodule add https://github.com/splitleasesharath/index_lite.git apps/index_lite
git commit -m "Add index_lite as submodule"
```

**Option B: Merge Git History** (Simpler, recommended for this use case)

```bash
cd apps/index_lite
# The .git directory is already there from our copy
# Just commit it as part of the monorepo
cd ../..
git add apps/index_lite
git commit -m "Integrate index_lite static website into apps directory"
git push
```

**Recommendation**: Use **Option B** for simplicity, since we're wrapping index_lite with the agentic layer.

---

## Phase 2: Trigger System Modernization

### Step 2.1: Add TAC-7 Modules to index_lite

**Objective**: Bring in GitHub integration and state management from TAC-7

**Actions**:

1. **Create adw_modules/github.py**

```bash
# Navigate to adw_modules
cd adws/adw_modules
```

Create the file `github.py` by copying from TAC-7:

```python
# Source: C:\Users\igor\My Drive (splitleaseteam@gmail.com)\!Agent Context and Tools\SL18\TAC\tac-7\adws\adw_modules\github.py
# Copy the entire github.py module which includes:
# - make_issue_comment()
# - get_issue_comments()
# - ADW_BOT_IDENTIFIER constant
# - GitHub CLI wrapper functions
```

**File Location**: `adws/adw_modules/github.py`

2. **Create adw_modules/state.py**

```python
# Source: C:\Users\igor\My Drive (splitleaseteam@gmail.com)\!Agent Context and Tools\SL18\TAC\tac-7\adws\adw_modules\state.py
# Copy the ADWState class for managing workflow state
```

**File Location**: `adws/adw_modules/state.py`

3. **Create adw_modules/workflow_ops.py**

```python
# Source: C:\Users\igor\My Drive (splitleaseteam@gmail.com)\!Agent Context and Tools\SL18\TAC\tac-7\adws\adw_modules\workflow_ops.py
# Copy workflow extraction and validation logic
```

**File Location**: `adws/adw_modules/workflow_ops.py`

### Step 2.2: Add Webhook Trigger

**Objective**: Replace cron trigger with webhook-based GitHub issue processing

**Actions**:

1. **Copy trigger_webhook.py**

```bash
cd adws/adw_triggers
```

Copy the file from TAC-7:

**Source**: `C:\Users\igor\My Drive (splitleaseteam@gmail.com)\!Agent Context and Tools\SL18\TAC\tac-7\adws\adw_triggers\trigger_webhook.py`

**Destination**: `adws/adw_triggers/trigger_webhook.py`

2. **Adapt trigger_webhook.py for Index Lite**

Make these modifications to trigger_webhook.py:

```python
# At line 201-202, update the repository root path calculation
# CURRENT:
repo_root = os.path.dirname(adws_dir)  # Go up to repository root

# CHANGE TO:
# For index_lite, repo_root is already at the right level
repo_root = os.path.dirname(adws_dir)  # This stays the same

# Verify that .claude/commands/ exists at repo_root
if not os.path.exists(os.path.join(repo_root, ".claude", "commands")):
    logger.error(f"Cannot find .claude/commands/ at {repo_root}")
    logger.error("Make sure trigger_webhook.py is running from the correct directory")
```

**No other changes needed** - the trigger is already generic enough to work with any app structure.

3. **Rename old cron trigger (optional)**

```bash
# Optional: Keep the cron trigger for tasks.md processing
mv adw_trigger_cron_todone.py trigger_cron.py
```

### Step 2.3: Add Health Check System

**Objective**: Validate system health via /health endpoint

**Actions**:

```bash
# Create test directory
mkdir -p adws/adw_tests
cd adws/adw_tests
```

Copy from TAC-7:

**Source**: `C:\Users\igor\My Drive (splitleaseteam@gmail.com)\!Agent Context and Tools\SL18\TAC\tac-7\adws\adw_tests\health_check.py`

**Destination**: `adws/adw_tests/health_check.py`

**Adaptations Needed**:

Update health_check.py to validate Index Lite structure:

```python
# Modify the directory checks around line 50-100

def check_directory_structure():
    """Verify required directories exist."""
    required_dirs = [
        ".claude/commands",
        "adws/adw_modules",
        "adws/adw_triggers",
        "apps/index_lite",  # NEW: Check for index_lite
        "specs",
    ]

    # Add index_lite specific checks
    index_lite_files = [
        "apps/index_lite/index.html",
        "apps/index_lite/styles.css",
        "apps/index_lite/script.js",
    ]

    for file_path in index_lite_files:
        if not os.path.exists(file_path):
            print(f"  ❌ Missing index_lite file: {file_path}")
            return False

    return True
```

---

## Phase 3: Environment Configuration

### Step 3.1: Update .env.sample

**Objective**: Create comprehensive environment variable template

**Actions**:

Replace the existing `.env.sample` with:

```bash
# ============================================================================
# INDEX LITE AGENTIC LAYER - ENVIRONMENT CONFIGURATION
# ============================================================================
# Copy this file to .env and fill in your actual values
# NEVER commit .env to version control (it's in .gitignore)

# ----------------------------------------------------------------------------
# REQUIRED: Anthropic API Configuration
# ----------------------------------------------------------------------------
# Get your API key from: https://console.anthropic.com/
# This is required for Claude Code to run agents programmatically
ANTHROPIC_API_KEY=

# ----------------------------------------------------------------------------
# REQUIRED: GitHub Configuration
# ----------------------------------------------------------------------------
# The GitHub repository URL for this project
# Format: https://github.com/USERNAME/REPO_NAME
# Example: https://github.com/splitleasesharath/index-lite-agentic
GITHUB_REPO_URL=

# GitHub Personal Access Token (PAT)
# Required scopes: repo, workflow, write:packages
# Generate at: https://github.com/settings/tokens
# If not set, ADW will use the default 'gh auth' login
GITHUB_PAT=

# ----------------------------------------------------------------------------
# Claude Code CLI Configuration
# ----------------------------------------------------------------------------
# Path to Claude Code executable
# Run 'which claude' (Mac/Linux) or 'where claude' (Windows) to find it
# Default: claude (assumes it's in PATH)
CLAUDE_CODE_PATH=claude

# Maintain project working directory after each command
# Recommended: true (prevents directory drift during agent execution)
CLAUDE_BASH_MAINTAIN_PROJECT_WORKING_DIR=true

# ----------------------------------------------------------------------------
# ADW Webhook Configuration
# ----------------------------------------------------------------------------
# Port for the webhook server (trigger_webhook.py)
# Default: 8001
PORT=8001

# Cloudflare Tunnel Token (OPTIONAL)
# If you want to expose the webhook endpoint to GitHub (public internet)
# without port forwarding, use Cloudflare Tunnel
# Get from: https://one.dash.cloudflare.com/ → Access → Tunnels
CLOUDFLARED_TUNNEL_TOKEN=

# ----------------------------------------------------------------------------
# Deployment Configuration
# ----------------------------------------------------------------------------
# Cloudflare Pages Project Name
# This is the project name you'll use for 'wrangler pages deploy'
CLOUDFLARE_PAGES_PROJECT_NAME=index-lite

# Cloudflare Account ID (for Pages deployment)
CLOUDFLARE_ACCOUNT_ID=

# ----------------------------------------------------------------------------
# OPTIONAL: Image Upload Configuration
# ----------------------------------------------------------------------------
# Cloudflare R2 Configuration (for uploading review screenshots)
# If configured, review screenshots will be uploaded to R2 and displayed as images
# If not configured, local file paths will be shown instead
CLOUDFLARE_R2_ACCESS_KEY_ID=
CLOUDFLARE_R2_SECRET_ACCESS_KEY=
CLOUDFLARE_R2_BUCKET_NAME=
CLOUDFLARE_R2_PUBLIC_DOMAIN=

# ----------------------------------------------------------------------------
# OPTIONAL: Advanced Agent Configuration
# ----------------------------------------------------------------------------
# E2B API Key (for cloud sandbox environment)
# Get from: https://e2b.dev/
# Only needed if you want agents to run in isolated sandboxes
E2B_API_KEY=

# Default model for agent execution
# Options: sonnet (fast, cheaper) | opus (advanced reasoning, expensive)
# Default: sonnet
DEFAULT_AGENT_MODEL=sonnet

# Maximum concurrent agents from cron trigger
# Default: 5
MAX_CONCURRENT_AGENTS=5

# Cron polling interval (seconds)
# How often to check tasks.md for new tasks
# Default: 5
CRON_POLLING_INTERVAL=5
```

### Step 3.2: Create .env File

**Manual Action Required**: User creates `.env` file

```bash
# Copy the template
cp .env.sample .env

# Open in editor and fill in values
# Windows:
notepad .env

# Mac/Linux:
nano .env
# or
code .env
```

**Required Values**:

1. `ANTHROPIC_API_KEY`: Get from https://console.anthropic.com/
2. `GITHUB_REPO_URL`: The repository URL from Phase 1, Step 1.2
3. `GITHUB_PAT`: Generate from https://github.com/settings/tokens
4. `CLAUDE_CODE_PATH`: Run `where claude` on Windows or `which claude` on Mac/Linux

**Optional Values**:

- `CLOUDFLARED_TUNNEL_TOKEN`: Only if exposing webhook publicly
- `CLOUDFLARE_PAGES_PROJECT_NAME`: For deployment (default: index-lite)
- `CLOUDFLARE_ACCOUNT_ID`: For Cloudflare Pages deployment

### Step 3.3: Update adw_modules/agent.py

**Objective**: Ensure agent.py reads from .env correctly

**Actions**:

Verify that `adws/adw_modules/agent.py` includes proper environment variable loading:

```python
# At the top of agent.py, ensure this exists:
from dotenv import load_dotenv

# Load .env from project root
load_dotenv()

# In get_safe_subprocess_env() function, add GitHub vars:
def get_safe_subprocess_env() -> Dict[str, str]:
    """Get filtered environment variables safe for subprocess execution."""
    safe_env_vars = {
        # Anthropic Configuration (required)
        "ANTHROPIC_API_KEY": os.getenv("ANTHROPIC_API_KEY"),

        # GitHub Configuration (required for ADW)
        "GITHUB_REPO_URL": os.getenv("GITHUB_REPO_URL"),
        "GITHUB_PAT": os.getenv("GITHUB_PAT"),

        # Claude Code Configuration
        "CLAUDE_CODE_PATH": os.getenv("CLAUDE_CODE_PATH", "claude"),
        "CLAUDE_BASH_MAINTAIN_PROJECT_WORKING_DIR": os.getenv(
            "CLAUDE_BASH_MAINTAIN_PROJECT_WORKING_DIR", "true"
        ),

        # Essential system environment variables
        "HOME": os.getenv("HOME"),
        "USER": os.getenv("USER"),
        "PATH": os.getenv("PATH"),
        "SHELL": os.getenv("SHELL"),
        "TERM": os.getenv("TERM"),
        "LANG": os.getenv("LANG"),
        "LC_ALL": os.getenv("LC_ALL"),

        # Python-specific variables
        "PYTHONPATH": os.getenv("PYTHONPATH"),
        "PYTHONUNBUFFERED": "1",
    }

    # Filter out None values
    return {k: v for k, v in safe_env_vars.items() if v is not None}
```

---

## Phase 4: Development Scripts

### Step 4.1: Create scripts/ Directory

```bash
mkdir -p scripts
cd scripts
```

### Step 4.2: Local Development Server Script

**File**: `scripts/start_dev.sh`

```bash
#!/bin/bash
# Start local development server for Index Lite

set -e

echo "🚀 Starting Index Lite Development Server..."

# Navigate to the index_lite app directory
cd "$(dirname "$0")/../apps/index_lite"

# Check if Python is available
if command -v python3 &> /dev/null; then
    echo "📡 Server starting at http://localhost:8000"
    echo "📂 Serving: $(pwd)"
    echo "🛑 Press Ctrl+C to stop"
    echo ""
    python3 -m http.server 8000
elif command -v python &> /dev/null; then
    echo "📡 Server starting at http://localhost:8000"
    echo "📂 Serving: $(pwd)"
    echo "🛑 Press Ctrl+C to stop"
    echo ""
    python -m http.server 8000
else
    echo "❌ Python not found. Please install Python 3 to run the dev server."
    exit 1
fi
```

**Make executable**:

```bash
chmod +x scripts/start_dev.sh
```

**Usage**:

```bash
./scripts/start_dev.sh
```

### Step 4.3: Build Script

**File**: `scripts/build.sh`

```bash
#!/bin/bash
# Build Index Lite for production deployment

set -e

echo "🏗️  Building Index Lite for production..."

# Navigate to the index_lite app directory
cd "$(dirname "$0")/../apps/index_lite"

# Check if package.json exists and has build script
if [ -f "package.json" ]; then
    # Use the build script from package.json
    if command -v npm &> /dev/null; then
        echo "📦 Running npm build..."
        npm run build 2>/dev/null || npm run build-windows 2>/dev/null || {
            echo "⚠️  No build script found, copying files manually..."
            mkdir -p dist
            cp index.html styles.css script.js dist/
        }
    else
        echo "⚠️  npm not found, copying files manually..."
        mkdir -p dist
        cp index.html styles.css script.js dist/
    fi
else
    echo "⚠️  No package.json found, copying files manually..."
    mkdir -p dist
    cp index.html styles.css script.js dist/
fi

echo "✅ Build complete! Output in apps/index_lite/dist/"
ls -lh dist/
```

**Make executable**:

```bash
chmod +x scripts/build.sh
```

### Step 4.4: Deployment Script

**File**: `scripts/deploy.sh`

```bash
#!/bin/bash
# Deploy Index Lite to Cloudflare Pages

set -e

echo "🚀 Deploying Index Lite to Cloudflare Pages..."

# Load environment variables
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

# Check for required environment variables
if [ -z "$CLOUDFLARE_PAGES_PROJECT_NAME" ]; then
    echo "❌ Error: CLOUDFLARE_PAGES_PROJECT_NAME not set in .env"
    exit 1
fi

# Build first
echo "📦 Building Index Lite..."
./scripts/build.sh

# Navigate to the index_lite app directory
cd "$(dirname "$0")/../apps/index_lite"

# Deploy using wrangler
if command -v wrangler &> /dev/null; then
    echo "🌍 Deploying to Cloudflare Pages..."
    wrangler pages deploy dist --project-name="$CLOUDFLARE_PAGES_PROJECT_NAME"
    echo "✅ Deployment complete!"
else
    echo "❌ Error: wrangler CLI not found"
    echo "Install with: npm install -g wrangler"
    exit 1
fi
```

**Make executable**:

```bash
chmod +x scripts/deploy.sh
```

### Step 4.5: Webhook Server Script

**File**: `scripts/start_webhook.sh`

```bash
#!/bin/bash
# Start the GitHub webhook listener

set -e

echo "🎣 Starting GitHub Webhook Listener..."

# Load environment variables
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
else
    echo "⚠️  Warning: .env file not found, using defaults"
fi

# Check for required environment variable
if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo "❌ Error: ANTHROPIC_API_KEY not set in .env"
    exit 1
fi

# Navigate to project root
cd "$(dirname "$0")/.."

# Start the webhook server
echo "📡 Webhook server starting on port ${PORT:-8001}..."
echo "🔗 Endpoint: http://localhost:${PORT:-8001}/gh-webhook"
echo "❤️  Health check: http://localhost:${PORT:-8001}/health"
echo "🛑 Press Ctrl+C to stop"
echo ""

uv run adws/adw_triggers/trigger_webhook.py
```

**Make executable**:

```bash
chmod +x scripts/start_webhook.sh
```

### Step 4.6: Cron Trigger Script (Optional)

**File**: `scripts/start_cron.sh`

```bash
#!/bin/bash
# Start the cron-based task monitor

set -e

echo "⏰ Starting Cron Task Monitor..."

# Load environment variables
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

# Navigate to project root
cd "$(dirname "$0")/.."

# Start the cron trigger
echo "👀 Monitoring tasks.md every ${CRON_POLLING_INTERVAL:-5} seconds..."
echo "🛑 Press Ctrl+C to stop"
echo ""

uv run adws/adw_triggers/trigger_cron.py --interval ${CRON_POLLING_INTERVAL:-5}
```

**Make executable**:

```bash
chmod +x scripts/start_cron.sh
```

---

## Phase 5: Testing & Validation

### Step 5.1: Test Local Development Server

**Objective**: Verify Index Lite serves correctly

**Actions**:

```bash
# Start the dev server
./scripts/start_dev.sh

# In a browser, navigate to:
# http://localhost:8000

# Expected: Index Lite page loads with all styles and scripts
```

**Validation Checklist**:

- [ ] Page loads without errors
- [ ] Styles render correctly (no broken CSS)
- [ ] Hero images appear
- [ ] Navigation works
- [ ] Schedule selector is interactive
- [ ] Console shows no JavaScript errors

### Step 5.2: Test Build Process

**Objective**: Verify production build works

**Actions**:

```bash
# Run the build script
./scripts/build.sh

# Check output
ls -la apps/index_lite/dist/

# Expected files:
# - index.html
# - styles.css
# - script.js
# - (any other files copied by package.json build script)
```

### Step 5.3: Test Health Check

**Objective**: Validate system prerequisites

**Actions**:

```bash
# Run the health check
uv run adws/adw_tests/health_check.py

# Expected output: ✅ All checks pass
```

**If Errors Occur**:

Fix any missing dependencies or configuration issues identified by the health check.

### Step 5.4: Test Webhook Server (Without GitHub)

**Objective**: Verify webhook server starts correctly

**Actions**:

```bash
# Start the webhook server
./scripts/start_webhook.sh

# Expected output:
# 📡 Webhook server starting on port 8001...
# 🔗 Endpoint: http://localhost:8001/gh-webhook
# ❤️  Health check: http://localhost:8001/health
```

**Test Health Endpoint**:

In another terminal:

```bash
curl http://localhost:8001/health
```

**Expected Response**:

```json
{
  "status": "healthy",
  "service": "adw-webhook-trigger",
  "health_check": {
    "success": true,
    "warnings": [],
    "errors": [],
    "details": "Run health_check.py directly for full report"
  }
}
```

### Step 5.5: Test Agent Execution Manually

**Objective**: Verify Claude Code agents can execute

**Actions**:

```bash
# Test a simple prompt execution
uv run adws/adw_prompt.py "List the files in apps/index_lite directory"

# Expected: Agent executes, outputs file listing
```

**Test a slash command**:

```bash
# Create a test task in tasks.md
echo "## Git Worktree test-worktree" >> tasks.md
echo "[] Test task: Add a comment to index.html" >> tasks.md

# Process tasks (dry run)
uv run adws/adw_triggers/trigger_cron.py --once --dry-run

# Expected: Shows the task would be picked up
```

### Step 5.6: Test Full Workflow (End-to-End)

**Objective**: Execute a complete task workflow

**Actions**:

```bash
# 1. Create a real test task
cat >> tasks.md << 'EOF'

## Git Worktree test-feature
[] Add a copyright year comment to index.html header
EOF

# 2. Run the cron trigger once
uv run adws/adw_triggers/trigger_cron.py --once

# Expected behavior:
# - Creates worktree at ../test-feature/
# - Marks task as [🟡, adw-xxxxxx]
# - Spawns adw_build_update_task.py
# - Agent modifies index.html
# - Task updated to [✅, adw-xxxxxx, commit-hash]
```

**Validation**:

- [ ] Worktree created
- [ ] Task status updated in tasks.md
- [ ] Agent output in agents/adw-xxxxxx/
- [ ] Commit made in worktree
- [ ] PR created (if configured)

---

## Phase 6: Deployment Automation

### Step 6.1: Configure Cloudflare Pages

**Manual Actions Required**:

1. **Install Wrangler CLI**:

```bash
npm install -g wrangler
```

2. **Authenticate with Cloudflare**:

```bash
wrangler login
```

3. **Create Cloudflare Pages Project**:

Go to Cloudflare Dashboard → Pages → Create a project

- Project name: `index-lite` (or value from .env)
- Production branch: `main`
- Build command: (leave empty, we build locally)
- Build output directory: `apps/index_lite/dist`

4. **Get Account ID**:

```bash
wrangler whoami
```

Copy the Account ID and add to .env:

```bash
CLOUDFLARE_ACCOUNT_ID=your_account_id_here
```

### Step 6.2: Test Manual Deployment

**Objective**: Verify deployment works

**Actions**:

```bash
# Deploy to Cloudflare Pages
./scripts/deploy.sh

# Expected output:
# ✅ Deployment complete!
# URL: https://index-lite.pages.dev
```

**Validation**:

- [ ] Deployment succeeds
- [ ] URL is accessible
- [ ] Page renders correctly on Cloudflare Pages

### Step 6.3: Configure GitHub Webhook

**Objective**: Connect GitHub issues to trigger_webhook.py

**Prerequisites**:

- Webhook endpoint must be publicly accessible
- Options:
  1. Use Cloudflare Tunnel (recommended)
  2. Use ngrok
  3. Use port forwarding

**Option 1: Cloudflare Tunnel (Recommended)**

```bash
# Install cloudflared
# Download from: https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/install-and-setup/installation/

# Start tunnel
cloudflared tunnel --url http://localhost:8001

# Copy the public URL (e.g., https://abc-def.trycloudflare.com)
```

**Option 2: Using Cloudflare Tunnel Token**

If you have a permanent tunnel token in .env:

```bash
# Start webhook with tunnel
cloudflared tunnel --url http://localhost:8001 --token $CLOUDFLARED_TUNNEL_TOKEN &
./scripts/start_webhook.sh
```

**Configure GitHub Webhook**:

1. Go to GitHub repo → Settings → Webhooks → Add webhook
2. Payload URL: `https://your-tunnel-url.trycloudflare.com/gh-webhook`
3. Content type: `application/json`
4. Events: Choose individual events
   - ✅ Issues
   - ✅ Issue comments
5. Active: ✅
6. Click "Add webhook"

### Step 6.4: Test GitHub Webhook Integration

**Objective**: Verify end-to-end GitHub → Webhook → Agent flow

**Actions**:

1. **Ensure webhook server is running**:

```bash
./scripts/start_webhook.sh
```

2. **Create a test GitHub issue**:

Go to GitHub repo → Issues → New issue

```
Title: Test ADW Workflow
Body:
Testing the webhook integration.

adw_build_update_task

Please add a comment to the top of index.html with today's date.
```

3. **Expected Behavior**:

- Webhook receives the event
- Console shows: `Detected workflow: adw_build_update_task`
- Agent spawned in background
- GitHub issue receives a comment from ADW bot with ADW ID
- Agent modifies index.html
- Commits are made
- Task status reported back to issue

**Validation**:

- [ ] Webhook receives issue event
- [ ] ADW workflow spawned
- [ ] Bot comment posted to issue
- [ ] Agent executes successfully
- [ ] Files modified
- [ ] Final status reported to issue

---

## Usage Guide

### For Local Development

#### Starting Everything

```bash
# Terminal 1: Start webhook listener (for GitHub issues)
./scripts/start_webhook.sh

# Terminal 2: Start cron trigger (for tasks.md)
./scripts/start_cron.sh

# Terminal 3: Start local dev server (to preview Index Lite)
./scripts/start_dev.sh
```

#### Working with tasks.md

**Task Format**:

```markdown
## Git Worktree feature-name

[] Pending task description
[⏰] Blocked task (won't run until ready)
[🟡, adw-abc123] In progress task
[✅, adw-abc123, a1b2c3d] Completed task
[❌, adw-abc123] Failed task
```

**Tags**:

- `{opus}` - Use Opus model (advanced reasoning)
- `{sonnet}` - Use Sonnet model (default)
- `{adw_plan_implement_update_task}` - Use full plan-implement-update workflow

**Example tasks.md**:

```markdown
# Multi-Agent Task List for Index Lite

## Git Worktree feature-dark-mode
[] Implement dark mode toggle in header {opus}
[] Add CSS variables for dark theme colors
[] Update localStorage to persist theme preference

## Git Worktree fix-mobile-nav
[] Fix hamburger menu not closing on mobile {sonnet}

## Git Worktree perf-lazy-load
[] Implement lazy loading for property images {adw_plan_implement_update_task, opus}
[⏰] Test lazy loading performance on mobile
```

#### Working with GitHub Issues

**To trigger a workflow via GitHub issue**:

1. Create a new issue
2. In the issue body, include:
   - Workflow command: `adw_build_update_task` or `adw_plan_implement_update_task`
   - Task description
   - Optional: ADW ID (for dependent workflows)
   - Optional: Model preference `{opus}` or `{sonnet}`

**Example Issue**:

```
Title: Add lazy loading to images

Body:
adw_plan_implement_update_task {opus}

Implement lazy loading for all property card images in index.html.
Use the Intersection Observer API for optimal performance.
```

**ADW bot will**:

- Comment on the issue with the ADW ID and status
- Execute the workflow
- Post updates as the workflow progresses
- Report final success/failure with commit hash or error

### For Deployment

#### Manual Deployment

```bash
# Build and deploy to Cloudflare Pages
./scripts/deploy.sh
```

#### Automated Deployment (Future)

Create a GitHub Action (`.github/workflows/deploy.yml`):

```yaml
name: Deploy to Cloudflare Pages

on:
  push:
    branches: [main]
    paths:
      - 'apps/index_lite/**'

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Build Index Lite
        run: ./scripts/build.sh

      - name: Deploy to Cloudflare Pages
        uses: cloudflare/pages-action@v1
        with:
          apiToken: ${{ secrets.CLOUDFLARE_API_TOKEN }}
          accountId: ${{ secrets.CLOUDFLARE_ACCOUNT_ID }}
          projectName: index-lite
          directory: apps/index_lite/dist
```

---

## Troubleshooting

### Common Issues

#### 1. Webhook Not Receiving Events

**Symptoms**: GitHub shows webhook delivery failed

**Solutions**:

- Check webhook server is running: `curl http://localhost:8001/health`
- Verify tunnel is active: `curl https://your-tunnel-url/health`
- Check GitHub webhook settings: Recent Deliveries tab
- Inspect webhook logs in terminal running `start_webhook.sh`

#### 2. Agent Execution Fails

**Symptoms**: Task stays stuck at `[🟡, adw-xxx]`

**Solutions**:

```bash
# Check agent logs
cat agents/adw-xxx/build/execution.log

# Verify ANTHROPIC_API_KEY is set
echo $ANTHROPIC_API_KEY

# Test Claude Code CLI manually
claude --version

# Check .env file is loaded
uv run adws/adw_tests/health_check.py
```

#### 3. Worktree Creation Fails

**Symptoms**: Error: "Cannot create worktree"

**Solutions**:

```bash
# Check git is initialized
git status

# Ensure no uncommitted changes
git add .
git commit -m "WIP"

# Verify worktree base path
ls -la ../

# Manually create worktree to test
git worktree add ../test-worktree-manual
```

#### 4. Build Fails

**Symptoms**: `./scripts/build.sh` errors

**Solutions**:

```bash
# Check package.json exists
cat apps/index_lite/package.json

# Verify Node.js installed (if using npm build)
node --version
npm --version

# Run build manually
cd apps/index_lite
npm run build
# or
npm run build-windows
```

#### 5. Deployment Fails

**Symptoms**: Wrangler deployment errors

**Solutions**:

```bash
# Re-authenticate with Cloudflare
wrangler login

# Check account ID
wrangler whoami

# Verify project name in .env
grep CLOUDFLARE_PAGES_PROJECT_NAME .env

# Test wrangler manually
cd apps/index_lite
wrangler pages deploy dist --project-name=index-lite
```

### Debug Mode

**Enable verbose logging**:

```bash
# For webhook
DEBUG=1 ./scripts/start_webhook.sh

# For cron trigger
uv run adws/adw_triggers/trigger_cron.py --verbose --once
```

**Check agent output**:

```bash
# List all agent runs
ls -la agents/

# View specific agent output
cat agents/adw-abc123/build/cc_raw_output.json | jq .

# View agent summary
cat agents/adw-abc123/build/custom_summary_output.json
```

---

## Future Enhancements

### Phase 7: Advanced Features (Post-MVP)

1. **Automated Testing**
   - Add slash command `/test` to run UI tests
   - Integrate with Playwright for browser testing
   - Screenshot regression testing

2. **Review Workflow**
   - Add `/review` command for code review
   - Screenshot comparison for visual changes
   - Upload screenshots to Cloudflare R2

3. **Analytics Integration**
   - Track agent execution metrics
   - Monitor deployment frequency
   - Measure task completion time

4. **Multi-App Support**
   - Add more apps to apps/ directory
   - Shared components library
   - Cross-app task orchestration

5. **Advanced Deployment**
   - Preview deployments for PRs
   - A/B testing infrastructure
   - Rollback automation

---

## Summary Checklist

### Implementation Steps

- [ ] **Phase 1**: Repository Setup
  - [ ] Initialize git repository
  - [ ] Create GitHub repository
  - [ ] Connect local to remote
  - [ ] Handle index_lite git history

- [ ] **Phase 2**: Trigger System
  - [ ] Add github.py, state.py, workflow_ops.py modules
  - [ ] Copy and adapt trigger_webhook.py
  - [ ] Add health_check.py

- [ ] **Phase 3**: Environment Configuration
  - [ ] Update .env.sample with all variables
  - [ ] Create .env file with actual values
  - [ ] Update agent.py environment handling

- [ ] **Phase 4**: Development Scripts
  - [ ] Create start_dev.sh
  - [ ] Create build.sh
  - [ ] Create deploy.sh
  - [ ] Create start_webhook.sh
  - [ ] Create start_cron.sh

- [ ] **Phase 5**: Testing & Validation
  - [ ] Test local dev server
  - [ ] Test build process
  - [ ] Test health check
  - [ ] Test webhook server
  - [ ] Test agent execution
  - [ ] Test full workflow end-to-end

- [ ] **Phase 6**: Deployment
  - [ ] Configure Cloudflare Pages
  - [ ] Test manual deployment
  - [ ] Configure GitHub webhook
  - [ ] Test GitHub webhook integration

### Post-Implementation

- [ ] Document any deviations from plan
- [ ] Create first real task in tasks.md
- [ ] Create first real GitHub issue with ADW workflow
- [ ] Monitor agent logs for errors
- [ ] Optimize polling intervals
- [ ] Set up monitoring/alerting (optional)

---

## Conclusion

This implementation plan provides a comprehensive, step-by-step guide to deeply integrating the Index Lite static website with the Multi-Agent Task Orchestration (Todone) agentic layer.

**Key Outcomes**:

✅ **Webhook-triggered workflows** via GitHub issues
✅ **Automated task distribution** from tasks.md
✅ **Parallel development** in git worktrees
✅ **AI-driven implementation** via Claude Code
✅ **Automated deployment** to Cloudflare Pages
✅ **Comprehensive monitoring** via health checks and logs

**Next Steps**:

1. Execute Phase 1-6 in sequence
2. Test thoroughly at each phase
3. Document any issues or deviations
4. Create your first AI-driven task
5. Monitor and optimize

**Success Criteria**:

- [ ] Index Lite loads correctly on localhost
- [ ] Agents can execute tasks from tasks.md
- [ ] GitHub issues trigger workflows
- [ ] Deployments succeed to Cloudflare Pages
- [ ] All health checks pass

---

**Document Version**: 1.0
**Last Updated**: October 18, 2025
**Author**: Claude Code Implementation Planning Agent
**Status**: Ready for Implementation
