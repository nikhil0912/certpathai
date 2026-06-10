"""
Agent 2: Learning Path Curator
--------------------------------
Grounded knowledge retrieval agent. Uses Foundry IQ knowledge base
(study_guides.md + certification docs) to return cited study resources
mapped to identified skill gaps. Refuses to recommend uncited content.
"""

from pathlib import Path
from agents.agent1_profiler import run as profiler_run

DATA_DIR = Path(__file__).parent.parent / "data"

# Foundry IQ Knowledge Base (simulated — in production this hits Azure AI Search)
KNOWLEDGE_BASE = {
    "Azure App Service": {
        "source": "Engineering Certification Enablement Guide (Synthetic)",
        "section": "AZ-204 Domain 1: Develop Azure Compute Solutions",
        "content": "Azure App Service: deployment slots, scaling, custom domains. Recommended: Microsoft Learn 'Implement Azure App Service web apps'.",
        "url": "https://learn.microsoft.com/training/paths/create-azure-app-service-web-apps/"
    },
    "Azure Functions": {
        "source": "Engineering Certification Enablement Guide (Synthetic)",
        "section": "AZ-204 Domain 1: Develop Azure Compute Solutions",
        "content": "Azure Functions: triggers, bindings, durable functions. Recommended: Microsoft Learn 'Implement Azure Functions'.",
        "url": "https://learn.microsoft.com/training/paths/implement-azure-functions/"
    },
    "Blob Storage": {
        "source": "Engineering Certification Enablement Guide (Synthetic)",
        "section": "AZ-204 Domain 2: Develop for Azure Storage",
        "content": "Azure Blob Storage: tiers, lifecycle management, SAS tokens.",
        "url": "https://learn.microsoft.com/training/modules/store-app-data-with-azure-blob-storage/"
    },
    "Cosmos DB": {
        "source": "Engineering Certification Enablement Guide (Synthetic)",
        "section": "AZ-204 Domain 2: Develop for Azure Storage",
        "content": "Azure Cosmos DB: consistency levels, partitioning, SDK usage.",
        "url": "https://learn.microsoft.com/training/paths/work-with-nosql-data-in-azure-cosmos-db/"
    },
    "API Management": {
        "source": "Engineering Certification Enablement Guide (Synthetic)",
        "section": "AZ-204 Domain 5: Connect and Consume Services",
        "content": "API Management: policies, versioning, developer portal.",
        "url": "https://learn.microsoft.com/training/modules/publish-manage-apis-with-azure-api-management/"
    },
    "Azure AD Authentication": {
        "source": "Engineering Certification Enablement Guide (Synthetic)",
        "section": "AZ-204 Domain 3: Implement Azure Security",
        "content": "Microsoft Entra ID: app registrations, service principals, managed identities, Key Vault.",
        "url": "https://learn.microsoft.com/training/paths/implement-applications-azure-ad/"
    },
    "CI/CD": {
        "source": "Engineering Certification Enablement Guide (Synthetic)",
        "section": "AZ-400 Domain 1: Build and Release Pipelines",
        "content": "Azure Pipelines: YAML pipelines, stages, jobs, steps. Release strategies: blue-green, canary, ring.",
        "url": "https://learn.microsoft.com/training/paths/build-applications-with-azure-devops/"
    },
    "GitHub Actions": {
        "source": "Engineering Certification Enablement Guide (Synthetic)",
        "section": "AZ-400 Domain 1: Build and Release Pipelines",
        "content": "GitHub Actions: workflows, secrets, environments, reusable workflows.",
        "url": "https://learn.microsoft.com/training/paths/automate-workflow-github-actions/"
    },
    "Azure Data Factory": {
        "source": "Engineering Certification Enablement Guide (Synthetic)",
        "section": "DP-203 Domain 2: Design and Develop Data Processing",
        "content": "Azure Data Factory: pipelines, datasets, linked services, triggers.",
        "url": "https://learn.microsoft.com/training/paths/data-integration-scale-azure-data-factory/"
    },
    "Apache Spark": {
        "source": "Engineering Certification Enablement Guide (Synthetic)",
        "section": "DP-203 Domain 2: Design and Develop Data Processing",
        "content": "Apache Spark in Synapse: DataFrames, transformations, Spark SQL.",
        "url": "https://learn.microsoft.com/training/paths/perform-data-engineering-with-azure-synapse-apache-spark-pools/"
    },
    "Azure Synapse Analytics": {
        "source": "Engineering Certification Enablement Guide (Synthetic)",
        "section": "DP-203 Domain 1: Design and Implement Data Storage",
        "content": "Azure Synapse: dedicated vs serverless SQL pools, Delta Lake, partitioning strategies.",
        "url": "https://learn.microsoft.com/training/paths/realize-integrated-analytical-solutions-with-azure-synapse-analytics/"
    },
    "Stream Analytics": {
        "source": "Engineering Certification Enablement Guide (Synthetic)",
        "section": "DP-203 Domain 2: Design and Develop Data Processing",
        "content": "Stream Analytics: windowing functions, reference data, Event Hubs integration.",
        "url": "https://learn.microsoft.com/training/paths/implement-data-streaming-with-azure-stream-analytics/"
    },
    "Power BI": {
        "source": "Engineering Certification Enablement Guide (Synthetic)",
        "section": "DP-600 Domain 3: Implement and Manage Semantic Models",
        "content": "Power BI: DAX, semantic models, report design, dataset modes.",
        "url": "https://learn.microsoft.com/training/paths/model-data-power-bi/"
    },
    "Microsoft Fabric": {
        "source": "Engineering Certification Enablement Guide (Synthetic)",
        "section": "DP-600 Domain 1: Plan, Implement and Manage a Solution",
        "content": "Microsoft Fabric: OneLake, Lakehouse, data pipelines, workspaces.",
        "url": "https://learn.microsoft.com/training/paths/get-started-fabric/"
    },
    "Azure Networking": {
        "source": "Engineering Certification Enablement Guide (Synthetic)",
        "section": "AZ-305 Domain 4: Design Infrastructure Solutions",
        "content": "Azure VNets, NSGs, Application Gateway, ExpressRoute, Private Endpoints.",
        "url": "https://learn.microsoft.com/training/paths/design-implement-microsoft-azure-networking-solutions-az-700/"
    },
    "High Availability": {
        "source": "Engineering Certification Enablement Guide (Synthetic)",
        "section": "AZ-305 Domain 3: Design Business Continuity Solutions",
        "content": "Availability zones, availability sets, load balancing, Traffic Manager, backup strategies.",
        "url": "https://learn.microsoft.com/training/modules/design-solution-for-backup-disaster-recovery/"
    }
}

GENERAL_STUDY_TIPS = {
    "source": "Engineering Certification Enablement Guide (Synthetic)",
    "section": "Recommended Study Patterns",
    "content": (
        "Optimal session: 90 mins focused study. 5 sessions/week minimum. "
        "Week 1-2: Conceptual foundations. Week 3-4: Hands-on labs. "
        "Week 5: Full practice exams. Week 6: Targeted revision of weak domains."
    )
}


def retrieve_from_knowledge_base(skill_gaps: list) -> list:
    """Simulate Foundry IQ knowledge base retrieval with citations."""
    resources = []
    for gap in skill_gaps:
        # Exact match first
        if gap in KNOWLEDGE_BASE:
            entry = KNOWLEDGE_BASE[gap]
            resources.append({
                "skill": gap,
                "cited_source": entry["source"],
                "section": entry["section"],
                "guidance": entry["content"],
                "learn_url": entry["url"],
                "grounded": True
            })
        else:
            # Partial match
            matched = False
            for kb_key, entry in KNOWLEDGE_BASE.items():
                if kb_key.lower() in gap.lower() or gap.lower() in kb_key.lower():
                    resources.append({
                        "skill": gap,
                        "cited_source": entry["source"],
                        "section": entry["section"],
                        "guidance": entry["content"],
                        "learn_url": entry["url"],
                        "grounded": True
                    })
                    matched = True
                    break
            if not matched:
                # Foundry IQ returns no result — agent refuses to hallucinate
                resources.append({
                    "skill": gap,
                    "cited_source": None,
                    "guidance": "No grounded resource found in knowledge base for this skill. Manual curation recommended.",
                    "grounded": False
                })
    return resources


def run(learner_id: str = None, profile: dict = None) -> dict:
    """
    Curate a grounded learning path for a learner based on their skill gaps.
    All recommendations are cited from the Foundry IQ knowledge base.

    Args:
        learner_id: Learner ID to profile first
        profile: Or pass Agent 1 output directly

    Returns:
        dict with cited_resources, coverage, grounding_score
    """
    if profile is None:
        profile = profiler_run(learner_id=learner_id)

    if "error" in profile:
        return profile

    skill_gaps = profile.get("skill_gaps", [])
    cert_id = profile.get("target_cert")

    # Retrieve grounded resources from Foundry IQ
    cited_resources = retrieve_from_knowledge_base(skill_gaps)

    # General study pattern (always appended, cited)
    grounded_count = sum(1 for r in cited_resources if r["grounded"])
    total_count = len(cited_resources)
    grounding_score = round(grounded_count / total_count * 100) if total_count > 0 else 100

    # Domain priority (from Fabric IQ semantic weights)
    domain_weights = profile.get("domain_weights", {})
    priority_domains = sorted(domain_weights.items(), key=lambda x: x[1], reverse=True)

    result = {
        "agent": "Learning Path Curator",
        "learner_id": profile["learner_id"],
        "learner_name": profile.get("learner_name"),
        "target_cert": cert_id,
        "skill_gaps_addressed": len(skill_gaps),
        "grounding_score_pct": grounding_score,
        "cited_resources": cited_resources,
        "general_study_guidance": GENERAL_STUDY_TIPS,
        "priority_domains": [
            {"domain": d, "weight_pct": round(w * 100)} for d, w in priority_domains
        ],
        "reasoning": (
            f"Retrieved {grounded_count}/{total_count} resources from Foundry IQ knowledge base "
            f"(grounding score: {grounding_score}%). "
            f"All cited resources reference the Engineering Certification Enablement Guide (Synthetic). "
            f"Top priority domain: '{priority_domains[0][0]}' at {round(priority_domains[0][1]*100)}% exam weight."
        )
    }

    return result


if __name__ == "__main__":
    for lid in ["L-1001", "L-1003"]:
        result = run(learner_id=lid)
        print(f"\n{'='*60}")
        print(f"AGENT 2 OUTPUT — {result.get('learner_name', lid)}")
        print(f"{'='*60}")
        print(f"Grounding Score: {result.get('grounding_score_pct')}%")
        print(f"Resources Found: {result.get('skill_gaps_addressed')}")
        print(f"Reasoning: {result.get('reasoning')}")
        for r in result.get("cited_resources", [])[:3]:
            print(f"  → [{r['skill']}] {r.get('section', 'N/A')} | Grounded: {r['grounded']}")
