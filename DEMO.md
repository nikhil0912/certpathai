# 🎯 CertPathAI — Judge Demo Guide

> **Microsoft Agents League 2026 · Reasoning Agents Track**
> Estimated demo time: **3 minutes**

This guide walks you through the complete reasoning pipeline. Everything runs locally — no Azure credentials, no setup beyond `pip install`.

---

## ⚡ 60-Second Quick Start

```bash
git clone https://github.com/nikhil0912/certpathai
cd certpathai
pip install -r requirements.txt
streamlit run app.py
```

Open `http://localhost:8501` — you'll see the cosmic dark UI loaded with the 6-agent pipeline.

---

## 🎬 Demo Path 1 — The GO Decision (Riley Park)

**The story:** Senior data engineer ready to book the DP-203 exam.

| Step | Action | What to look for |
|---|---|---|
| 1 | Select **Riley Park (L-1004)** in the sidebar | Profile shows 82% practice score, 22h studied |
| 2 | Cert defaults to **DP-203** | All prerequisites met |
| 3 | Click **▶️ Run Full Pipeline** | Watch all 6 agents execute in ~40ms |
| 4 | Scroll through agent results | Each agent shows reasoning + outputs |
| 5 | Reach **Agent 6 — Manager Insights** | Final decision: **✅ GO** at 82% composite |
| 6 | Expand **🔍 Pipeline Trace** | See all 17 guardrail rules passed, per-agent timing |

**What judges should notice:**
- All 61 guardrail rules pass
- Total pipeline time under 50ms
- Every agent output has a `reasoning` field — full auditability
- Human confirmation flag is enforced — agent does not autonomously book

---

## 🎬 Demo Path 2 — The Blocked Case (Jordan Smith)

**The story:** Software engineer wants AZ-400 but lacks the AZ-204 prerequisite.

| Step | Action | What to look for |
|---|---|---|
| 1 | Select **Jordan Smith (L-1002)** | Target cert: AZ-400 |
| 2 | Click **▶️ Run Full Pipeline** | Agent 1 immediately flags missing prereq |
| 3 | Agent 6 returns **NOT_YET** | Score: `Blocked (prereqs)` — handled cleanly |
| 4 | Read the reason | "Complete AZ-204 first" |

**What judges should notice:**
- The system does not give a misleading score for blocked learners
- Decision is honest: NOT_YET, not a fudged number
- No "guaranteed pass" language anywhere (caught by guardrail R08)

---

## 🎬 Demo Path 3 — Manager Dashboard (Team View)

| Step | Action | What to look for |
|---|---|---|
| 1 | In sidebar, switch to **👥 Manager Dashboard** | Auto-runs all 5 learners |
| 2 | See team-level metrics | 40% team readiness, 2 GO, 1 CONDITIONAL, 2 NOT_YET |
| 3 | Scroll the per-learner table | Sorted decisions across the team |
| 4 | Check **at-risk** and **capacity-constrained** lists | Work IQ signals surfaced |

---

## 🧪 Run the Evaluation Suite

```bash
python eval.py
```

**Expected output:** `33/33 tests passing, 100% score`

Tests cover: data integrity, all 6 agents, reasoning patterns, responsible AI, guardrails, decision logic, edge cases.

---

## 🔍 Reasoning Traces — Where to Look

Every agent exposes its full reasoning. Look for these in the UI:

| Agent | Reasoning Pattern | Field to inspect |
|---|---|---|
| Agent 1 — Profiler | Fabric IQ semantic gap analysis | `reasoning`, `skill_gaps`, `domain_weights` |
| Agent 2 — Curator | Foundry IQ grounded retrieval | `cited_resources`, `grounding_score_pct` |
| Agent 3 — Planner | **Planner → Executor** + Largest Remainder algorithm | `weekly_schedule`, `domain_hour_allocations` |
| Agent 4 — Engagement | Work IQ rhythm signals | `reminders`, `work_iq_rationale` |
| Agent 5 — Assessment | **Critic → Verifier** with grounded questions | `questions`, `critic_review` |
| Agent 6 — Manager | Threshold-based composite decision | `composite_score`, `decision`, `confidence` |

---

## 🛡️ 17-Rule Guardrail Pipeline

| Category | Rules | What's checked |
|---|---|---|
| **Schema** | R01–R04 | Required fields, no nulls, length, numeric range |
| **Safety** | R05–R08 | No autonomous booking, no clinical advice, valid decisions, no "guaranteed pass" |
| **Grounding** | R09–R11 | Citations, no hallucinated cert IDs, reasoning auditable |
| **Logic** | R12–R15 | Score consistency, progress capped, no zero-hour domains, valid signals |
| **Privacy** | R16–R17 | No PII, synthetic IDs only |

Visible in UI under **🔍 Pipeline Trace — Guardrail Audit Log**.

---

## 🏛️ Architecture at a Glance

```
Learner Profile → Curated Path → Study Plan
        ↓
   Engagement ← Assessment → Manager Decision
        ↓
   All outputs → 17-rule Guardrail Pipeline
        ↓
   GO / CONDITIONAL_GO / NOT_YET
```

Open `architecture.html` in a browser for the full visual diagram.

---

## 🧭 Reasoning Patterns Demonstrated

| Pattern | Where | Why it matters |
|---|---|---|
| **Planner → Executor** | Agent 3 | Largest Remainder ensures no domain gets 0 hours |
| **Critic → Verifier** | Agent 5 | Question quality is reviewed before scoring |
| **Self-reflection** | Agents 1, 5, 6 | Low-confidence outputs trigger re-evaluation |
| **Tool use** | All agents | Each agent calls its own retrieval and reasoning tools |

---

## 🔒 Responsible AI

- **All data is synthetic** — `data/learners.json`, no real PII
- **Citations on every grounded output** — `cited_resources` field
- **Human confirmation required** before any exam booking
- **No clinical or medical advice** ever
- **No guaranteed pass promises** — only readiness signals
- **17-rule guardrail audit** on every agent output

---

## 📂 Repo Structure

```
certpathai/
├── app.py                  # Streamlit dual-mode UI
├── guardrails.py           # 17-rule pipeline
├── eval.py                 # 33-test evaluation suite
├── architecture.html       # Full architecture diagram
├── agents/
│   ├── agent1_profiler.py
│   ├── agent2_curator.py
│   ├── agent3_planner.py
│   ├── agent4_engagement.py
│   ├── agent5_assessment.py
│   └── agent6_manager.py
└── data/
    ├── certifications.json # Fabric IQ semantic model
    ├── learners.json       # 5 synthetic learners
    └── work_signals.json   # Work IQ signals
```

---

*All data is synthetic. Built entirely for the Agents League 2026 hackathon.*
