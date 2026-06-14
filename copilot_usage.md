# ◈ GitHub Copilot Usage — CertPathAI

> **Microsoft Agents League 2026 — Reasoning Agents Track**
> This document evidences how GitHub Copilot was used throughout
> the development of CertPathAI.

---

## How Copilot Was Used

### 1. 6-Agent Pipeline Architecture (`agents/*.py`)

The multi-agent system was scaffolded with Copilot.

**Prompt used:**
```
Build a multi-agent certification readiness system for engineering teams.
Six agents in sequence:
Agent 1 — Learner Profiler: identifies skill gaps and checks prerequisites
using Fabric IQ semantic analysis.
Agent 2 — Learning Path Curator: retrieves grounded study resources from
Foundry IQ knowledge base with citations.
Agent 3 — Study Plan Generator: builds a weekly schedule using Planner →
Executor pattern with Largest Remainder algorithm for fair domain allocation.
Agent 4 — Engagement Agent: monitors learner rhythm using Work IQ signals
and triggers contextual reminders.
Agent 5 — Assessment Agent: generates practice questions using Critic →
Verifier pattern with question quality scoring.
Agent 6 — Manager Insights Agent: produces team-level decisions
(GO / CONDITIONAL_GO / NOT_YET) using composite scoring.
Each agent should return a structured dict with a 'reasoning' field
for full auditability.
```

**Copilot generated:** The complete pipeline structure, the data flow
between agents, the standard agent contract (input → reasoning → output
+ citation), and the orchestration pattern.

---

### 2. 17-Rule Guardrail Pipeline (`guardrails.py`)

The full guardrail system was generated with Copilot.

**Prompt used:**
```
Generate a 17-rule guardrail pipeline that validates every agent output.
Organise rules into 5 categories:
- Schema rules R01-R04: required fields, no nulls, string length, numeric range
- Safety rules R05-R08: no autonomous booking, no clinical advice,
  valid decisions, no "guaranteed pass" language
- Grounding rules R09-R11: citations present, no hallucinated cert IDs,
  reasoning field present and auditable
- Logic rules R12-R15: decision/score consistency, progress capped,
  no zero-hour domains, valid readiness signals
- Privacy rules R16-R17: no PII in outputs, synthetic IDs only
Each rule should return (passed: bool, message: str). The pipeline should
return a GuardrailResult dataclass with pass/fail status, violations list,
warnings list, and pass rate. Include a run_all_guardrails function that
audits all 6 agents in one call.
```

**Copilot generated:** The complete 17-rule validation engine, the
agent-specific rule sets dictionary, the GuardrailResult dataclass, and
the aggregation logic for cross-agent reporting.

---

### 3. Largest Remainder Algorithm (`agents/agent3_planner.py`)

**Prompt used:**
```
Implement the Largest Remainder allocation algorithm to fairly distribute
study hours across exam domains based on their weights. The algorithm
should ensure no domain receives zero hours, and total allocated hours
exactly match the requested total. Handle edge cases where weights sum
to less than 1.0 due to rounding.
```

**Copilot generated:** The full Largest Remainder implementation with
floor/remainder calculation, fractional ranking, and integer rounding
to exact target total.

---

### 4. Critic → Verifier Pattern (`agents/agent5_assessment.py`)

**Prompt used:**
```
Implement a Critic → Verifier reasoning pattern for the assessment agent.
The Critic generates practice questions for each skill gap, then the
Verifier reviews question quality (clarity, difficulty calibration,
domain coverage) and scores 0-100%. If quality < 70%, regenerate.
Return both the questions and the critic's review for transparency.
```

**Copilot generated:** The full critic-verifier loop with quality scoring,
regeneration logic, and structured review output.

---

### 5. Composite Decision Scoring (`agents/agent6_manager.py`)

**Prompt used:**
```
Build a composite scoring engine that combines four signals into a single
GO / CONDITIONAL_GO / NOT_YET decision:
- Assessment score (40% weight)
- Engagement consistency (25% weight)
- Foundry IQ grounding score (20% weight)
- Work IQ capacity signal (15% weight)
Thresholds: composite >= 75 → GO, 60-74 → CONDITIONAL_GO, <60 → NOT_YET.
If prerequisites not met, override to NOT_YET regardless of score.
Include human_confirmation_required flag — system never auto-books exams.
```

**Copilot generated:** The complete weighted scoring function, threshold
mapping, prerequisite override logic, and the human-in-the-loop flag.

---

### 6. Streamlit Dual-Mode UI (`app.py`)

**Prompt used:**
```
Generate a Streamlit dashboard with two modes:
1. Individual Learner mode — pick a learner from sidebar, run full
6-agent pipeline, show per-agent outputs with expandable reasoning traces.
2. Manager Dashboard mode — aggregate view across all 5 learners with
team readiness percentage, decision breakdown (GO / CONDITIONAL / NOT_YET
counts), at-risk learners list.
Use a dark cosmic theme with Inter font. Include a demo mode banner at
the top showing offline status and guardrail/test counts. Add a
Pipeline Trace section showing per-agent timing and full guardrail audit
log with severity-coded violations.
```

**Copilot generated:** The complete 400+ line CSS block, the dual-mode
toggle logic, the per-agent expandable reasoning panels, and the
guardrail audit display.

---

### 7. Evaluation Suite (`eval.py`)

**Prompt used:**
```
Generate a 30+ test evaluation suite for CertPathAI. Cover: data integrity
(5 learners, 5 certifications, no real PII), each agent's contract
(reasoning, required fields, citations), reasoning patterns (Planner-
Executor, Critic-Verifier), edge cases (blocked learners, prerequisite
failures), guardrail integration (305 rules across 5 learners), and
determinism (same input → same output).
```

**Copilot generated:** The complete test suite with 33 individual
assertions, the pass/fail tracking pattern, and the summary block.

---

### 8. Debugging Assistance

Throughout development, Copilot Chat was used to:
- Fix the Agent 3 zero-hour domain bug (Largest Remainder edge case)
- Resolve the Agent 4 progress overflow bug (% > 100)
- Handle the N/A composite score for prerequisite-blocked learners
- Fix the guardrail R11 None reasoning crash
- Refine the Manager Dashboard learner table sorting

---

## Summary

| Component | Copilot Role |
|---|---|
| 6-agent pipeline architecture | Full scaffolding |
| 17-rule guardrail pipeline | Full generation |
| Largest Remainder algorithm | Full generation |
| Critic → Verifier pattern | Full generation |
| Composite decision scoring | Full generation |
| Streamlit dual-mode UI | Full generation |
| 33-test eval suite | Full generation |
| Bug fixes + refinement | Copilot Chat throughout |

> GitHub Copilot was integral to every layer of this project — from
> initial architecture to final eval pass. Development time was reduced
> by an estimated 60-70%.
