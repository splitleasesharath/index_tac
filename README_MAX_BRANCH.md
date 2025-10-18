# Max Branch - Authenticated Claude Code

This branch (`max`) is configured to use **authenticated Claude Code** with your Claude Max Plan subscription, eliminating the need for an `ANTHROPIC_API_KEY`.

## Key Differences from Main Branch

### 1. No API Key Required 

**Main branch:** Requires `ANTHROPIC_API_KEY` in `.env`
**Max branch:** Uses your authenticated Claude Code session (Claude Max Plan)

### 2. Authentication Mode

The max branch uses your locally authenticated Claude Code CLI, which:
- Uses your Claude.ai account credentials
- Leverages your Claude Max Plan subscription
- No need to manage API keys
- Works with Windows credential manager

### 3. Environment Configuration

**`.env.sample` changes:**
```bash
# OPTIONAL: Anthropic API Configuration
# This branch uses authenticated Claude Code (Claude Max Plan)
# No API key needed - Claude Code uses your local authentication
#
# If you want to use API mode instead, get a key from: https://console.anthropic.com/
# ANTHROPIC_API_KEY=
```

### 4. Code Changes

**Updated files:**
- `adws/adw_modules/agent.py` - Made `ANTHROPIC_API_KEY` optional, added Windows auth env vars
- `adws/adw_tests/health_check.py` - Removed API key requirement, detects auth mode
- `.env.sample` - Documented that API key is optional

**Added Windows environment variables for authentication:**
- `USERPROFILE` - Windows user profile path
- `APPDATA` - Application data folder
- `LOCALAPPDATA` - Local application data
- `USERNAME` - Windows username

These variables allow Claude Code to access the Windows credential manager for authentication.

## Setup Instructions

### 1. Ensure Claude Code is Authenticated

Verify your Claude Code is authenticated with your Max Plan:

```bash
claude --version
```

If not authenticated, run:
```bash
claude auth login
```

### 2. Configure Environment

```bash
# Copy the template
cp .env.sample .env

# Edit .env - NO NEED to set ANTHROPIC_API_KEY
notepad .env  # Windows

# Just configure GitHub settings:
# GITHUB_REPO_URL=https://github.com/splitleasesharath/index_tac
# GITHUB_PAT=your_github_token
```

### 3. Run Health Check

```bash
uv run adws/adw_tests/health_check.py
```

**Expected output:**
```
 Claude Code:
   version: 2.0.22 (Claude Code)
   authentication_mode: Authenticated Claude Code (Max Plan)
   note: Using authenticated Claude Code - no API key required on 'max' branch
```

### 4. Use the System

All scripts work the same way:

```bash
# Start local dev
./scripts/start_dev.sh

# Start task monitor
./scripts/start_cron.sh

# Start webhook
./scripts/start_webhook.sh
```

## Benefits of Max Branch

1. **No API Key Management** - One less secret to manage
2. **Uses Max Plan** - Leverages your existing Claude subscription
3. **Simpler Setup** - Fewer environment variables to configure
4. **Windows-Friendly** - Better integration with Windows credential storage

## Switching Between Branches

### To Max Branch (authenticated mode)
```bash
git checkout max
# No API key needed in .env
```

### To Main Branch (API key mode)
```bash
git checkout main
# Add ANTHROPIC_API_KEY to .env
```

## Troubleshooting

### "Authentication failed" errors

1. **Re-authenticate Claude Code:**
   ```bash
   claude auth logout
   claude auth login
   ```

2. **Verify authentication:**
   ```bash
   claude auth status
   ```

3. **Check health:**
   ```bash
   uv run adws/adw_tests/health_check.py
   ```

### API key warnings

If you see warnings about API key format, that's normal on the max branch - it will fall back to authenticated mode automatically.

## Technical Details

The max branch uses the same Claude Code CLI but relies on your local authentication instead of an API key. When you run `claude` commands:

1. Claude Code checks for `ANTHROPIC_API_KEY` environment variable
2. If not found, falls back to local authentication
3. Reads credentials from Windows credential manager (or keychain on Mac)
4. Connects to Claude.ai using your authenticated session

All agent functionality remains identical - only the authentication method changes.

---

**Branch:** `max`
**Authentication:** Authenticated Claude Code (Max Plan)
**Requires API Key:** No L
**Status:** Ready to use 
