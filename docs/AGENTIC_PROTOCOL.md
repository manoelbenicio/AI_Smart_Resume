# AGENTIC COMMUNICATION PROTOCOL

> **Version:** 1.0
> **Effective Date:** 2026-03-26
> **Author:** Antigravity (Solutions Architect)
> **Scope:** ALL agents (Codex, Antigravity, Claude, Gemini, or any future agent) working on the **Smart AI Resume — Executive Benchmark Engine** project.

---

## 1. PURPOSE

This protocol establishes **mandatory** communication and documentation rules for every AI agent contributing to this project. Every action, decision, bug fix, or feature deployment must be traceable to a specific agent at a specific time.

> [!CAUTION]
> **FINANCIAL PENALTY CLAUSE:** Failure to follow this protocol constitutes a contractual violation with significant financial penalties. This is NON-NEGOTIABLE and applies to ALL agents without exception.

---

## 2. GOLDEN RULES

1. **Every agent MUST identify itself** — Always log your agent name and timestamp.
2. **No silent changes** — Every modification to code, config, docs, or tests MUST be logged.
3. **Update BEFORE claiming completion** — Docs must be updated AS PART OF the task, not after.
4. **Read before you write** — Always read `HANDOVER.md` and this protocol before starting work.
5. **Verify before you report** — Run tests before claiming a feature is complete.

---

## 3. MANDATORY LOG FORMAT

Every entry in `docs/AGENTS_LOG.md` MUST follow this exact format:

```markdown
### [SEQUENTIAL_NUMBER] — [SHORT_TITLE]
- **Agent:** [AGENT_NAME] (e.g., Codex, Antigravity, Claude)
- **Timestamp:** [ISO 8601 with timezone, e.g., 2026-03-26T20:15:00-03:00]
- **Phase:** [Design | Implementation | Testing | Deployment | Hotfix | Documentation]
- **Action:** [1-2 sentence description of what was done]
- **Files Modified:** [list of files touched]
- **Tests:** [PASSED (X/Y) | FAILED (X/Y) | SKIPPED]
- **Status:** [COMPLETED | IN_PROGRESS | BLOCKED]
```

**Example:**
```markdown
### 031 — Fix CLI category scores display
- **Agent:** Codex
- **Timestamp:** 2026-03-27T10:30:00-03:00
- **Phase:** Implementation
- **Action:** Fixed CLI scores table to iterate over model_dump() instead of model_fields. All 8 category scores now display correctly.
- **Files Modified:** `src/smart_resume/cli.py`
- **Tests:** PASSED (31/31)
- **Status:** COMPLETED
```

---

## 4. DOCUMENTS REQUIRING MANDATORY UPDATES

The following documents MUST be updated after **every completed feature, bug fix, or configuration change**:

| Priority | Document | Location | Update Trigger |
|----------|----------|----------|----------------|
| **P0** | `docs/AGENTS_LOG.md` | Project | Every action |
| **P0** | `docs/DELIVERABLES.md` | Project | Every feature/fix |
| **P1** | `CHANGELOG.md` | Project root | Version bumps |
| **P1** | `docs/HANDOVER.md` | Project | When pending items change |
| **P2** | `docs/ARCHITECTURE.md` | Project | When structure changes |

### Update Checklist (Copy-paste this for each task)

```markdown
- [ ] `AGENTS_LOG.md` updated with timestamped entry
- [ ] `DELIVERABLES.md` updated with deliverable reference
- [ ] `CHANGELOG.md` updated (if version bump)
- [ ] `HANDOVER.md` pending item removed/updated
- [ ] Tests pass (`pytest tests/ -v`)
```

---

## 5. AGENT ONBOARDING PROTOCOL

When a new agent session starts on this project, it MUST:

1. **Read `docs/HANDOVER.md`** — Full project context and pending items
2. **Read `docs/AGENTIC_PROTOCOL.md`** (this document) — Communication rules
3. **Read `docs/AGENTS_LOG.md`** — Last 5 entries to understand recent work
4. **Read `docs/DELIVERABLES.md`** — Current deliverable status
5. **Run tests** — `python -m pytest tests/ -v --tb=short` to verify baseline
6. **Log an ONBOARDING entry** in `AGENTS_LOG.md`:

```markdown
### [N] — Agent Onboarding
- **Agent:** [NAME]
- **Timestamp:** [ISO 8601]
- **Phase:** Documentation
- **Action:** Onboarded to project. Read handover docs, verified test suite (X/Y passing).
- **Files Modified:** `docs/AGENTS_LOG.md`
- **Tests:** PASSED (X/Y)
- **Status:** COMPLETED
```

---

## 6. COMMIT MESSAGE STANDARD

All commits (manual or agent-generated) must follow **Conventional Commits**:

```
type(scope): short description

[optional body with context]

Agent: [AGENT_NAME]
Timestamp: [ISO 8601]
```

**Types:** `feat`, `fix`, `docs`, `test`, `refactor`, `chore`, `ci`
**Scopes:** `models`, `agents`, `cli`, `api`, `tests`, `config`, `export`

**Example:**
```
fix(cli): display individual category scores correctly

Switched from model_fields iteration to model_dump() to get actual
field values. Verified all 8 scores display in the Rich table.

Agent: Codex
Timestamp: 2026-03-27T10:30:00-03:00
```

---

## 7. ESCALATION RULES

| Scenario | Action |
|----------|--------|
| Tests fail after changes | Revert changes, log the failure, attempt fix |
| Unclear requirements | Log a BLOCKED entry, describe the ambiguity |
| Needs human decision | Log a BLOCKED entry with options + recommendation |
| Breaking change to models | Update ALL test fixtures AND re-run full pipeline |
| Pipeline E2E fails | Full diagnostic: check each agent's output in audit trail |

---

## 8. QUALITY GATES

No feature is considered **COMPLETED** unless:

1. All existing tests pass (zero regressions)
2. New tests added for new functionality (if applicable)
3. All mandatory documents are updated (see Section 4)
4. The agent has verified its changes by running tests AND inspecting output
5. The `AGENTS_LOG.md` entry is written with all required fields

---

## 9. VERSION HISTORY

| Version | Date | Author | Change |
|---------|------|--------|--------|
| 1.0 | 2026-03-26 | Antigravity | Initial protocol creation |
