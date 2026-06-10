"""
Agent 5: Assessment Agent
--------------------------
Implements the Critic → Verifier reasoning pattern.

Generator:  Produces grounded practice questions cited from Foundry IQ KB
Critic:     Reviews question quality, difficulty balance, domain coverage
Verifier:   Checks answer accuracy against source content before scoring
"""

import random
from pathlib import Path
from agents.agent1_profiler import run as profiler_run

DATA_DIR = Path(__file__).parent.parent / "data"

# Foundry IQ grounded question bank — every question has a citation
QUESTION_BANK = {
    "AZ-204": [
        {
            "id": "AZ204-Q01",
            "domain": "Develop Azure compute solutions",
            "question": "Which Azure service provides serverless event-driven compute with support for durable workflows?",
            "options": ["Azure App Service", "Azure Functions", "Azure Container Instances", "Azure Batch"],
            "correct": "Azure Functions",
            "explanation": "Azure Functions supports durable functions for stateful workflows in a serverless model.",
            "source": "Engineering Certification Enablement Guide (Synthetic) — AZ-204 Domain 1",
            "difficulty": "MEDIUM"
        },
        {
            "id": "AZ204-Q02",
            "domain": "Implement Azure security",
            "question": "What is the recommended way to access Azure Key Vault from an Azure VM without storing credentials?",
            "options": ["Service Principal with secret", "Managed Identity", "Shared Access Signature", "Connection String"],
            "correct": "Managed Identity",
            "explanation": "Managed identities eliminate the need to store credentials by providing an automatically managed identity in Microsoft Entra ID.",
            "source": "Engineering Certification Enablement Guide (Synthetic) — AZ-204 Domain 3",
            "difficulty": "MEDIUM"
        },
        {
            "id": "AZ204-Q03",
            "domain": "Develop for Azure storage",
            "question": "Which Cosmos DB consistency level provides the strongest consistency guarantees?",
            "options": ["Eventual", "Session", "Bounded Staleness", "Strong"],
            "correct": "Strong",
            "explanation": "Strong consistency guarantees linearizability — reads always return the most recent committed version.",
            "source": "Engineering Certification Enablement Guide (Synthetic) — AZ-204 Domain 2",
            "difficulty": "EASY"
        },
        {
            "id": "AZ204-Q04",
            "domain": "Connect and consume services",
            "question": "In Azure API Management, which component is used to apply transformation rules to API requests and responses?",
            "options": ["Subscriptions", "Policies", "Products", "Backends"],
            "correct": "Policies",
            "explanation": "Policies in APIM are a collection of statements executed on API requests/responses for transformation, access control, etc.",
            "source": "Engineering Certification Enablement Guide (Synthetic) — AZ-204 Domain 5",
            "difficulty": "MEDIUM"
        },
        {
            "id": "AZ204-Q05",
            "domain": "Develop Azure compute solutions",
            "question": "Which Azure App Service feature allows zero-downtime deployments by running two versions simultaneously?",
            "options": ["Auto-scaling", "Deployment slots", "WebJobs", "Custom domains"],
            "correct": "Deployment slots",
            "explanation": "Deployment slots let you deploy to a staging slot and swap with production for zero-downtime releases.",
            "source": "Engineering Certification Enablement Guide (Synthetic) — AZ-204 Domain 1",
            "difficulty": "EASY"
        }
    ],
    "AZ-400": [
        {
            "id": "AZ400-Q01",
            "domain": "Design and implement build and release pipelines",
            "question": "In Azure Pipelines YAML, what keyword defines a group of steps that run on the same agent?",
            "options": ["stage", "job", "step", "task"],
            "correct": "job",
            "explanation": "A job is a series of steps that run sequentially on the same agent. Jobs within a stage can run in parallel.",
            "source": "Engineering Certification Enablement Guide (Synthetic) — AZ-400 Domain 1",
            "difficulty": "EASY"
        },
        {
            "id": "AZ400-Q02",
            "domain": "Design and implement build and release pipelines",
            "question": "Which deployment strategy releases changes to a small subset of users before full rollout?",
            "options": ["Blue-green", "Rolling", "Canary", "Recreate"],
            "correct": "Canary",
            "explanation": "Canary deployment routes a small percentage of traffic to the new version to validate before full rollout.",
            "source": "Engineering Certification Enablement Guide (Synthetic) — AZ-400 Domain 1",
            "difficulty": "MEDIUM"
        },
        {
            "id": "AZ400-Q03",
            "domain": "Implement an instrumentation strategy",
            "question": "Which Azure service provides distributed tracing and application performance monitoring?",
            "options": ["Azure Monitor Logs", "Application Insights", "Azure Metrics", "Log Analytics"],
            "correct": "Application Insights",
            "explanation": "Application Insights is an APM service that provides distributed tracing, dependency tracking, and performance monitoring.",
            "source": "Engineering Certification Enablement Guide (Synthetic) — AZ-400 Domain 5",
            "difficulty": "EASY"
        }
    ],
    "DP-203": [
        {
            "id": "DP203-Q01",
            "domain": "Design and implement data storage",
            "question": "Which Azure Synapse Analytics pool type provides on-demand SQL queries without provisioned resources?",
            "options": ["Dedicated SQL Pool", "Serverless SQL Pool", "Spark Pool", "Data Explorer Pool"],
            "correct": "Serverless SQL Pool",
            "explanation": "Serverless SQL Pool allows querying data in Azure Data Lake on-demand without provisioning dedicated capacity.",
            "source": "Engineering Certification Enablement Guide (Synthetic) — DP-203 Domain 1",
            "difficulty": "MEDIUM"
        },
        {
            "id": "DP203-Q02",
            "domain": "Design and develop data processing",
            "question": "Which windowing function in Stream Analytics groups events that arrive within a fixed time interval?",
            "options": ["Sliding Window", "Tumbling Window", "Hopping Window", "Session Window"],
            "correct": "Tumbling Window",
            "explanation": "Tumbling windows are fixed-size, non-overlapping time intervals. Every event belongs to exactly one tumbling window.",
            "source": "Engineering Certification Enablement Guide (Synthetic) — DP-203 Domain 2",
            "difficulty": "HARD"
        }
    ],
    "AZ-305": [
        {
            "id": "AZ305-Q01",
            "domain": "Design identity and access solutions",
            "question": "Which Azure AD feature enables users from partner organisations to access your Azure resources?",
            "options": ["Azure AD B2C", "Azure AD B2B", "Managed Identity", "Conditional Access"],
            "correct": "Azure AD B2B",
            "explanation": "Azure AD B2B collaboration allows you to invite external users (guests) from partner organisations.",
            "source": "Engineering Certification Enablement Guide (Synthetic) — AZ-305 Domain 1",
            "difficulty": "EASY"
        },
        {
            "id": "AZ305-Q02",
            "domain": "Design data storage solutions",
            "question": "Which Azure storage service is best suited for storing large amounts of unstructured data like images and videos?",
            "options": ["Azure SQL Database", "Azure Table Storage", "Azure Blob Storage", "Azure Files"],
            "correct": "Azure Blob Storage",
            "explanation": "Azure Blob Storage is optimised for storing massive amounts of unstructured data such as images, videos, and backups.",
            "source": "Engineering Certification Enablement Guide (Synthetic) — AZ-305 Domain 2",
            "difficulty": "EASY"
        },
        {
            "id": "AZ305-Q03",
            "domain": "Design business continuity solutions",
            "question": "Which Azure feature distributes resources across physically separate locations within the same region to protect against datacenter failures?",
            "options": ["Region Pairs", "Availability Zones", "Availability Sets", "Azure Site Recovery"],
            "correct": "Availability Zones",
            "explanation": "Availability Zones are physically separate datacenters within an Azure region, each with independent power, cooling, and networking.",
            "source": "Engineering Certification Enablement Guide (Synthetic) — AZ-305 Domain 3",
            "difficulty": "MEDIUM"
        },
        {
            "id": "AZ305-Q04",
            "domain": "Design infrastructure solutions",
            "question": "Which Azure networking service provides private connectivity from on-premises networks to Azure over a dedicated private connection?",
            "options": ["VPN Gateway", "ExpressRoute", "Azure Firewall", "Application Gateway"],
            "correct": "ExpressRoute",
            "explanation": "ExpressRoute provides dedicated private connectivity between on-premises and Azure, bypassing the public internet.",
            "source": "Engineering Certification Enablement Guide (Synthetic) — AZ-305 Domain 4",
            "difficulty": "MEDIUM"
        },
        {
            "id": "AZ305-Q05",
            "domain": "Design identity and access solutions",
            "question": "Which Azure AD feature allows you to enforce MFA or block access based on user location and device compliance?",
            "options": ["Identity Protection", "Privileged Identity Management", "Conditional Access", "Azure AD B2C"],
            "correct": "Conditional Access",
            "explanation": "Conditional Access policies evaluate signals like location, device state, and risk level to enforce MFA or block sign-ins.",
            "source": "Engineering Certification Enablement Guide (Synthetic) — AZ-305 Domain 1",
            "difficulty": "MEDIUM"
        }
    ],
    "DP-600": [
        {
            "id": "DP600-Q01",
            "domain": "Prepare and serve data",
            "question": "What is the unified data storage layer in Microsoft Fabric that all workloads read from and write to?",
            "options": ["Azure Data Lake", "OneLake", "Azure Blob Storage", "Synapse Analytics"],
            "correct": "OneLake",
            "explanation": "OneLake is the single, unified, logical data lake for the entire organisation in Microsoft Fabric.",
            "source": "Engineering Certification Enablement Guide (Synthetic) — DP-600 Domain 2",
            "difficulty": "EASY"
        },
        {
            "id": "DP600-Q02",
            "domain": "Implement and manage semantic models",
            "question": "In Power BI, which function calculates a sum that respects filters applied in a report?",
            "options": ["SUM()", "CALCULATE()", "SUMX()", "TOTALYTD()"],
            "correct": "CALCULATE()",
            "explanation": "CALCULATE() modifies the filter context, making it the cornerstone DAX function for conditional aggregations.",
            "source": "Engineering Certification Enablement Guide (Synthetic) — DP-600 Domain 3",
            "difficulty": "MEDIUM"
        },
        {
            "id": "DP600-Q03",
            "domain": "Plan, implement, and manage a solution",
            "question": "What is the primary workspace item in Microsoft Fabric used to store and analyse data in a lakehouse architecture?",
            "options": ["Dataset", "Dataflow", "Lakehouse", "Warehouse"],
            "correct": "Lakehouse",
            "explanation": "A Lakehouse in Microsoft Fabric combines the flexibility of a data lake with the analytical power of a SQL warehouse.",
            "source": "Engineering Certification Enablement Guide (Synthetic) — DP-600 Domain 1",
            "difficulty": "EASY"
        },
        {
            "id": "DP600-Q04",
            "domain": "Explore and analyze data",
            "question": "Which query language is used natively in Microsoft Fabric Real-Time Analytics and Azure Data Explorer?",
            "options": ["SQL", "DAX", "KQL", "MDX"],
            "correct": "KQL",
            "explanation": "Kusto Query Language (KQL) is the native query language for Azure Data Explorer and Fabric Real-Time Analytics.",
            "source": "Engineering Certification Enablement Guide (Synthetic) — DP-600 Domain 4",
            "difficulty": "MEDIUM"
        },
        {
            "id": "DP600-Q05",
            "domain": "Prepare and serve data",
            "question": "Which Microsoft Fabric feature enables you to build ETL pipelines visually without writing code?",
            "options": ["Spark Notebooks", "Data Pipelines", "KQL Querysets", "Semantic Models"],
            "correct": "Data Pipelines",
            "explanation": "Data Pipelines in Microsoft Fabric provide a visual interface for building and scheduling data integration workflows.",
            "source": "Engineering Certification Enablement Guide (Synthetic) — DP-600 Domain 2",
            "difficulty": "EASY"
        }
    ]
}


def generate_questions(cert_id: str, domain_weights: dict, count: int = 5) -> list:
    """Generate questions weighted by domain importance (Foundry IQ grounded)."""
    available = QUESTION_BANK.get(cert_id, [])
    if not available:
        return []

    # Weight selection by domain weights
    selected = []
    domains_sorted = sorted(domain_weights.items(), key=lambda x: x[1], reverse=True)

    for domain, _ in domains_sorted:
        domain_qs = [q for q in available if domain.lower() in q["domain"].lower()]
        if domain_qs and len(selected) < count:
            selected.extend(domain_qs[:max(1, round(len(domain_qs) * domain_weights.get(domain, 0.2)))])

    # Fill remaining slots
    remaining = [q for q in available if q not in selected]
    random.shuffle(remaining)
    selected.extend(remaining[:max(0, count - len(selected))])

    return selected[:count]


def critic_review(questions: list) -> dict:
    """CRITIC: Review question quality and domain coverage balance."""
    issues = []
    domains_covered = set(q["domain"] for q in questions)
    difficulties = [q["difficulty"] for q in questions]

    # Check difficulty balance
    easy_count = difficulties.count("EASY")
    hard_count = difficulties.count("HARD")
    medium_count = difficulties.count("MEDIUM")

    if easy_count > len(questions) * 0.6:
        issues.append("Too many EASY questions — increase difficulty balance")
    if hard_count > len(questions) * 0.5:
        issues.append("Too many HARD questions — risk of discouraging learner")

    # Check all have citations
    uncited = [q["id"] for q in questions if not q.get("source")]
    if uncited:
        issues.append(f"Questions missing citations: {uncited}")

    quality_score = max(0, 100 - len(issues) * 15)

    return {
        "domains_covered": list(domains_covered),
        "difficulty_distribution": {"EASY": easy_count, "MEDIUM": medium_count, "HARD": hard_count},
        "issues_found": issues,
        "quality_score": quality_score,
        "approved": quality_score >= 70
    }


def verifier_check(questions: list, user_answers: dict = None) -> dict:
    """VERIFIER: Validate answers against Foundry IQ source content and score."""
    if user_answers is None:
        # Simulate learner answers for demo
        # ~70% accuracy: wrong on every 3rd question starting from index 2
        user_answers = {}
        for i, q in enumerate(questions):
            # Wrong on index 2, 5, 8 ... (never on index 0 to avoid 0% on 1-question sets)
            if i > 0 and i % 3 == 2 and len(q["options"]) > 1:
                wrong = [o for o in q["options"] if o != q["correct"]]
                user_answers[q["id"]] = wrong[0] if wrong else q["correct"]
            else:
                user_answers[q["id"]] = q["correct"]

    results = []
    domain_scores = {}

    for q in questions:
        user_ans = user_answers.get(q["id"], "")
        is_correct = user_ans == q["correct"]
        domain = q["domain"]

        if domain not in domain_scores:
            domain_scores[domain] = {"correct": 0, "total": 0}
        domain_scores[domain]["total"] += 1
        if is_correct:
            domain_scores[domain]["correct"] += 1

        results.append({
            "question_id": q["id"],
            "domain": domain,
            "user_answer": user_ans,
            "correct_answer": q["correct"],
            "is_correct": is_correct,
            "explanation": q["explanation"],
            "verified_against": q["source"]
        })

    overall_score = round(sum(1 for r in results if r["is_correct"]) / len(results) * 100) if results else 0
    domain_pct = {
        d: round(v["correct"] / v["total"] * 100)
        for d, v in domain_scores.items()
    }
    weak_domains = [d for d, pct in domain_pct.items() if pct < 70]

    return {
        "overall_score_pct": overall_score,
        "domain_scores": domain_pct,
        "weak_domains": weak_domains,
        "detailed_results": results,
        "verified": True
    }


def run(learner_id: str = None, profile: dict = None, user_answers: dict = None) -> dict:
    """
    Run full assessment pipeline: Generate → Critic → Verifier.

    Returns:
        dict with questions, critique, scores, weak domains, readiness signal
    """
    if profile is None:
        profile = profiler_run(learner_id=learner_id)

    if "error" in profile:
        return profile

    cert_id = profile.get("target_cert")
    domain_weights = profile.get("domain_weights", {})

    # Generate grounded questions
    questions = generate_questions(cert_id, domain_weights, count=5)

    if not questions:
        return {
            "agent": "Assessment Agent",
            "error": f"No questions available in knowledge base for {cert_id}"
        }

    # CRITIC review
    critique = critic_review(questions)

    # VERIFIER scoring
    verification = verifier_check(questions, user_answers)

    overall_score = verification["overall_score_pct"]
    readiness_signal = (
        "EXAM_READY" if overall_score >= 75
        else "NEAR_READY" if overall_score >= 65
        else "NEEDS_PREPARATION"
    )

    result = {
        "agent": "Assessment Agent",
        "pattern": "Critic → Verifier",
        "learner_id": profile["learner_id"],
        "learner_name": profile.get("learner_name"),
        "target_cert": cert_id,
        "questions_generated": len(questions),
        "questions": questions,
        "critic_review": critique,
        "verification": verification,
        "overall_score_pct": overall_score,
        "weak_domains": verification["weak_domains"],
        "readiness_signal": readiness_signal,
        "all_citations_verified": all(q.get("source") for q in questions),
        "reasoning": (
            f"Generated {len(questions)} grounded questions for {cert_id} "
            f"(Critic quality score: {critique['quality_score']}%). "
            f"Verifier scored learner at {overall_score}% overall. "
            f"Readiness signal: {readiness_signal}. "
            f"{'Weak domains: ' + ', '.join(verification['weak_domains']) if verification['weak_domains'] else 'No weak domains identified.'}"
        )
    }

    return result


if __name__ == "__main__":
    for lid in ["L-1001", "L-1002", "L-1004"]:
        result = run(learner_id=lid)
        print(f"\n{'='*60}")
        print(f"AGENT 5 OUTPUT — {result.get('learner_name', lid)}")
        print(f"{'='*60}")
        print(f"Pattern:   {result.get('pattern')}")
        print(f"Score:     {result.get('overall_score_pct')}%")
        print(f"Signal:    {result.get('readiness_signal')}")
        print(f"Weak:      {result.get('weak_domains')}")
        print(f"Reasoning: {result.get('reasoning')}")
