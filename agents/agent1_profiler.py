"""
Agent 1: Learner Profiler
-------------------------
Intake agent that analyses learner role, target certification,
current skills, and cross-references the Fabric IQ semantic model
to produce a skill gap analysis and readiness baseline.
"""

import json
import os
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"


def load_certifications():
    with open(DATA_DIR / "certifications.json") as f:
        return json.load(f)


def load_learners():
    with open(DATA_DIR / "learners.json") as f:
        return json.load(f)


def run(learner_id: str = None, learner_data: dict = None) -> dict:
    """
    Profile a learner: identify skill gaps, check prerequisites,
    compute readiness baseline against Fabric IQ semantic model.

    Args:
        learner_id: ID to look up from synthetic dataset
        learner_data: Or pass learner dict directly (for live UI input)

    Returns:
        dict with skill_gaps, missing_prereqs, readiness_baseline, recommendation
    """
    cert_data = load_certifications()

    # Resolve learner
    if learner_data is None:
        learners = load_learners()
        learner = next((l for l in learners if l["learner_id"] == learner_id), None)
        if not learner:
            return {"error": f"Learner {learner_id} not found"}
    else:
        learner = learner_data

    cert_id = learner["target_certification"]
    cert = next((c for c in cert_data["certifications"] if c["id"] == cert_id), None)

    if not cert:
        return {"error": f"Certification {cert_id} not found in semantic model"}

    # --- Skill Gap Analysis (Fabric IQ semantic layer) ---
    required_skills = set(cert["skills"])
    current_skills = set(learner.get("current_skills", []))
    skill_gaps = list(required_skills - current_skills)
    skills_covered = list(required_skills & current_skills)
    coverage_pct = round(len(skills_covered) / len(required_skills) * 100)

    # --- Prerequisite Check ---
    prerequisites = cert.get("prerequisites", [])
    missing_prereqs = []
    for prereq in prerequisites:
        has_prereq = any(
            prereq.lower() in s.lower()
            for s in current_skills
        )
        if not has_prereq:
            missing_prereqs.append(prereq)

    # --- Readiness Baseline ---
    thresholds = cert_data["readiness_thresholds"]
    practice_score = learner.get("practice_score_avg", 0)
    hours_studied = learner.get("hours_studied", 0)
    recommended_hours = cert["recommended_hours"]
    hours_remaining = max(0, recommended_hours - hours_studied)

    if (practice_score >= thresholds["GO"]["min_practice_score"] and
            hours_studied >= thresholds["GO"]["min_hours_studied"]):
        baseline_status = "STRONG"
    elif (practice_score >= thresholds["CONDITIONAL_GO"]["min_practice_score"] and
          hours_studied >= thresholds["CONDITIONAL_GO"]["min_hours_studied"]):
        baseline_status = "DEVELOPING"
    else:
        baseline_status = "EARLY"

    # --- Agent Output ---
    result = {
        "agent": "Learner Profiler",
        "learner_id": learner["learner_id"],
        "learner_name": learner.get("name", "Unknown"),
        "role": learner["role"],
        "target_cert": cert_id,
        "cert_name": cert["name"],
        "skill_coverage_pct": coverage_pct,
        "skills_covered": skills_covered,
        "skill_gaps": skill_gaps,
        "missing_prerequisites": missing_prereqs,
        "practice_score_avg": practice_score,
        "hours_studied": hours_studied,
        "hours_remaining_estimate": hours_remaining,
        "readiness_baseline": baseline_status,
        "domain_weights": cert["domain_weights"],
        "pass_threshold": cert["pass_threshold"],
        "reasoning": (
            f"{learner.get('name', learner_id)} is targeting {cert_id} ({cert['name']}) "
            f"with {coverage_pct}% skill coverage. "
            f"{'No prerequisites missing. ' if not missing_prereqs else f'Missing prerequisites: {missing_prereqs}. '}"
            f"Current practice score of {practice_score}% and {hours_studied}h studied "
            f"places this learner at '{baseline_status}' baseline. "
            f"Estimated {hours_remaining}h of study remaining to reach recommended {recommended_hours}h."
        )
    }

    return result


if __name__ == "__main__":
    for lid in ["L-1001", "L-1002", "L-1003", "L-1004", "L-1005"]:
        result = run(learner_id=lid)
        print(f"\n{'='*60}")
        print(f"AGENT 1 OUTPUT — {result.get('learner_name', lid)}")
        print(f"{'='*60}")
        print(f"Cert:         {result.get('target_cert')} — {result.get('cert_name')}")
        print(f"Skill Cover:  {result.get('skill_coverage_pct')}%")
        print(f"Skill Gaps:   {result.get('skill_gaps')}")
        print(f"Missing Prereqs: {result.get('missing_prerequisites')}")
        print(f"Baseline:     {result.get('readiness_baseline')}")
        print(f"Reasoning:    {result.get('reasoning')}")
