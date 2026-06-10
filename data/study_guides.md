# Engineering Certification Enablement Guide (Synthetic — Demo Only)

> ⚠️ This document is entirely synthetic and created for demonstration purposes only.
> No real employee data, customer data, or proprietary information is included.

---

## Role-to-Certification Mapping

### Cloud Engineer
- **Primary Certification:** AZ-204 (Developing Solutions for Microsoft Azure)
- **Advanced Certification:** AZ-305 (Designing Azure Infrastructure Solutions)
- **Recommended Path:** AZ-204 → AZ-305

### DevOps Engineer
- **Primary Certification:** AZ-400 (DevOps Solutions)
- **Prerequisite Recommended:** AZ-204 or equivalent experience
- **Recommended Path:** AZ-204 → AZ-400

### Data Engineer
- **Primary Certification:** DP-203 (Data Engineering on Azure)
- **Advanced Certification:** DP-600 (Microsoft Fabric Analytics)
- **Recommended Path:** DP-203 → DP-600

---

## Recommended Study Patterns

### Daily Study Habits
- **Optimal session length:** 90 minutes per focused study block
- **Frequency:** 5 sessions per week minimum
- **Break pattern:** 25 minutes study, 5 minutes break (Pomodoro)
- **Avoid:** Studying during heavy meeting days — comprehension drops 40%

### Weekly Milestones
- Week 1–2: Conceptual foundations, Microsoft Learn modules
- Week 3–4: Hands-on labs, sandbox practice
- Week 5: Full practice exams, domain gap analysis
- Week 6: Targeted revision of weak domains only

### Practice Score Benchmarks
- Below 60%: Intensive review required — do not book exam
- 60–70%: Conditional readiness — address weak domains first
- 70–75%: Near ready — one more practice run recommended
- Above 75%: Exam ready — book within 2 weeks

---

## AZ-204 Study Guide

### Domain 1: Develop Azure Compute Solutions (25%)
Key topics:
- Azure App Service: deployment slots, scaling, custom domains
- Azure Functions: triggers, bindings, durable functions
- Azure Container Instances and Azure Container Apps
- Azure Kubernetes Service basics

Recommended resources:
- Microsoft Learn: "Implement Azure App Service web apps"
- Microsoft Learn: "Implement Azure Functions"
- Hands-on: Deploy a function app with HTTP trigger

### Domain 2: Develop for Azure Storage (15%)
Key topics:
- Azure Blob Storage: tiers, lifecycle management, SAS tokens
- Azure Cosmos DB: consistency levels, partitioning, SDK usage
- Azure Table Storage vs Cosmos DB selection criteria

### Domain 3: Implement Azure Security (20%)
Key topics:
- Microsoft Entra ID: app registrations, service principals
- Managed identities: system-assigned vs user-assigned
- Azure Key Vault: secrets, certificates, access policies
- Microsoft Graph API basics

---

## AZ-400 Study Guide

### Domain 1: Build and Release Pipelines (40%)
Key topics:
- Azure Pipelines: YAML pipelines, stages, jobs, steps
- GitHub Actions: workflows, secrets, environments
- Release strategies: blue-green, canary, ring deployment
- Artifact management: Azure Artifacts, versioning

### Domain 2: Infrastructure as Code (included in pipelines domain)
Key topics:
- Bicep and ARM templates
- Terraform on Azure basics
- Pipeline-driven IaC deployment patterns

---

## DP-203 Study Guide

### Domain 1: Design and Implement Data Storage (40%)
Key topics:
- Azure Data Lake Storage Gen2: hierarchical namespace, ACLs
- Azure Synapse Analytics: dedicated vs serverless SQL pools
- Delta Lake format: ACID transactions, time travel
- Data partitioning strategies for performance

### Domain 2: Design and Develop Data Processing (25%)
Key topics:
- Azure Data Factory: pipelines, datasets, linked services
- Apache Spark in Synapse: DataFrames, transformations
- Stream Analytics: windowing functions, reference data
- Event Hubs: partitions, consumer groups, capture

---

## Team Learning Best Practices

### Manager Guidance
- Review team readiness weekly, not monthly
- Protect focus time blocks on team calendars during cert sprints
- Celebrate CONDITIONAL GO as progress — not failure
- Run team practice sessions for shared certification tracks

### Capacity Planning
- Never assign cert sprint during high-delivery sprints
- Employees with 20+ meeting hours/week need 20% more calendar time
- Pair junior learners with recently-certified senior colleagues
- Budget: 2 hours protected learning time per working day during cert month

### Risk Signals to Watch
- Practice score declining week over week → immediate coaching
- Hours studied below 50% of target by week 3 → schedule adjustment
- Focus hours below 10/week → escalate workload concern to PM
