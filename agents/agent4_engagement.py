"""
Agent 4: Engagement Agent
--------------------------
Monitors learner progress against their study plan and adapts
reminders to work rhythm using Work IQ signals.
Flags at-risk learners to Manager Insights Agent (Agent 6).
"""

import json
from pathlib import Path
from agents.agent3_planner import run as planner_run
from agents.agent1_profiler import run as profiler_run

DATA_DIR = Path(__file__).parent.parent / "data"


def load_work_signals():
    with open(DATA_DIR / "work_signals.json") as f:
        return json.load(f)


def load_certifications():
    with open(DATA_DIR / "certifications.json") as f:
        return json.load(f)


def compute_progress_status(profile: dict, study_plan: dict) -> dict:
    """Assess current progress vs recommended hours — capped at 100%."""
    cert_data = load_certifications()
    cert_id = profile.get("target_cert", "")

    # Use recommended hours as the baseline (not planned hours)
    cert = next(
        (c for c in cert_data["certifications"] if c["id"] == cert_id), None
    )
    recommended_hours = cert["recommended_hours"] if cert else 20

    hours_studied = profile.get("hours_studied", 0)
    weeks_until_target = max(profile.get("weeks_until_target", 1), 1)
    total_weeks = study_plan.get("weeks_planned", 6)
    weeks_elapsed = max(1, total_weeks - weeks_until_target)

    # Expected hours by now: proportional to elapsed weeks
    expected_by_now = (recommended_hours / max(total_weeks, 1)) * weeks_elapsed
    # Cap progress at 100%
    progress_pct = min(100, round((hours_studied / recommended_hours) * 100))
    on_track = hours_studied >= (expected_by_now * 0.80)  # 20% tolerance

    practice_score = profile.get("practice_score_avg", 0)
    if practice_score >= 75:
        score_trend = "strong"
    elif practice_score >= 65:
        score_trend = "developing"
    else:
        score_trend = "needs_attention"

    return {
        "hours_studied": hours_studied,
        "recommended_hours": recommended_hours,
        "hours_expected_by_now": round(expected_by_now, 1),
        "progress_pct": progress_pct,
        "on_track": on_track,
        "score_trend": score_trend,
        "at_risk": not on_track or score_trend == "needs_attention"
    }


def generate_reminders(progress: dict, work_signals: dict, study_plan: dict) -> list:
    """Generate Work IQ-aware reminders — avoids heavy meeting days."""
    reminders = []
    peak_days = work_signals.get("peak_focus_days", ["Tuesday", "Wednesday"])
    heavy_days = work_signals.get("heavy_meeting_days", ["Monday", "Friday"])
    slot = work_signals.get("preferred_learning_slot", "Morning")
    focus_hours = work_signals.get("focus_hours_per_week", 12)
    meeting_hours = work_signals.get("meeting_hours_per_week", 20)

    best_day = next((d for d in peak_days if d not in heavy_days), peak_days[0])
    hours_behind = max(0, progress["hours_expected_by_now"] - progress["hours_studied"])

    if not progress["on_track"]:
        reminders.append({
            "type": "CATCH_UP",
            "priority": "HIGH",
            "message": (
                f"You are {hours_behind:.1f}h behind schedule. "
                f"Consider adding an extra session this {best_day} {slot.lower()}."
            ),
            "suggested_day": best_day,
            "suggested_slot": slot,
            "work_iq_rationale": (
                f"Chosen based on your peak focus day ({best_day}) "
                f"and preferred {slot} slot."
            )
        })

    if focus_hours < 12:
        reminders.append({
            "type": "WORKLOAD_WARNING",
            "priority": "MEDIUM",
            "message": (
                f"Your focus time ({focus_hours}h/week) is below optimal for cert prep. "
                f"Consider blocking 90-min focus windows on {best_day}."
            ),
            "suggested_day": best_day,
            "suggested_slot": slot,
            "work_iq_rationale": (
                f"Work IQ signals: {meeting_hours}h meetings vs "
                f"{focus_hours}h focus — high meeting load detected."
            )
        })

    if progress["score_trend"] == "needs_attention":
        reminders.append({
            "type": "SCORE_ALERT",
            "priority": "HIGH",
            "message": (
                f"Practice score needs attention. "
                f"Focus on weak domains from your study plan this week."
            ),
            "suggested_day": best_day,
            "suggested_slot": slot,
            "work_iq_rationale": (
                "Reminder scheduled during identified focus window "
                "to maximise retention."
            )
        })

    if progress["on_track"] and progress["score_trend"] == "strong":
        reminders.append({
            "type": "POSITIVE_REINFORCEMENT",
            "priority": "LOW",
            "message": (
                f"Great progress! You are {progress['progress_pct']}% through "
                f"your recommended study hours. Keep your {slot.lower()} "
                f"sessions going on {best_day}."
            ),
            "suggested_day": best_day,
            "suggested_slot": slot,
            "work_iq_rationale": (
                "Positive nudge scheduled to maintain momentum "
                "during peak focus time."
            )
        })

    if not reminders:
        reminders.append({
            "type": "ROUTINE_CHECK_IN",
            "priority": "LOW",
            "message": (
                f"Time for your weekly study check-in. "
                f"Review your {study_plan.get('target_cert')} progress."
            ),
            "suggested_day": best_day,
            "suggested_slot": slot,
            "work_iq_rationale": (
                f"Scheduled on {best_day} {slot.lower()} — "
                f"your peak focus window."
            )
        })

    return reminders


def run(
    learner_id: str = None,
    profile: dict = None,
    study_plan: dict = None
) -> dict:
    """
    Monitor progress and generate Work IQ-aware engagement reminders.
    """
    if profile is None:
        profile = profiler_run(learner_id=learner_id)
    if study_plan is None:
        study_plan = planner_run(profile=profile)

    if "error" in profile:
        return profile

    work_signals_data = load_work_signals()
    work_signals = next(
        (w for w in work_signals_data if w["learner_id"] == profile["learner_id"]),
        work_signals_data[0]
    )

    progress = compute_progress_status(profile, study_plan)
    reminders = generate_reminders(progress, work_signals, study_plan)

    escalate_to_manager = progress["at_risk"]
    high_priority = [r for r in reminders if r["priority"] == "HIGH"]

    result = {
        "agent": "Engagement Agent",
        "learner_id": profile["learner_id"],
        "learner_name": profile.get("learner_name"),
        "target_cert": profile.get("target_cert"),
        "progress_status": progress,
        "reminders": reminders,
        "high_priority_count": len(high_priority),
        "escalate_to_manager": escalate_to_manager,
        "work_iq_signals_used": {
            "peak_focus_days": work_signals.get("peak_focus_days"),
            "heavy_meeting_days": work_signals.get("heavy_meeting_days"),
            "preferred_slot": work_signals.get("preferred_learning_slot"),
            "focus_hours_pw": work_signals.get("focus_hours_per_week"),
            "meeting_hours_pw": work_signals.get("meeting_hours_per_week")
        },
        "reasoning": (
            f"Progress: {progress['progress_pct']}% of recommended "
            f"{progress['recommended_hours']}h completed "
            f"({'ON TRACK' if progress['on_track'] else 'BEHIND SCHEDULE'}). "
            f"Score trend: {progress['score_trend']}. "
            f"Generated {len(reminders)} reminder(s), "
            f"{len(high_priority)} high-priority. "
            f"{'⚠️ Escalating to manager.' if escalate_to_manager else '✓ No escalation needed.'}"
        )
    }

    return result


if __name__ == "__main__":
    for lid in ["L-1001", "L-1002", "L-1003", "L-1004", "L-1005"]:
        result = run(learner_id=lid)
        print(f"\n{'='*60}")
        print(f"AGENT 4 OUTPUT — {result.get('learner_name', lid)}")
        print(f"{'='*60}")
        p = result["progress_status"]
        print(f"Progress:  {p['progress_pct']}% | "
              f"Expected: {p['hours_expected_by_now']}h | "
              f"Studied: {p['hours_studied']}h | "
              f"On Track: {p['on_track']}")
        print(f"Escalate:  {result.get('escalate_to_manager')}")
        print(f"Reasoning: {result.get('reasoning')}")
        for r in result.get("reminders", []):
            print(f"  [{r['priority']}] {r['type']}: {r['message'][:80]}")
