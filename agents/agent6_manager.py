"""
Agent 6: Manager Insights Agent
---------------------------------
Team-level visibility agent. Aggregates signals from all other agents
across the full learner cohort and produces:
  - GO / CONDITIONAL GO / NOT YET booking decision per learner
  - Team risk map and readiness summary
  - Capacity-constrained learner flags
  - Manager dashboard data
Uses Fabric IQ semantic thresholds + Work IQ capacity signals.
"""

import json
from pathlib import Path
from agents.agent1_profiler import run as profiler_run
from agents.agent3_planner import run as planner_run
from agents.agent4_engagement import run as engagement_run
from agents.agent5_assessment import run as assessment_run

DATA_DIR = Path(__file__).parent.parent / "data"


def load_certifications():
    with open(DATA_DIR / "certifications.json") as f:
        return json.load(f)


def load_learners():
    with open(DATA_DIR / "learners.json") as f:
        return json.load(f)


def load_work_signals():
    with open(DATA_DIR / "work_signals.json") as f:
        return json.load(f)


def make_booking_decision(
    profile: dict,
    assessment: dict,
    engagement: dict
) -> dict:
    """
    Final GO / CONDITIONAL GO / NOT YET decision using Fabric IQ thresholds.
    Human confirmation required before any exam booking.
    """
    cert_data = load_certifications()
    thresholds = cert_data["readiness_thresholds"]

    practice_score = profile.get("practice_score_avg", 0)
    hours_studied = profile.get("hours_studied", 0)
    missing_prereqs = profile.get("missing_prerequisites", [])
    at_risk = engagement.get("escalate_to_manager", False)

    # Assessment score — default to practice score if assessment unavailable
    assessment_score = assessment.get("overall_score_pct")
    if assessment_score is None or assessment.get("error"):
        assessment_score = practice_score

    # Hard blocker: missing prerequisites
    if missing_prereqs:
        return {
            "decision": "NOT_YET",
            "confidence": "HIGH",
            "composite_score": None,
            "practice_score": practice_score,
            "assessment_score": assessment_score,
            "hours_studied": hours_studied,
            "reason": (
                f"Missing prerequisites: {', '.join(missing_prereqs)}. "
                f"Complete these first before scheduling exam."
            ),
            "action": (
                "Complete prerequisite certification(s) before scheduling this exam."
            ),
            "color": "RED",
            "human_confirmation_required": True
        }

    # Composite score: weighted average
    composite = round((practice_score * 0.4) + (assessment_score * 0.6))

    go_t = thresholds["GO"]
    cgo_t = thresholds["CONDITIONAL_GO"]

    if (composite >= go_t["min_practice_score"]
            and hours_studied >= go_t["min_hours_studied"]
            and not at_risk):
        decision = "GO"
        confidence = "HIGH" if composite >= 80 else "MEDIUM"
        reason = (
            f"Composite readiness score {composite}% with {hours_studied}h studied "
            f"exceeds GO thresholds (≥75% score, ≥18h studied)."
        )
        action = "Schedule exam within 2 weeks. Maintain current study pace."
        color = "GREEN"

    elif (composite >= cgo_t["min_practice_score"]
          and hours_studied >= cgo_t["min_hours_studied"]):
        decision = "CONDITIONAL_GO"
        confidence = "MEDIUM"
        reason = (
            f"Composite score {composite}% meets conditional threshold "
            f"but not fully optimised."
        )
        action = "Address weak domains first. Re-assess in 1 week before booking."
        color = "AMBER"

    else:
        decision = "NOT_YET"
        confidence = "HIGH"
        reason = (
            f"Composite score {composite}% and/or {hours_studied}h studied "
            f"below minimum thresholds (≥65% score, ≥12h studied)."
        )
        action = (
            "Continue study plan. Re-assess after completing recommended hours."
        )
        color = "RED"

    return {
        "decision": decision,
        "confidence": confidence,
        "composite_score": composite,
        "practice_score": practice_score,
        "assessment_score": assessment_score,
        "hours_studied": hours_studied,
        "reason": reason,
        "action": action,
        "color": color,
        "human_confirmation_required": True
    }


def run_for_learner(learner_id: str) -> dict:
    """Run full pipeline for a single learner."""
    profile = profiler_run(learner_id=learner_id)
    if "error" in profile:
        return {"learner_id": learner_id, "error": profile["error"]}

    study_plan = planner_run(profile=profile)
    engagement = engagement_run(profile=profile, study_plan=study_plan)
    assessment = assessment_run(profile=profile)
    decision = make_booking_decision(profile, assessment, engagement)

    return {
        "learner_id": learner_id,
        "learner_name": profile.get("learner_name"),
        "role": profile.get("role"),
        "target_cert": profile.get("target_cert"),
        "decision": decision,
        "profile_summary": {
            "skill_coverage_pct": profile.get("skill_coverage_pct"),
            "readiness_baseline": profile.get("readiness_baseline"),
            "hours_studied": profile.get("hours_studied"),
            "hours_remaining": profile.get("hours_remaining_estimate"),
            "practice_score": profile.get("practice_score_avg")
        },
        "engagement_summary": {
            "on_track": engagement["progress_status"]["on_track"],
            "at_risk": engagement.get("escalate_to_manager"),
            "reminders_count": len(engagement.get("reminders", []))
        },
        "assessment_summary": {
            "score_pct": assessment.get("overall_score_pct"),
            "readiness_signal": assessment.get("readiness_signal"),
            "weak_domains": assessment.get("weak_domains", [])
        },
        "study_plan_summary": {
            "weeks_planned": study_plan.get("weeks_planned"),
            "total_hours": study_plan.get("total_planned_hours"),
            "preferred_slot": study_plan.get("preferred_study_slot")
        }
    }


def run(learner_ids: list = None) -> dict:
    """
    Run full team-level analysis and produce manager dashboard.
    """
    if learner_ids is None:
        learners = load_learners()
        learner_ids = [l["learner_id"] for l in learners]

    learner_results = [run_for_learner(lid) for lid in learner_ids]

    decisions = [
        r["decision"]["decision"]
        for r in learner_results
        if "decision" in r
    ]
    go_count = decisions.count("GO")
    cgo_count = decisions.count("CONDITIONAL_GO")
    not_yet_count = decisions.count("NOT_YET")
    at_risk = [
        r for r in learner_results
        if r.get("engagement_summary", {}).get("at_risk")
    ]

    cert_groups = {}
    for r in learner_results:
        cert = r.get("target_cert", "Unknown")
        if cert not in cert_groups:
            cert_groups[cert] = {"GO": 0, "CONDITIONAL_GO": 0, "NOT_YET": 0}
        d = r.get("decision", {}).get("decision", "NOT_YET")
        cert_groups[cert][d] += 1

    work_signals = load_work_signals()
    capacity_constrained = [
        w["learner_id"]
        for w in work_signals
        if w.get("meeting_hours_per_week", 0) >= 20
    ]

    team_readiness_pct = (
        round(go_count / len(decisions) * 100) if decisions else 0
    )

    result = {
        "agent": "Manager Insights Agent",
        "total_learners": len(learner_results),
        "team_summary": {
            "GO": go_count,
            "CONDITIONAL_GO": cgo_count,
            "NOT_YET": not_yet_count,
            "team_readiness_pct": team_readiness_pct
        },
        "learner_decisions": learner_results,
        "at_risk_learners": [r["learner_id"] for r in at_risk],
        "capacity_constrained_learners": capacity_constrained,
        "cert_track_breakdown": cert_groups,
        "fabric_iq_thresholds_used": {
            "GO": ">=75% composite score + >=18h studied",
            "CONDITIONAL_GO": ">=65% composite score + >=12h studied",
            "NOT_YET": "Below CONDITIONAL_GO thresholds"
        },
        "manager_actions": [
            f"⚠️  {len(at_risk)} learner(s) flagged at-risk — review study support",
            f"📅  {len(capacity_constrained)} learner(s) capacity-constrained (20+ meeting hrs/week)",
            f"✅  {go_count}/{len(decisions)} learner(s) ready to book exam",
            "🔒  All decisions require human confirmation before exam booking"
        ],
        "reasoning": (
            f"Team of {len(learner_results)}: "
            f"{go_count} GO, {cgo_count} CONDITIONAL GO, {not_yet_count} NOT YET. "
            f"Team readiness: {team_readiness_pct}%. "
            f"{len(at_risk)} at-risk learner(s) flagged for manager attention. "
            f"Decisions use Fabric IQ semantic thresholds. "
            f"Human confirmation required before any exam booking."
        )
    }

    return result


if __name__ == "__main__":
    result = run()
    print(f"\n{'='*60}")
    print("AGENT 6 OUTPUT — MANAGER DASHBOARD")
    print(f"{'='*60}")
    ts = result["team_summary"]
    print(f"Team Readiness:        {ts['team_readiness_pct']}%")
    print(f"GO: {ts['GO']} | CONDITIONAL: {ts['CONDITIONAL_GO']} | NOT YET: {ts['NOT_YET']}")
    print(f"At Risk:               {result['at_risk_learners']}")
    print(f"Capacity Constrained:  {result['capacity_constrained_learners']}")
    print(f"\nManager Actions:")
    for action in result["manager_actions"]:
        print(f"  {action}")
    print(f"\nPer-Learner Decisions:")
    for lr in result["learner_decisions"]:
        if "decision" in lr:
            d = lr["decision"]
            score_display = (
                f"{d['composite_score']}%"
                if d.get("composite_score") is not None
                else "Blocked (prereqs)"
            )
            print(
                f"  {lr['learner_name']:15} | "
                f"{lr['target_cert']:8} | "
                f"{d['decision']:16} | "
                f"Score: {score_display}"
            )
