#!/usr/bin/env uv run
# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "python-dotenv",
#     "pydantic",
# ]
# ///

"""
Health Check Script for ADW System

Usage:
uv run adws/health_check.py <issue_number>

This script performs comprehensive health checks:
1. Validates all required environment variables
2. Checks git repository configuration
3. Tests Claude Code CLI functionality
4. Returns structured results
"""

import os
import sys
import json
import subprocess
import tempfile
from typing import Dict, List, Optional, Any
from datetime import datetime
from pathlib import Path
import argparse

from dotenv import load_dotenv
from pydantic import BaseModel

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import git repo functions from github module
from adw_modules.github import get_repo_url, extract_repo_path, make_issue_comment
from adw_modules.utils import get_safe_subprocess_env

# Load environment variables
load_dotenv()


class CheckResult(BaseModel):
    """Individual check result."""

    success: bool
    error: Optional[str] = None
    warning: Optional[str] = None
    details: Dict[str, Any] = {}


class HealthCheckResult(BaseModel):
    """Structure for health check results."""

    success: bool
    timestamp: str
    checks: Dict[str, CheckResult]
    warnings: List[str] = []
    errors: List[str] = []


def check_env_vars() -> CheckResult:
    """Check required environment variables.

    Note: On 'max' branch, ANTHROPIC_API_KEY is optional since we use
    authenticated Claude Code (Claude Max Plan).
    """
    required_vars = {
        "CLAUDE_CODE_PATH": "Path to Claude Code CLI (defaults to 'claude')",
    }

    optional_vars = {
        "ANTHROPIC_API_KEY": "(Optional) Anthropic API Key - not needed if using authenticated Claude Code",
        "GITHUB_PAT": "(Optional) GitHub Personal Access Token - only needed if you want ADW to use a different GitHub account than 'gh auth login'",
        "E2B_API_KEY": "(Optional) E2B API Key for sandbox environments",
        "CLOUDFLARED_TUNNEL_TOKEN": "(Optional) Cloudflare tunnel token for webhook exposure",
        "CLOUDFLARE_ACCOUNT_ID": "(Optional) Cloudflare account ID for R2 screenshot uploads",
        "CLOUDFLARE_R2_ACCESS_KEY_ID": "(Optional) R2 access key ID for screenshot uploads",
        "CLOUDFLARE_R2_SECRET_ACCESS_KEY": "(Optional) R2 secret access key for screenshot uploads",
        "CLOUDFLARE_R2_BUCKET_NAME": "(Optional) R2 bucket name for screenshot storage",
        "CLOUDFLARE_R2_PUBLIC_DOMAIN": "(Optional) Custom domain for public R2 access",
    }

    missing_required = []
    missing_optional = []

    # Check required vars
    for var, desc in required_vars.items():
        if not os.getenv(var):
            if var == "CLAUDE_CODE_PATH":
                # This has a default, so not critical
                continue
            missing_required.append(f"{var} ({desc})")

    # Check optional vars
    for var, desc in optional_vars.items():
        if not os.getenv(var):
            missing_optional.append(f"{var} ({desc})")

    success = len(missing_required) == 0

    return CheckResult(
        success=success,
        error="Missing required environment variables" if not success else None,
        details={
            "missing_required": missing_required,
            "missing_optional": missing_optional,
            "claude_code_path": os.getenv("CLAUDE_CODE_PATH", "claude"),
        },
    )


def check_git_repo() -> CheckResult:
    """Check git repository configuration using github module."""
    try:
        # Get repo URL using the github module function
        repo_url = get_repo_url()
        repo_path = extract_repo_path(repo_url)

        # Check if still using disler's repo
        is_disler_repo = "disler" in repo_path.lower()

        return CheckResult(
            success=True,
            warning=(
                "Repository still points to 'disler'. Please update to your own GitHub repository."
                if is_disler_repo
                else None
            ),
            details={
                "repo_url": repo_url,
                "repo_path": repo_path,
                "is_disler_repo": is_disler_repo,
            },
        )
    except ValueError as e:
        return CheckResult(success=False, error=str(e))


def check_claude_code() -> CheckResult:
    """Test Claude Code CLI functionality."""
    claude_path = os.getenv("CLAUDE_CODE_PATH", "claude")

    # Check if Claude Code is installed and get version
    try:
        result = subprocess.run(
            [claude_path, "--version"], capture_output=True, text=True, timeout=5
        )
        if result.returncode != 0:
            return CheckResult(
                success=False,
                error=f"Claude Code CLI not functional at '{claude_path}'",
            )

        version = result.stdout.strip()

    except FileNotFoundError:
        return CheckResult(
            success=False,
            error=f"Claude Code CLI not found at '{claude_path}'. Please install or set CLAUDE_CODE_PATH correctly.",
        )
    except subprocess.TimeoutExpired:
        return CheckResult(
            success=False,
            error="Claude Code version check timed out",
        )

    # Check if ANTHROPIC_API_KEY is set (optional on 'max' branch)
    api_key = os.getenv("ANTHROPIC_API_KEY")
    auth_mode = "API Key" if api_key else "Authenticated Claude Code (Max Plan)"

    if api_key and not api_key.startswith("sk-ant-"):
        return CheckResult(
            success=True,
            warning="ANTHROPIC_API_KEY may be invalid (should start with 'sk-ant-'), but using authenticated mode as fallback",
            details={
                "version": version,
                "authentication_mode": auth_mode,
            },
        )

    # All checks passed - Claude Code is ready (with or without API key)
    return CheckResult(
        success=True,
        details={
            "version": version,
            "authentication_mode": auth_mode,
            "note": "Using authenticated Claude Code - no API key required on 'max' branch",
        },
    )


def check_github_cli() -> CheckResult:
    """Check if GitHub CLI is installed and authenticated."""
    try:
        # Check if gh is installed
        result = subprocess.run(["gh", "--version"], capture_output=True, text=True)
        if result.returncode != 0:
            return CheckResult(success=False, error="GitHub CLI (gh) is not installed")

        # Check authentication status - don't use filtered env for gh auth
        # gh needs access to system keyring/credential manager on Windows
        result = subprocess.run(
            ["gh", "auth", "status"], capture_output=True, text=True
        )

        authenticated = result.returncode == 0

        return CheckResult(
            success=authenticated,
            error="GitHub CLI not authenticated" if not authenticated else None,
            details={"installed": True, "authenticated": authenticated},
        )

    except FileNotFoundError:
        return CheckResult(
            success=False,
            error="GitHub CLI (gh) is not installed. Install with: brew install gh",
            details={"installed": False},
        )


def run_health_check() -> HealthCheckResult:
    """Run all health checks and return results."""
    result = HealthCheckResult(
        success=True, timestamp=datetime.now().isoformat(), checks={}
    )

    # Check environment variables
    env_check = check_env_vars()
    result.checks["environment"] = env_check
    if not env_check.success:
        result.success = False
        if env_check.error:
            result.errors.append(env_check.error)
        # Add specific missing vars to errors
        missing_required = env_check.details.get("missing_required", [])
        result.errors.extend(
            [f"Missing required env var: {var}" for var in missing_required]
        )
    # Don't add warnings for optional env vars - they're optional!

    # Check git repository
    git_check = check_git_repo()
    result.checks["git_repository"] = git_check
    if not git_check.success:
        result.success = False
        if git_check.error:
            result.errors.append(git_check.error)
    elif git_check.warning:
        result.warnings.append(git_check.warning)

    # Check GitHub CLI
    gh_check = check_github_cli()
    result.checks["github_cli"] = gh_check
    if not gh_check.success:
        result.success = False
        if gh_check.error:
            result.errors.append(gh_check.error)

    # Check Claude Code - only if we have the API key
    if os.getenv("ANTHROPIC_API_KEY"):
        claude_check = check_claude_code()
        result.checks["claude_code"] = claude_check
        if not claude_check.success:
            result.success = False
            if claude_check.error:
                result.errors.append(claude_check.error)
    else:
        result.checks["claude_code"] = CheckResult(
            success=False,
            details={"skipped": True, "reason": "ANTHROPIC_API_KEY not set"},
        )

    return result


def main():
    """Main entry point."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="ADW System Health Check")
    parser.add_argument(
        "issue_number",
        nargs="?",
        help="Optional GitHub issue number to post results to",
    )
    args = parser.parse_args()

    print("🏥 Running ADW System Health Check...\n")

    result = run_health_check()

    # Print summary
    print(
        f"{'✅' if result.success else '❌'} Overall Status: {'HEALTHY' if result.success else 'UNHEALTHY'}"
    )
    print(f"📅 Timestamp: {result.timestamp}\n")

    # Print detailed results
    print("📋 Check Results:")
    print("-" * 50)

    for check_name, check_result in result.checks.items():
        status = "✅" if check_result.success else "❌"
        print(f"\n{status} {check_name.replace('_', ' ').title()}:")

        # Print check-specific details
        for key, value in check_result.details.items():
            if value is not None and key not in [
                "missing_required",
                "missing_optional",
            ]:
                print(f"   {key}: {value}")

        if check_result.error:
            print(f"   ❌ Error: {check_result.error}")
        if check_result.warning:
            print(f"   ⚠️  Warning: {check_result.warning}")

    # Print warnings
    if result.warnings:
        print("\n⚠️  Warnings:")
        for warning in result.warnings:
            print(f"   - {warning}")

    # Print errors
    if result.errors:
        print("\n❌ Errors:")
        for error in result.errors:
            print(f"   - {error}")

    # Print next steps
    if not result.success:
        print("\n📝 Next Steps:")
        if any("ANTHROPIC_API_KEY" in e for e in result.errors):
            print("   1. Set ANTHROPIC_API_KEY in your .env file")
        if any("GITHUB_PAT" in e for e in result.errors):
            print("   2. Set GITHUB_PAT in your .env file")
        if any("GitHub CLI" in e for e in result.errors):
            print("   3. Install GitHub CLI: brew install gh")
            print("   4. Authenticate: gh auth login")
        if any("disler" in w for w in result.warnings):
            print(
                "   5. Fork/clone the repository and update git remote to your own repo"
            )

    # If issue number provided, post comment
    if args.issue_number:
        print(f"\n📤 Posting health check results to issue #{args.issue_number}...")
        status_emoji = "✅" if result.success else "❌"
        comment = f"{status_emoji} Health check completed: {'HEALTHY' if result.success else 'UNHEALTHY'}"
        try:
            make_issue_comment(args.issue_number, comment)
            print(f"✅ Posted health check comment to issue #{args.issue_number}")
        except Exception as e:
            print(f"❌ Failed to post comment: {e}")

    # Return appropriate exit code
    sys.exit(0 if result.success else 1)


if __name__ == "__main__":
    main()
