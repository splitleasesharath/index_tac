#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///

"""
Simple standalone test for Claude Code on Max Plan (authenticated mode).

This script tests that Claude Code works WITHOUT an API key,
using your authenticated Claude Max Plan subscription.

Usage:
    uv run tests/test_claude_max.py

Expected: Should work without ANTHROPIC_API_KEY environment variable.
"""

import subprocess
import sys
import os
import json
import tempfile
from pathlib import Path


# Claude Code CLI path - update this if needed
# Found via: where claude (Windows) or which claude (Mac/Linux)
CLAUDE_PATH = r"C:\Users\igor\AppData\Roaming\npm\claude.cmd"


def print_header(text: str):
    """Print a formatted header."""
    print(f"\n{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}\n")


def print_success(text: str):
    """Print success message."""
    print(f" {text}")


def print_error(text: str):
    """Print error message."""
    print(f"L {text}")


def print_info(text: str):
    """Print info message."""
    print(f"9  {text}")


def check_claude_installed():
    """Check if Claude Code CLI is installed."""
    print_info("Checking if Claude Code is installed...")

    try:
        result = subprocess.run(
            [CLAUDE_PATH, "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )

        if result.returncode == 0:
            version = result.stdout.strip()
            print_success(f"Claude Code found: {version}")
            return True
        else:
            print_error("Claude Code CLI is not working")
            return False

    except FileNotFoundError:
        print_error("Claude Code CLI not found in PATH")
        print_info("Install from: https://claude.com/claude-code")
        return False
    except subprocess.TimeoutExpired:
        print_error("Claude Code version check timed out")
        return False


def check_api_key_status():
    """Check if API key is set (should NOT be needed on max branch)."""
    print_info("Checking API key status...")

    api_key = os.getenv("ANTHROPIC_API_KEY")

    if api_key:
        print_info(f"API key is set (starts with: {api_key[:10]}...)")
        print_info("On max branch, this is optional - will use if available")
    else:
        print_success("No API key set - will use authenticated Claude Code (Max Plan)")

    return True


def test_claude_simple_prompt():
    """Test Claude Code with a simple prompt."""
    print_info("Testing Claude Code with simple prompt...")
    print_info("Prompt: 'What is 2+2? Reply only with the number.'")

    # Create temporary file for output
    with tempfile.NamedTemporaryFile(mode='w', suffix='.jsonl', delete=False) as tmp:
        output_file = tmp.name

    try:
        # Prepare environment - explicitly REMOVE API key to test authenticated mode
        env = os.environ.copy()
        if "ANTHROPIC_API_KEY" in env:
            print_info("Temporarily removing API key to test authenticated mode...")
            del env["ANTHROPIC_API_KEY"]

        # Run Claude Code with simple prompt
        cmd = [
            CLAUDE_PATH,
            "-p",
            "What is 2+2? Reply only with the number.",
            "--output-format",
            "stream-json",
            "--verbose",
            "--dangerously-skip-permissions"
        ]

        print_info("Executing Claude Code CLI...")
        print_info("(This may take 5-15 seconds for first request)")

        with open(output_file, 'w') as f:
            result = subprocess.run(
                cmd,
                stdout=f,
                stderr=subprocess.PIPE,
                text=True,
                env=env,
                timeout=30
            )

        # Check result
        if result.returncode != 0:
            print_error(f"Claude Code execution failed")
            print_error(f"Error: {result.stderr}")
            return False

        # Parse output
        response_found = False
        response_text = ""

        with open(output_file, 'r') as f:
            for line in f:
                if line.strip():
                    try:
                        msg = json.loads(line)
                        if msg.get("type") == "result":
                            response_text = msg.get("result", "")
                            response_found = True
                            break
                    except json.JSONDecodeError:
                        continue

        if response_found:
            print_success("Claude Code responded successfully!")
            print_success(f"Response: {response_text.strip()[:100]}")

            # Check if response contains "4"
            if "4" in response_text:
                print_success("Response is correct (contains '4')")
            else:
                print_info(f"Response doesn't contain '4', but Claude responded")

            return True
        else:
            print_error("No response found in output")
            return False

    except subprocess.TimeoutExpired:
        print_error("Claude Code request timed out after 30 seconds")
        print_info("This might indicate authentication issues")
        return False
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        return False
    finally:
        # Clean up temp file
        if os.path.exists(output_file):
            os.unlink(output_file)


def main():
    """Run all tests."""
    print_header("Claude Code Max Plan Test")
    print_info("Testing authenticated Claude Code (no API key required)")
    print_info("Branch: max")

    all_passed = True

    # Test 1: Check Claude is installed
    if not check_claude_installed():
        print_error("\nTest failed: Claude Code not installed")
        sys.exit(1)

    # Test 2: Check API key status
    if not check_api_key_status():
        print_error("\nTest failed: API key check")
        sys.exit(1)

    # Test 3: Test actual Claude Code execution
    if not test_claude_simple_prompt():
        print_error("\nTest failed: Claude Code execution")
        all_passed = False

    # Final result
    print_header("Test Results")

    if all_passed:
        print_success("All tests passed! (")
        print_success("Claude Code is working on Max Plan (authenticated mode)")
        print_success("You can now use the ADW system without an API key")
        sys.exit(0)
    else:
        print_error("Some tests failed")
        print_info("\nTroubleshooting:")
        print_info("1. Ensure you're logged into Claude Code: claude auth login")
        print_info("2. Check authentication: claude auth status")
        print_info("3. Verify Max Plan subscription is active")
        sys.exit(1)


if __name__ == "__main__":
    main()
