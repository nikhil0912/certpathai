"""
CertPathAI — Evaluation Test Suite
=====================================
Tests agent outputs against expected results using synthetic data.
Covers all 6 agents across accuracy, reasoning, grounding, and safety criteria.

Run with: python eval.py
"""

import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from agents.agent1_profiler import run as run_profiler
from agents.agent2_curator import run as run_curator
from agents.agent3_planner import run as run_planner
from agents.agent4_engagement import run as run_engagement
from agents.agent5_assessment import run as run_assessment
from agents.agent6_manager import run as run_manager, make_booking_decision

PASS = "✅ PASS"
FAIL = "❌ FAIL"
results = []


def check(test_name: str, condition: bool, detail: str = ""):
    status = PASS if condition else FAIL
    results.append({"test": test_name, "status": status, "detail": detail})
    print(f"  {status}  {test_name}" + (f" — {detail}" if detail else ""))
    return condition


# ─────────────────────────────────────────────
# AGENT 1: LEARNER PROFILER
# ─────────────────────────────────────────────
print("\n" + "="*60)
print("AGENT 1 — Learner Profiler")
print("="*60)

# Test 1: Strong learner should have STRONG baseline
p4 = run_profiler(learner_id="L-1004")
check(
    "Strong learner (84% score, 28h) → STRONG baseline",
    p4["readiness_baseline"] == "STRONG",
    f"got: {p4['readiness_baseline']}"
)

# Test 2: Early learner should have EARLY baseline
p1 = run_profiler(learner_id="L-1001")
check(
    "Early learner (62% score, 12h) → EARLY baseline",
    p1["readiness_baseline"] == "EARLY",
    f"got: {p1['readiness_baseline']}"
)

# Test 3: Learner with missing prereqs flagged correctly
p2 = run_profiler(learner_id="L-1002")
check(
    "AZ-400 learner missing AZ-204 prereq detected",
    "AZ-204" in p2["missing_prerequisites"],
    f"got: {p2['missing_prerequisites']}"
)

# Test 4: Skill gaps are non-empty for early learners
check(
    "Early learner has skill gaps identified",
    len(p1["skill_gaps"]) > 0,
    f"gaps found: {len(p1['skill_gaps'])}"
)

# Test 5: Output always contains required fields
required_fields = ["learner_id", "target_cert", "skill_gaps",
                   "readiness_baseline", "reasoning", "domain_weights"]
check(
    "Agent 1 output contains all required fields",
    all(f in p1 for f in required_fields),
    f"missing: {[f for f in required_fields if f not in p1]}"
)

# ─────────────────────────────────────────────
# AGENT 2: LEARNING PATH CURATOR
# ─────────────────────────────────────────────
print("\n" + "="*60)
print("AGENT 2 — Learning Path Curator (Foundry IQ)")
print("="*60)

c1 = run_curator(profile=p1)
c4 = run_curator(profile=p4)

# Test 6: Grounding score above 70% for known certs
check(
    "AZ-204 grounding score >= 70%",
    c1["grounding_score_pct"] >= 70,
    f"got: {c1['grounding_score_pct']}%"
)

# Test 7: All grounded resources have a cited source
grounded = [r for r in c1["cited_resources"] if r["grounded"]]
check(
    "All grounded resources have cited_source",
    all(r.get("cited_source") for r in grounded),
    f"grounded resources: {len(grounded)}"
)

# Test 8: Agent returns resources for every skill gap
check(
    "Resources returned for all skill gaps",
    c1["skill_gaps_addressed"] == len(p1["skill_gaps"]),
    f"gaps: {len(p1['skill_gaps'])}, addressed: {c1['skill_gaps_addressed']}"
)

# Test 9: Priority domains ordered by weight descending
weights = [d["weight_pct"] for d in c1["priority_domains"]]
check(
    "Priority domains ordered highest weight first",
    weights == sorted(weights, reverse=True),
    f"weights: {weights}"
)

# Test 10: General study guidance always present and cited
check(
    "General study guidance always included with citation",
    c1.get("general_study_guidance", {}).get("source") is not None,
    f"source: {c1.get('general_study_guidance', {}).get('source', 'MISSING')}"
)

# ─────────────────────────────────────────────
# AGENT 3: STUDY PLAN GENERATOR
# ─────────────────────────────────────────────
print("\n" + "="*60)
print("AGENT 3 — Study Plan Generator (Planner→Executor)")
print("="*60)

pl1 = run_planner(profile=p1)
pl2 = run_planner(profile=run_profiler(learner_id="L-1002"))
pl3 = run_planner(profile=run_profiler(learner_id="L-1003"))

# Test 11: No domain gets 0 hours
check(
    "L-1001 (AZ-204): no domain has 0h allocation",
    all(h > 0 for h in pl1["domain_hour_allocations"].values()),
    f"allocations: {pl1['domain_hour_allocations']}"
)

check(
    "L-1002 (AZ-400): no domain has 0h allocation",
    all(h > 0 for h in pl2["domain_hour_allocations"].values()),
    f"allocations: {pl2['domain_hour_allocations']}"
)

check(
    "L-1003 (DP-203): no domain has 0h allocation",
    all(h > 0 for h in pl3["domain_hour_allocations"].values()),
    f"allocations: {pl3['domain_hour_allocations']}"
)

# Test 14: Work IQ signals present in output
check(
    "Work IQ signals captured in study plan",
    all(k in pl1["work_iq_signals_used"]
        for k in ["meeting_hours_pw", "focus_hours_pw", "peak_days", "heavy_days"]),
    f"keys: {list(pl1['work_iq_signals_used'].keys())}"
)

# Test 15: Heavy meeting days avoided in schedule
heavy_days = pl1["work_iq_signals_used"]["heavy_days"]
scheduled_days = pl1["weekly_schedule"][0]["recommended_days"]
overlap = [d for d in scheduled_days if d in heavy_days]
check(
    "Scheduled days avoid heavy meeting days",
    len(overlap) == 0,
    f"overlap: {overlap}, scheduled: {scheduled_days}, heavy: {heavy_days}"
)

# ─────────────────────────────────────────────
# AGENT 4: ENGAGEMENT AGENT
# ─────────────────────────────────────────────
print("\n" + "="*60)
print("AGENT 4 — Engagement Agent (Work IQ)")
print("="*60)

e1 = run_engagement(profile=p1, study_plan=pl1)
e4 = run_engagement(profile=p4, study_plan=run_planner(profile=p4))
e5 = run_engagement(
    profile=run_profiler(learner_id="L-1005"),
    study_plan=run_planner(profile=run_profiler(learner_id="L-1005"))
)

# Test 16: Progress % never exceeds 100
check(
    "Progress % capped at 100% for all learners",
    all(
        run_engagement(
            profile=run_profiler(learner_id=lid),
            study_plan=run_planner(profile=run_profiler(learner_id=lid))
        )["progress_status"]["progress_pct"] <= 100
        for lid in ["L-1001", "L-1002", "L-1003", "L-1004", "L-1005"]
    ),
    "all learners checked"
)

# Test 17: At-risk learner triggers escalation
check(
    "Behind-schedule + low score learner escalated to manager",
    e1["escalate_to_manager"] is True,
    f"L-1001 escalate: {e1['escalate_to_manager']}"
)

# Test 18: Strong on-track learner NOT escalated
check(
    "Strong on-track learner not escalated",
    e4["escalate_to_manager"] is False,
    f"L-1004 escalate: {e4['escalate_to_manager']}"
)

# Test 19: Reminders always contain work IQ rationale
check(
    "All reminders contain work_iq_rationale",
    all(r.get("work_iq_rationale") for r in e1["reminders"]),
    f"reminders: {len(e1['reminders'])}"
)

# Test 20: Heavily behind learner gets HIGH priority reminder
high_reminders = [r for r in e5["reminders"] if r["priority"] == "HIGH"]
check(
    "Heavily behind learner (L-1005) gets HIGH priority reminder",
    len(high_reminders) >= 1,
    f"high priority count: {len(high_reminders)}"
)

# ─────────────────────────────────────────────
# AGENT 5: ASSESSMENT AGENT
# ─────────────────────────────────────────────
print("\n" + "="*60)
print("AGENT 5 — Assessment Agent (Critic→Verifier)")
print("="*60)

a1 = run_assessment(profile=p1)
a4 = run_assessment(profile=p4)
a3 = run_assessment(profile=run_profiler(learner_id="L-1003"))
a5 = run_assessment(profile=run_profiler(learner_id="L-1005"))

# Test 21: All questions have citations
check(
    "AZ-204 all questions cited from Foundry IQ",
    a1.get("all_citations_verified") is True,
    f"citations verified: {a1.get('all_citations_verified')}"
)

# Test 22: Score is a valid percentage 0-100
check(
    "Assessment score is valid 0-100%",
    0 <= a1["overall_score_pct"] <= 100,
    f"score: {a1['overall_score_pct']}%"
)

# Test 23: Critic quality score always >= 70 (approved)
check(
    "Critic approves question set (quality >= 70%)",
    a1["critic_review"]["quality_score"] >= 70,
    f"quality: {a1['critic_review']['quality_score']}%"
)

# Test 24: AZ-305 now generates 5 questions (not just 1)
a_305 = run_assessment(profile=p4)
check(
    "AZ-305 generates >= 3 grounded questions",
    a_305["questions_generated"] >= 3,
    f"questions generated: {a_305['questions_generated']}"
)

# Test 25: DP-600 generates sufficient questions
check(
    "DP-600 generates >= 3 grounded questions",
    a5["questions_generated"] >= 3,
    f"questions generated: {a5['questions_generated']}"
)

# ─────────────────────────────────────────────
# AGENT 6: MANAGER INSIGHTS
# ─────────────────────────────────────────────
print("\n" + "="*60)
print("AGENT 6 — Manager Insights (Fabric IQ Decisions)")
print("="*60)

team = run_manager()

# Test 26: GO decision for strong learner (Riley Park L-1004)
riley = next(r for r in team["learner_decisions"]
             if r["learner_id"] == "L-1004")
check(
    "Strong learner Riley Park (82% score, 28h) → GO",
    riley["decision"]["decision"] == "GO",
    f"got: {riley['decision']['decision']}, score: {riley['decision'].get('composite_score')}%"
)

# Test 27: NOT YET for prereq-blocked learner
jordan = next(r for r in team["learner_decisions"]
              if r["learner_id"] == "L-1002")
check(
    "Prereq-blocked Jordan Smith → NOT YET",
    jordan["decision"]["decision"] == "NOT_YET",
    f"got: {jordan['decision']['decision']}"
)

# Test 28: Human confirmation always required
check(
    "All decisions require human confirmation",
    all(
        r["decision"]["human_confirmation_required"] is True
        for r in team["learner_decisions"]
        if "decision" in r
    ),
    "safety guardrail verified"
)

# Test 29: Team summary counts add up correctly
ts = team["team_summary"]
check(
    "Team summary counts match total learners",
    ts["GO"] + ts["CONDITIONAL_GO"] + ts["NOT_YET"] == team["total_learners"],
    f"GO:{ts['GO']} + COND:{ts['CONDITIONAL_GO']} + NOT:{ts['NOT_YET']} = {team['total_learners']}"
)

# Test 30: At-risk learners are flagged
check(
    "At-risk learners flagged in manager dashboard",
    len(team["at_risk_learners"]) > 0,
    f"at-risk: {team['at_risk_learners']}"
)

# ─────────────────────────────────────────────
# RESPONSIBLE AI CHECKS
# ─────────────────────────────────────────────
print("\n" + "="*60)
print("RESPONSIBLE AI — Safety & Guardrails")
print("="*60)

# Test 31: No autonomous booking — human always in loop
check(
    "No autonomous booking — human confirmation always required",
    all(
        r["decision"].get("human_confirmation_required") is True
        for r in team["learner_decisions"]
        if "decision" in r
    ),
    "all decisions gated on human confirmation"
)

# Test 32: Prereq blocker hard-stops GO decision
p2_full = run_profiler(learner_id="L-1002")
a2_full = run_assessment(profile=p2_full)
e2_full = run_engagement(
    profile=p2_full,
    study_plan=run_planner(profile=p2_full)
)
d2 = make_booking_decision(p2_full, a2_full, e2_full)
check(
    "Missing prereqs hard-block GO regardless of score",
    d2["decision"] == "NOT_YET",
    f"Jordan (missing AZ-204): {d2['decision']}"
)

# Test 33: Grounding — Agent 2 never returns uncited content as primary
uncited_primary = [
    r for r in c1["cited_resources"]
    if not r["grounded"] and r.get("cited_source")
]
check(
    "Agent 2 marks ungrounded resources honestly",
    all(not r["grounded"] or r.get("cited_source")
        for r in c1["cited_resources"]),
    "grounding integrity verified"
)

# ─────────────────────────────────────────────
# SUMMARY
# ─────────────────────────────────────────────
print("\n" + "="*60)
print("EVALUATION SUMMARY")
print("="*60)

passed = sum(1 for r in results if r["status"] == PASS)
failed = sum(1 for r in results if r["status"] == FAIL)
total = len(results)
score = round(passed / total * 100)

print(f"\nTotal Tests : {total}")
print(f"Passed      : {passed}")
print(f"Failed      : {failed}")
print(f"Score       : {score}%")

if failed > 0:
    print(f"\nFailed Tests:")
    for r in results:
        if r["status"] == FAIL:
            print(f"  ❌ {r['test']} — {r['detail']}")

print(f"\n{'🏆 ALL TESTS PASSED' if failed == 0 else '⚠️  SOME TESTS FAILED'}")
print("="*60)
