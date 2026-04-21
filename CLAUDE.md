# AWS LLMOps Project - Claude Code Guide

## 🔄 Critical: Session Context Required

**⚠️ MANDATORY**: On every new chat session, you MUST read these files IN ORDER:

### 1️⃣ **Environment Constraints** (必読)
**File**: `/docs/progress_log_constraints.md`
- Docker is NOT available locally — CloudShell only
- This is a **safety-critical constraint**

### 2️⃣ **AI Directives** (必読)
**File**: `/docs/progress_log_directives.md`
- 16 mandatory rules for AI behavior
- Rules 3, 9, 12, 14, 16 are CRITICAL
- This controls how you handle files, documents, and handoffs

### 3️⃣ **Current State** (必読)
**File**: `/docs/progress_log_trusted_state.md`
- Current Phase, verified resources, next steps
- This is the "single source of truth" — treat it as authoritative
- Do NOT verify things listed as ✅

### 4️⃣ **Session History** (As needed)
**File**: `/docs/Progress_log.md`
- Original file contains detailed session records
- Read only if you need to understand past decisions or blockers
- Focus on the most recent session entry

## 📋 Project Quick Reference

- **Project Type**: AWS LLMOps Hands-on Generator
- **Language**: Python
- **Infrastructure**: AWS SAM + Lambda + DynamoDB + Bedrock
- **Observability**: Langfuse v4 (SDK integration)
- **Testing**: pytest + GitHub Actions (CI/CD)

---

## ⏱️ Session Start Checklist (Copy-paste friendly)

Before you start working:

- [ ] Read `progress_log_constraints.md` (Docker constraints)
- [ ] Read `progress_log_directives.md` (16 rules)
- [ ] Read `progress_log_trusted_state.md` (Current state)
- [ ] Skim `Progress_log.md` most recent session (if needed)
- [ ] Ready to start

## 🔑 Key Files & Aliases

| Alias | Path | Purpose |
|-------|------|---------|
| **constraints** | `/docs/progress_log_constraints.md` | **[SESSION START]** Environment & safety constraints |
| **directives** | `/docs/progress_log_directives.md` | **[SESSION START]** 16 mandatory AI rules |
| **trusted_state** | `/docs/progress_log_trusted_state.md` | **[SESSION START]** Current verified state (Phase, resources) |
| progress_log | `/docs/Progress_log.md` | Session history & detailed decisions |
| implementation_checklist | `/docs/AI専用_実装前チェックリスト.md` | Pre-implementation validation (STEP 1-6) |
| usecase | `/docs/ユースケース_シナリオ_理由.md` | Business requirements & scenario context |
| manager_checklist | `/docs/Manager_Checklist.md` | Supervisor workflow & evidence tracking |

## 🚫 Strict Constraints

1. **No Docker locally** — use AWS CloudShell for `sam build`, `docker build`, etc.
2. **API Key handling** — never commit API keys; use environment variables
3. **Cost control** — target ≤ $1-3/month for hands-on work (discuss changes with user)

## 📝 Handover Pattern

At the end of each session, update Progress_log.md with:
- What was completed
- What failed and why
- Next steps and blockers
- Langfuse SDK version info (if relevant)

This ensures continuity across sessions.

---

**Last updated**: 2026-04-21 (Session 66)
