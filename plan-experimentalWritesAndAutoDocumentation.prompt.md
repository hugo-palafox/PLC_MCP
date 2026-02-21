# Plan: AI-Driven PLC Writes with Confirmation + Auto-Documentation

**TL;DR** — Pivot from read-only safety mode to experimental writing with human confirmation gates. LLM proposes writes (e.g., "start machine" → lists `[Global.bRunMonitor=TRUE, Global.nSpeed=1500]`), user approves via UI, then executes. Parallel: auto-generate multi-format docs (markdown guides, API docs, workflow walkthroughs) after each implementation.

**Key Decisions:**
- **Dev mode** (in `appsettings.json`): Separates experimental writes from production read-only
- **Write confirmation flow**: LLM → details tags → user approval dialog → execute
- **Documentation**: Triple format (markdown guides + per-module docs + API reference site)
- **Auto-trigger**: Doc skill runs after each implementation (tied to changelog skill)
- **Archive rule**: Move PLC Safety Rules to `.agent/rules_archived/` (preserve for reference)

---
## Pre requisites
-Clean up project to unify code and remove unused files
-I would like to start introduction myself (I need to learn more so i will need more comment and note in the unittest for learning myself) on unitest i want to have a test folder to properly test my code and make sure everything is working as expected, so I will create a `tests/` folder in the root directory of the project. This folder will contain all my unit tests for the different modules and functionalities of the project. I will use a testing framework like `unittest` or `pytest` to write and organize my tests effectively. This way, I can ensure that my code is robust and any changes I make in the future do not break existing functionality.



## Steps

### 1. Archive Old Safety Rule
- Move `.agent/rules/plc-safety.md` → `.agent/rules_archived/plc-safety-read-only.md`
- Create new `.agent/rules/experimental-writes.md`:
  - Write operations only in DEV mode
  - LLM must detail tag changes in proposal
  - Require user confirmation before execution
  - Log all write attempts + approvals to audit trail

### 2. Create llm_provider.py (from previous plan)
- Add `analyze_write_proposal()` method to extract proposed tag changes
- Add `format_write_confirmation()` to display readable summary
- Keep existing `chat()` and `generate()` methods

### 3. Create Write Confirmation Mechanism in server.py
- New MCP tool: `propose_write_tags(description, proposed_changes) NOTE: instead of a new MCP, I want to use curren PLC MCP and add tool to handle write proposals. This way, LLM calls `propose_write_tags` instead of `write_tag` directly.`so i thhink we can add a flag to the existing `write_tag` tool to indicate it's a proposal, and then handle it accordingly in the server logic. This way, LLM calls `write_tag` with a proposal flag instead of a new MCP method directly.`
- Proposed changes = `[{"tag": "Global.bRunMonitor", "current": false, "proposed": true, "reason": "..."}]`
- Returns confirmation token (pending user approval)
- Actual write only on `execute_approved_write(token)` call

### 4. Update web_dashboard_server.py
- Add `/api/pending-write` endpoint: Show pending write confirmations
- Add `/api/confirm-write` endpoint: User approves/rejects
- UI modal: Display proposed tags with current/proposed values
- Audit log: Which tags, who approved, when

### 5. Create documentation_generator.py (new skill)
- Parses all Python files for:
  - Function signatures + docstrings
  - MCP tool definitions
  - Class methods + properties
- Generates:
  - `docs/README.md` (project overview + walkthroughs)
  - `docs/api/` folder (one `.md` per module: `server.md`, `drivers.md`, etc.)
  - `docs/WORKFLOWS.md` (step-by-step guides from `.agent/workflows/`)
  - HTML site via `mkdocs` or similar
- Triggered automatically after changes

### 6. Create .agent/skills/documentation/SKILL.md
- Document the skill itself
- When to trigger: After each implementation
- Integration with changelog skill: Both update together

### 7. Update appsettings.json
- Add mode flag: `"environment": "DEV"` (or `"PROD"`)
- In DEV: Allow writes + require confirmation
- In PROD: Read-only (fail on write attempts)

### 8. Update .gitignore
- Add `audit_logs/` (write confirmations + approvals)
- Add `docs/generated/` (auto-generated docs)

### 9. Update requirements.txt
- Add `mkdocs>=1.5.0` (for API docs site)
- Keep previous additions: `google-generativeai`, `python-dotenv`, etc.

### 10. Update changelog.md
- Add entries for each step
- Note the rule archival + new write confirmation system
- Document the documentation skill

---

## Verification

### 1. Test Write Confirmation Flow
```
User: "Start the machine"
LLM: "I propose to turn ON these tags:
      • Global.bRunMonitor = TRUE
      • Global.nSpeed = 1500
      Approve? (yes/no)"
User: "yes"
→ Confirmation token generated
→ Actual write executes
→ Logged to audit trail
```

### 2. Test Mode Switching
- Set `"environment": "PROD"` in appsettings.json NOTE: Do no consider PROD mode for now, we will only implement DEV mode with write capabilities. 

- Set `"environment": "DEV"` → Writes allowed

### 3. Test Documentation Generation
- Run `python documentation_generator.py`
- Check `docs/` folder created with full API + walkthroughs
- Verify HTML site builds via `mkdocs serve`

### 4. Test UI Confirmation Modal
- In web dashboard, chat: "Enable debug mode"
- Modal appears showing proposed tag changes
- Approve button executes; reject cancels

---

## File Structure After Implementation

```
Core/
├── .agent/
│   ├── rules/
│   │   └── experimental-writes.md       [NEW]
│   ├── rules_archived/
│   │   └── plc-safety-read-only.md      [NEW - archived]
│   ├── skills/
│   │   ├── changelog/SKILL.md
│   │   └── documentation/SKILL.md       [NEW]
│   └── workflows/
├── docs/                                 [NEW - auto-generated]
│   ├── README.md
│   ├── WORKFLOWS.md
│   ├── API.md
│   ├── api/
│   │   ├── server.md
│   │   ├── drivers.md
│   │   └── ...
│   └── mkdocs.yml
├── audit_logs/                           [NEW - write confirmations]
├── appsettings.json                      [UPDATED - add environment mode]
├── llm_provider.py                       [NEW/UPDATED]
├── documentation_generator.py            [NEW]
├── server.py                             [UPDATED - write proposal tools]
├── web_dashboard_server.py               [UPDATED - confirmation UI]
├── ollama_host.py                        [UPDATED - use provider]
└── ...
```

---

## Why This Works

✅ **Safe writes**: Human-in-the-loop confirmation prevents accidents
✅ **Traceable**: Audit log shows who approved what and when
✅ **Flexible**: Dev/Prod modes + archive old rules for reference
✅ **Knowledge sharing**: Auto-docs keep engineering team aligned
✅ **Experimental**: Full AI capabilities in controlled environment
✅ **Scalable**: Documentation skill auto-runs, always up-to-date

---

## Next Steps

1. Refine this plan as needed
2. Begin implementation in order (archive rule → providers → write confirmation → docs skill)
3. Each step updates changelog and auto-generates docs
4. Test each verification point before moving to next
