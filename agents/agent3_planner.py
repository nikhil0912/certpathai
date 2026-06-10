"""
Agent 3: Study Plan Generator
--------------------------------
Implements the Planner → Executor reasoning pattern.

Planner: Decomposes certification into domain milestones with hour
         allocations using Largest Remainder algorithm.
Executor: Schedules milestones against Work IQ signals
          (meeting load, focus windows, preferred learning slots).
"""

import json
import math
from pathlib import Path
from agents.agent1_profiler import run as profiler_run
from agents.agent2_curator import run as curator_run

DATA_DIR = Path(__file__).parent.parent / "data"


def load_work_signals():
    with open(DATA_DIR / "work_signals.json") as f:
        return json.load(f)


def largest_remainder_allocation(domain_weights: dict, total_hours: float) -> dict:
    """
    Allocate study hours across domains using Largest Remainder Algorithm.
    Guarantees every domain gets at least 1 hour minimum.
    """
    domains = list(domain_weights.keys())
    n = len(domains)

    # Ensure total hours is enough to give every domain at least 1h
    total_hours = max(float(total_hours), float(n))

    raw = {d: domain_weights[d] * total_hours for d in domains}
    floor_alloc = {d: max(1, math.floor(raw[d])) for d in domains}

    # Adjust if floor sum exceeds total
    floor_sum = sum(floor_alloc.values())
    if floor_sum > round(total_hours):
        # Scale back — give each domain proportional share with min 1
        for d in domains:
            floor_alloc[d] = max(1, round(domain_weights[d] * total_hours))

    remainders = {d: raw[d] - floor_alloc[d] for d in domains}
    current_sum = sum(floor_alloc.values())
    target = max(round(total_hours), n)
    hours_to_add = target - current_sum

    if hours_to_add > 0:
        sorted_by_remainder = sorted(remainders.items(), key=lambda x: x[1], reverse=True)
        for i in range(int(hours_to_add)):
            domain = sorted_by_remainder[i % len(sorted_by_remainder)][0]
            floor_alloc[domain] += 1

    return floor_alloc


def plan_milestones(profile: dict, curator_output: dict) -> tuple:
    """PLANNER: Break certification into weekly domain milestones."""
    domain_weights = profile.get("domain_weights", {})
    recommended_hours = profile.get("hours_remaining_estimate", 20)
    weeks = max(profile.get("weeks_until_target", 6), len(domain_weights))
    available_per_week = profile.get("available_hours_per_week", 6)

    # Total study hours based on remaining need and available capacity
    total_study_hours = max(
        float(recommended_hours),
        float(len(domain_weights))  # at least 1h per domain
    )
    total_study_hours = min(total_study_hours, available_per_week * weeks)
    total_study_hours = max(total_study_hours, float(len(domain_weights)))

    # Allocate hours per domain
    domain_hours = largest_remainder_allocation(domain_weights, total_study_hours)

    # Build weekly milestones — one domain per week
    milestones = []
    focus_labels = ["Foundations", "Foundations", "Practice", "Practice", "Revision", "Revision"]
    for i, (domain, hours) in enumerate(domain_hours.items()):
        focus = focus_labels[min(i, len(focus_labels) - 1)]
        milestones.append({
            "week": i + 1,
            "domains": [domain],
            "study_hours": hours,
            "focus": focus,
            "milestone_goal": f"Complete: {domain}"
        })

    # Final week: practice exam
    milestones.append({
        "week": len(milestones) + 1,
        "domains": ["Full Practice Exam"],
        "study_hours": 3,
        "focus": "Assessment",
        "milestone_goal": "Complete 2 full practice exams — target 75%+"
    })

    return milestones, domain_hours


def execute_schedule(milestones: list, work_signals: dict, available_per_week: float) -> list:
    """EXECUTOR: Map milestones onto work-aware daily schedule using Work IQ signals."""
    preferred_slot = work_signals.get("preferred_learning_slot", "Morning")
    peak_days = work_signals.get("peak_focus_days", ["Tuesday", "Wednesday", "Thursday"])
    heavy_days = work_signals.get("heavy_meeting_days", ["Monday", "Friday"])
    focus_hours_pw = work_signals.get("focus_hours_per_week", 12)

    # Capacity adjustment
    capacity_factor = min(1.0, focus_hours_pw / 15)

    # Best study days: peak days that aren't heavy meeting days
    study_days = [d for d in peak_days if d not in heavy_days] or peak_days

    schedule = []
    for milestone in milestones:
        hours_per_session = round(
            milestone["study_hours"] / max(len(study_days), 1), 1
        )
        schedule.append({
            "week": milestone["week"],
            "milestone_goal": milestone["milestone_goal"],
            "focus_type": milestone["focus"],
            "total_hours": milestone["study_hours"],
            "recommended_days": study_days,
            "hours_per_session": max(0.5, hours_per_session),
            "study_slot": preferred_slot,
            "avoid_days": heavy_days,
            "work_iq_note": (
                f"Scheduled during {preferred_slot.lower()} focus windows "
                f"on {', '.join(study_days)}. "
                f"Avoiding heavy meeting days: {', '.join(heavy_days)}."
            ),
            "capacity_note": (
                f"Capacity factor {round(capacity_factor * 100)}% based on "
                f"{focus_hours_pw}h focus time/week."
            ) if capacity_factor < 1.0 else "Full capacity available."
        })

    return schedule


def run(learner_id: str = None, profile: dict = None, curator: dict = None) -> dict:
    """
    Generate a capacity-aware study plan using Planner→Executor pattern.
    """
    if profile is None:
        profile = profiler_run(learner_id=learner_id)
    if curator is None:
        curator = curator_run(profile=profile)

    if "error" in profile:
        return profile

    work_signals_data = load_work_signals()
    work_signals = next(
        (w for w in work_signals_data if w["learner_id"] == profile["learner_id"]),
        work_signals_data[0]
    )

    milestones, domain_hours = plan_milestones(profile, curator)
    schedule = execute_schedule(
        milestones,
        work_signals,
        profile.get("available_hours_per_week", 6)
    )

    total_planned_hours = sum(m["study_hours"] for m in milestones)

    result = {
        "agent": "Study Plan Generator",
        "pattern": "Planner → Executor",
        "learner_id": profile["learner_id"],
        "learner_name": profile.get("learner_name"),
        "target_cert": profile.get("target_cert"),
        "total_planned_hours": total_planned_hours,
        "weeks_planned": len(schedule),
        "domain_hour_allocations": domain_hours,
        "preferred_study_slot": work_signals.get("preferred_learning_slot"),
        "weekly_schedule": schedule,
        "work_iq_signals_used": {
            "meeting_hours_pw": work_signals.get("meeting_hours_per_week"),
            "focus_hours_pw": work_signals.get("focus_hours_per_week"),
            "peak_days": work_signals.get("peak_focus_days"),
            "heavy_days": work_signals.get("heavy_meeting_days")
        },
        "reasoning": (
            f"Planner decomposed {profile.get('target_cert')} into "
            f"{len(milestones)} milestones using Largest Remainder domain "
            f"allocation across {total_planned_hours}h total. "
            f"Executor scheduled sessions on "
            f"{', '.join(work_signals.get('peak_focus_days', []))} "
            f"during {work_signals.get('preferred_learning_slot', 'Morning')} windows, "
            f"avoiding heavy meeting days: "
            f"{', '.join(work_signals.get('heavy_meeting_days', []))}."
        )
    }

    return result


if __name__ == "__main__":
    for lid in ["L-1001", "L-1002", "L-1003"]:
        result = run(learner_id=lid)
        print(f"\n{'='*60}")
        print(f"AGENT 3 OUTPUT — {result.get('learner_name', lid)}")
        print(f"{'='*60}")
        print(f"Pattern:    {result.get('pattern')}")
        print(f"Total Hrs:  {result.get('total_planned_hours')}")
        print(f"Weeks:      {result.get('weeks_planned')}")
        print(f"Domain Allocations: {result.get('domain_hour_allocations')}")
        print(f"Reasoning:  {result.get('reasoning')}")
        for week in result.get("weekly_schedule", [])[:3]:
            print(f"  Week {week['week']}: {week['milestone_goal']} | "
                  f"{week['total_hours']}h | {week['study_slot']} | "
                  f"{week['recommended_days']}")
