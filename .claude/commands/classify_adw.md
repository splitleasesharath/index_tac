# ADW Workflow Extraction

Extract ADW workflow information from the text below and return a JSON response.

## Instructions

- Look for ADW workflow commands in the text (e.g., `/adw_plan_iso`, `/adw_build_iso`, `/adw_chore_implement`, etc.)
- Commands can appear in many formats:
  - With slash prefix: `/adw_sdlc_iso` or `/adw_plan_iso` or `/adw_chore_implement`
  - Without slash: `adw_sdlc_iso` or `adw_plan_iso` or `adw_chore_implement`
  - With spaces: `adw sdlc iso` or `adw plan iso` or `adw chore implement`
  - Mixed case: `ADW_SDLC_ISO` or `Adw_Chore_Implement`
  - On separate lines from other text
- Also recognize commands without the `_iso` suffix and automatically add it where appropriate
- Look for ADW IDs (8-character alphanumeric strings, often after "adw_id:" or "ADW ID:" or similar)
- Look for model set specification: "model_set base", "model_set sonnet", or "model_set opus" (case insensitive)
  - Default to "base" if no model_set is specified
  - Also recognize variations like "model set: sonnet", "modelset opus", etc.
- Return a JSON object with the extracted information
- If no ADW workflow is found, return empty JSON: `{}`
- CRITICAL: Search the ENTIRE text thoroughly, including all lines. The ADW command might appear anywhere in the text.

## Valid ADW Commands

### ISO Workflows
- `/adw_plan_iso` - Planning only
- `/adw_build_iso` - Building only (requires adw_id)
- `/adw_test_iso` - Testing only (requires adw_id)
- `/adw_review_iso` - Review only (requires adw_id)
- `/adw_document_iso` - Documentation only (requires adw_id)
- `/adw_ship_iso` - Ship/approve and merge PR (requires adw_id)
- `/adw_patch_iso` - Direct patch from issue
- `/adw_plan_build_iso` - Plan + Build
- `/adw_plan_build_test_iso` - Plan + Build + Test
- `/adw_plan_build_review_iso` - Plan + Build + Review (skips test)
- `/adw_plan_build_document_iso` - Plan + Build + Document (skips test and review)
- `/adw_plan_build_test_review_iso` - Plan + Build + Test + Review
- `/adw_sdlc_iso` - Complete SDLC: Plan + Build + Test + Review + Document
- `/adw_sdlc_ZTE_iso` - Zero Touch Execution: Complete SDLC + auto-merge

### Direct Workflows
- `/adw_chore_implement` - Implement a chore (direct execution)

## Response Format

Respond ONLY with a JSON object in this format:
```json
{
  "adw_slash_command": "adw_plan_iso",
  "adw_id": "abc12345",
  "model_set": "base"
}
```

Fields:
- `adw_slash_command`: The ADW command found (WITHOUT slash prefix; include _iso suffix if appropriate)
- `adw_id`: The 8-character ADW ID if found
- `model_set`: The model set to use ("base", "sonnet", or "opus"), defaults to "base" if not specified

If only some fields are found, include only those fields.
If nothing is found, return: `{}`
IMPORTANT: Always include `model_set` with value "base" if no model_set is explicitly mentioned in the text.

## Examples

Example 1 - Simple format:
Input: "adw_sdlc_iso"
Output: `{"adw_slash_command": "adw_sdlc_iso", "model_set": "base"}`

Example 2 - Chore command:
Input: "/feature\n\nadw_chore_implement\n\nAdd Dark Mode"
Output: `{"adw_slash_command": "adw_chore_implement", "model_set": "base"}`

Example 3 - Without _iso suffix:
Input: "adw_plan"
Output: `{"adw_slash_command": "adw_plan_iso", "model_set": "base"}`

Example 4 - With ADW ID:
Input: "adw_build_iso adw_id: abc12345"
Output: `{"adw_slash_command": "adw_build_iso", "adw_id": "abc12345", "model_set": "base"}`

Example 5 - With model set:
Input: "adw_sdlc_iso model_set sonnet"
Output: `{"adw_slash_command": "adw_sdlc_iso", "model_set": "sonnet"}`

Example 6 - Chore with description:
Input: "adw_chore_implement: Fix Windows authentication in webhook subprocess environment variables"
Output: `{"adw_slash_command": "adw_chore_implement", "model_set": "base"}`

## Text to Analyze

$ARGUMENTS
