"""
CertPathAI — Streamlit Demo UI
================================
Multi-agent certification readiness system demo.
Run with: streamlit run app.py
"""

import streamlit as st
import sys
import time
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from agents.agent1_profiler import run as run_profiler
from agents.agent2_curator import run as run_curator
from agents.agent3_planner import run as run_planner
from agents.agent4_engagement import run as run_engagement
from agents.agent5_assessment import run as run_assessment
from agents.agent6_manager import run as run_manager
from guardrails import run_guardrails, run_all_guardrails

# ── Page config ──────────────────────────────────────────────
st.set_page_config(
    page_title="CertPathAI",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Custom CSS ────────────────────────────────────────────────
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #0a0e1a 0%, #1a2a5e 100%);
        padding: 20px 30px;
        border-radius: 12px;
        margin-bottom: 24px;
        border: 1px solid #2a3a6e;
    }
    .agent-card {
        background: #0f1628;
        border: 1px solid #1e3a5e;
        border-radius: 10px;
        padding: 16px;
        margin: 8px 0;
    }
    .decision-go {
        background: #052e16;
        border: 2px solid #4aff9e;
        border-radius: 10px;
        padding: 20px;
        text-align: center;
    }
    .decision-conditional {
        background: #2a1f00;
        border: 2px solid #f59e0b;
        border-radius: 10px;
        padding: 20px;
        text-align: center;
    }
    .decision-not-yet {
        background: #2a0a0a;
        border: 2px solid #ef4444;
        border-radius: 10px;
        padding: 20px;
        text-align: center;
    }
    .iq-badge {
        display: inline-block;
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 11px;
        font-weight: 600;
        margin: 2px;
    }
    .metric-card {
        background: #0f1628;
        border: 1px solid #1e3a5e;
        border-radius: 8px;
        padding: 12px;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# ── Header ────────────────────────────────────────────────────
st.markdown("""
<div class="main-header">
    <h1 style="color: white; margin: 0; font-size: 28px;">🎯 CertPathAI</h1>
    <p style="color: #94a3b8; margin: 4px 0 0 0; font-size: 14px;">
        Multi-Agent Certification Readiness System · Microsoft Foundry · Reasoning Agents Track
    </p>
    <div style="margin-top: 10px;">
        <span style="background:#1a3a7e; color:#4a9eff; padding:3px 10px; border-radius:5px; font-size:11px; margin-right:6px;">⬡ Foundry IQ</span>
        <span style="background:#1e3a2a; color:#4aff9e; padding:3px 10px; border-radius:5px; font-size:11px; margin-right:6px;">⬡ Work IQ</span>
        <span style="background:#3a1a5e; color:#c084fc; padding:3px 10px; border-radius:5px; font-size:11px;">⬡ Fabric IQ</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Demo Mode Banner ──────────────────────────────────────────
st.markdown("""
<div style="background: linear-gradient(90deg, rgba(74,158,255,0.08) 0%, rgba(196,132,252,0.08) 100%);
     border: 1px solid rgba(74,158,255,0.25);
     border-radius: 8px; padding: 10px 18px; margin-bottom: 18px;
     display: flex; align-items: center; gap: 12px;">
  <span style="font-size: 16px;">🟢</span>
  <div style="flex: 1;">
    <span style="color: #4ade80; font-weight: 600; font-size: 13px;">DEMO MODE</span>
    <span style="color: #94a3b8; font-size: 12px; margin-left: 8px;">
      Running fully offline · All data is synthetic · No Azure credentials required · Pipeline completes in &lt; 50ms
    </span>
  </div>
  <span style="font-family: monospace; color: #64748b; font-size: 11px;">
    v1.0 · 6 agents · 17 guardrails · 33 tests
  </span>
</div>
""", unsafe_allow_html=True)

# ── Sidebar ───────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🧠 Agent Control Panel")
    st.markdown("---")

    mode = st.radio(
        "View Mode",
        ["👤 Individual Learner", "👥 Manager Dashboard"],
        index=0
    )

    if "Individual" in mode:
        st.markdown("#### Select Learner")
        learner_options = {
            "L-1001 — Alex Chen (Cloud Engineer)": "L-1001",
            "L-1002 — Jordan Smith (DevOps Engineer)": "L-1002",
            "L-1003 — Morgan Lee (Data Engineer)": "L-1003",
            "L-1004 — Riley Park (Cloud Engineer)": "L-1004",
            "L-1005 — Casey Wright (Data Engineer)": "L-1005"
        }
        selected_label = st.selectbox("Learner", list(learner_options.keys()))
        learner_id = learner_options[selected_label]

        st.markdown("#### Run Agents")
        run_all = st.button("▶️ Run Full Pipeline", type="primary", use_container_width=True)

    st.markdown("---")
    st.markdown("#### 📊 Data Sources")
    st.markdown("""
    <div style="font-size:12px; color:#64748b;">
    ⬡ <b style="color:#4a9eff">Foundry IQ</b> — Study guides KB<br>
    ⬡ <b style="color:#4aff9e">Work IQ</b> — Calendar signals<br>
    ⬡ <b style="color:#c084fc">Fabric IQ</b> — Cert semantic model<br><br>
    ⚠️ All data is <b>synthetic</b> and for demo only.
    </div>
    """, unsafe_allow_html=True)

# ── Main Content ──────────────────────────────────────────────

if "Individual" in mode:
    if run_all:
        with st.spinner("Running 6-agent reasoning pipeline..."):
            # ── Run pipeline with timing ──────────────────────────
            t0 = time.time()
            trace_log = []

            t = time.time()
            profile = run_profiler(learner_id=learner_id)
            trace_log.append({
                "agent": "Agent 1 — Learner Profiler",
                "pattern": "Fabric IQ Semantic Gap Analysis",
                "iq_layer": "Fabric IQ",
                "duration_ms": round((time.time()-t)*1000),
                "guardrail": run_guardrails("Learner Profiler", profile),
                "output": profile,
            })

            t = time.time()
            curator = run_curator(profile=profile)
            trace_log.append({
                "agent": "Agent 2 — Learning Path Curator",
                "pattern": "Foundry IQ Grounded Retrieval",
                "iq_layer": "Foundry IQ",
                "duration_ms": round((time.time()-t)*1000),
                "guardrail": run_guardrails("Learning Path Curator", curator),
                "output": curator,
            })

            t = time.time()
            planner = run_planner(profile=profile, curator=curator)
            trace_log.append({
                "agent": "Agent 3 — Study Plan Generator",
                "pattern": "Planner → Executor (Largest Remainder)",
                "iq_layer": "Work IQ",
                "duration_ms": round((time.time()-t)*1000),
                "guardrail": run_guardrails("Study Plan Generator", planner),
                "output": planner,
            })

            t = time.time()
            engagement = run_engagement(profile=profile, study_plan=planner)
            trace_log.append({
                "agent": "Agent 4 — Engagement Agent",
                "pattern": "Work IQ Rhythm Signals",
                "iq_layer": "Work IQ",
                "duration_ms": round((time.time()-t)*1000),
                "guardrail": run_guardrails("Engagement Agent", engagement),
                "output": engagement,
            })

            t = time.time()
            assessment = run_assessment(profile=profile)
            trace_log.append({
                "agent": "Agent 5 — Assessment Agent",
                "pattern": "Critic → Verifier (Grounded Questions)",
                "iq_layer": "Foundry IQ",
                "duration_ms": round((time.time()-t)*1000),
                "guardrail": run_guardrails("Assessment Agent", assessment),
                "output": assessment,
            })

            # Agent 6 — single learner decision
            from agents.agent6_manager import make_booking_decision
            t = time.time()
            decision = make_booking_decision(profile, assessment, engagement)
            team_output = run_manager()
            trace_log.append({
                "agent": "Agent 6 — Manager Insights",
                "pattern": "Threshold-Based Composite Decision",
                "iq_layer": "Fabric IQ",
                "duration_ms": round((time.time()-t)*1000),
                "guardrail": run_guardrails("Manager Insights Agent", team_output),
                "output": team_output,
            })

            total_ms = round((time.time()-t0)*1000)
            st.session_state["trace_log"] = trace_log
            st.session_state["total_ms"] = total_ms

        # ── Guardrail Summary Banner ──────────────────────────────
        all_passed = all(t["guardrail"].passed for t in trace_log)
        total_rules = sum(t["guardrail"].rules_checked for t in trace_log)
        total_violations = sum(len(t["guardrail"].violations) for t in trace_log)

        if all_passed:
            st.success(
                f"✅ **Guardrail Pipeline Passed** — "
                f"{total_rules} rules checked · 0 violations · "
                f"Pipeline completed in {st.session_state.get('total_ms', 0)}ms"
            )
        else:
            st.error(
                f"❌ **Guardrail Violations Found** — "
                f"{total_violations} violation(s) across {total_rules} rules"
            )

        # ── Agent 1: Profiler ─────────────────────────────────
        st.markdown("### Agent 1 — Learner Profiler")
        st.caption("🔧 Fabric IQ semantic model · Skill gap analysis · Prerequisite check")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Skill Coverage", f"{profile.get('skill_coverage_pct')}%")
        with col2:
            st.metric("Practice Score", f"{profile.get('practice_score_avg')}%")
        with col3:
            st.metric("Hours Studied", f"{profile.get('hours_studied')}h")
        with col4:
            st.metric("Baseline", profile.get('readiness_baseline'))

        if profile.get("skill_gaps"):
            st.warning(f"**Skill Gaps:** {', '.join(profile['skill_gaps'])}")
        if profile.get("missing_prerequisites"):
            st.error(f"**Missing Prerequisites:** {', '.join(profile['missing_prerequisites'])}")

        with st.expander("View Agent 1 Reasoning"):
            st.write(profile.get("reasoning"))

        st.divider()

        # ── Agent 2: Curator ──────────────────────────────────
        st.markdown("### Agent 2 — Learning Path Curator")
        st.caption("⬡ Foundry IQ Knowledge Base · Cited resources only · No hallucination")

        col1, col2 = st.columns(2)
        with col1:
            st.metric("Grounding Score", f"{curator.get('grounding_score_pct')}%")
        with col2:
            st.metric("Resources Found", curator.get('skill_gaps_addressed'))

        resources = curator.get("cited_resources", [])
        if resources:
            st.markdown("**📚 Cited Study Resources (Foundry IQ)**")
            for r in resources[:5]:
                grounded_icon = "✅" if r.get("grounded") else "⚠️"
                with st.expander(f"{grounded_icon} {r.get('skill', 'Unknown')} — {r.get('section', 'N/A')}"):
                    st.write(r.get("guidance", "No guidance available"))
                    if r.get("learn_url"):
                        st.markdown(f"🔗 [Microsoft Learn]({r['learn_url']})")
                    st.caption(f"Source: {r.get('cited_source', 'Not cited')}")

        st.divider()

        # ── Agent 3: Study Planner ────────────────────────────
        st.markdown("### Agent 3 — Study Plan Generator")
        st.caption("🔄 Planner → Executor Pattern · Largest Remainder Algorithm · Work IQ scheduling")

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Hours Planned", f"{planner.get('total_planned_hours')}h")
        with col2:
            st.metric("Weeks", planner.get('weeks_planned'))
        with col3:
            st.metric("Preferred Slot", planner.get('preferred_study_slot', 'N/A'))

        work_iq = planner.get("work_iq_signals_used", {})
        st.info(
            f"⬡ **Work IQ signals:** {work_iq.get('meeting_hours_pw')}h meetings/week · "
            f"{work_iq.get('focus_hours_pw')}h focus/week · "
            f"Peak days: {', '.join(work_iq.get('peak_days', []))}"
        )

        schedule = planner.get("weekly_schedule", [])
        if schedule:
            st.markdown("**📅 Weekly Schedule**")
            for week in schedule:
                col_a, col_b, col_c, col_d = st.columns([1, 3, 2, 2])
                with col_a:
                    st.write(f"**Wk {week['week']}**")
                with col_b:
                    st.write(week["milestone_goal"])
                with col_c:
                    st.write(f"⏱️ {week['total_hours']}h · {week['study_slot']}")
                with col_d:
                    st.write(f"📅 {', '.join(week.get('recommended_days', []))}")

        st.divider()

        # ── Agent 4: Engagement ───────────────────────────────
        st.markdown("### Agent 4 — Engagement Agent")
        st.caption("⬡ Work IQ rhythm · Progress monitoring · At-risk flagging")

        progress = engagement.get("progress_status", {})
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Progress", f"{progress.get('progress_pct')}%")
        with col2:
            on_track = progress.get("on_track", False)
            st.metric("Status", "✅ On Track" if on_track else "⚠️ Behind")
        with col3:
            st.metric("Score Trend", progress.get("score_trend", "N/A").title())

        reminders = engagement.get("reminders", [])
        if reminders:
            st.markdown("**🔔 Reminders**")
            for r in reminders:
                priority_color = {"HIGH": "🔴", "MEDIUM": "🟡", "LOW": "🟢"}.get(r["priority"], "⚪")
                st.write(f"{priority_color} **{r['type']}**: {r['message']}")
                st.caption(f"Work IQ: {r.get('work_iq_rationale', '')}")

        if engagement.get("escalate_to_manager"):
            st.warning("⚠️ **Escalated to Manager** — learner flagged as at-risk")

        st.divider()

        # ── Agent 5: Assessment ───────────────────────────────
        st.markdown("### Agent 5 — Assessment Agent")
        st.caption("⬡ Foundry IQ grounded questions · Critic → Verifier Pattern · All answers verified")

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Assessment Score", f"{assessment.get('overall_score_pct')}%")
        with col2:
            st.metric("Readiness Signal", assessment.get('readiness_signal', 'N/A'))
        with col3:
            critique = assessment.get("critic_review", {})
            st.metric("Critic Quality", f"{critique.get('quality_score', 0)}%")

        weak_domains = assessment.get("weak_domains", [])
        if weak_domains:
            st.warning(f"**Weak Domains:** {', '.join(weak_domains)}")

        questions = assessment.get("questions", [])
        if questions:
            st.markdown("**📝 Grounded Practice Questions (Foundry IQ)**")
            for i, q in enumerate(questions[:3]):
                with st.expander(f"Q{i+1}: {q['question'][:70]}..."):
                    for opt in q.get("options", []):
                        icon = "✅" if opt == q["correct"] else "◦"
                        st.write(f"{icon} {opt}")
                    st.success(f"✅ Answer: {q['correct']}")
                    st.write(f"💡 {q['explanation']}")
                    st.caption(f"📎 Source: {q['source']} | Difficulty: {q['difficulty']}")

        st.divider()

        # ── Agent 6: Final Decision ───────────────────────────
        st.markdown("### Agent 6 — Manager Insights · Booking Decision")
        st.caption("⬡ Fabric IQ thresholds · Composite scoring · Human confirmation required")

        decision_type = decision.get("decision", "NOT_YET")

        if decision_type == "GO":
            st.markdown("""
            <div class="decision-go">
                <h2 style="color:#4aff9e; margin:0;">✅ GO</h2>
                <p style="color:#86efac; margin:8px 0 0 0;">Ready to book exam</p>
            </div>
            """, unsafe_allow_html=True)
        elif decision_type == "CONDITIONAL_GO":
            st.markdown("""
            <div class="decision-conditional">
                <h2 style="color:#f59e0b; margin:0;">⚡ CONDITIONAL GO</h2>
                <p style="color:#fcd34d; margin:8px 0 0 0;">Address weak domains first</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="decision-not-yet">
                <h2 style="color:#ef4444; margin:0;">✗ NOT YET</h2>
                <p style="color:#fca5a5; margin:8px 0 0 0;">More preparation needed</p>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Composite Score", f"{decision.get('composite_score')}%")
        with col2:
            st.metric("Confidence", decision.get("confidence"))
        with col3:
            st.metric("Human Confirmation", "Required ✓")

        st.write(f"**Reason:** {decision.get('reason')}")
        st.write(f"**Recommended Action:** {decision.get('action')}")

        # ── Pipeline Trace & Guardrails ───────────────────────────
        st.divider()
        st.markdown("### 🔍 Reasoning Trace — Inspect Every Agent's Thinking")
        st.caption("Full auditability · 17-rule guardrail pipeline · Per-agent reasoning · Timing breakdown")

        trace_log = st.session_state.get("trace_log", [])
        total_ms = st.session_state.get("total_ms", 0)

        if trace_log:
            # Summary metrics
            col_m1, col_m2, col_m3, col_m4 = st.columns(4)
            with col_m1:
                st.metric("Pipeline Time", f"{total_ms}ms")
            with col_m2:
                st.metric("Agents", len(trace_log))
            with col_m3:
                total_rules = sum(t['guardrail'].rules_checked for t in trace_log)
                st.metric("Rules Checked", total_rules)
            with col_m4:
                total_violations = sum(len(t['guardrail'].violations) for t in trace_log)
                st.metric("Violations", total_violations)

            st.markdown("")

            for entry in trace_log:
                g = entry["guardrail"]
                status_icon = "✅" if g.passed else "❌"
                output = entry.get("output", {})
                reasoning = output.get("reasoning", "")

                with st.expander(
                    f"{status_icon} {entry['agent']} · "
                    f"{entry.get('pattern', 'Reasoning Step')} · "
                    f"{entry['duration_ms']}ms · "
                    f"{g.rules_passed}/{g.rules_checked} rules ✓"
                ):
                    # Metadata row
                    col_a, col_b, col_c, col_d = st.columns(4)
                    with col_a:
                        st.metric("IQ Layer", entry.get("iq_layer", "—"))
                    with col_b:
                        st.metric("Duration", f"{entry['duration_ms']}ms")
                    with col_c:
                        st.metric("Rules", f"{g.rules_passed}/{g.rules_checked}")
                    with col_d:
                        st.metric("Violations", len(g.violations))

                    # Reasoning field — the heart of auditability
                    if reasoning:
                        st.markdown("**🧠 Agent Reasoning:**")
                        st.info(reasoning)

                    # Key outputs by agent type
                    if "skill_gaps" in output and output["skill_gaps"]:
                        st.markdown(
                            f"**Skill Gaps Identified:** "
                            f"{', '.join(output['skill_gaps'])}"
                        )
                    if "missing_prerequisites" in output and output["missing_prerequisites"]:
                        st.markdown(
                            f"**Missing Prerequisites:** "
                            f"{', '.join(output['missing_prerequisites'])}"
                        )
                    if "grounding_score_pct" in output:
                        st.markdown(
                            f"**Grounding Score:** "
                            f"{output['grounding_score_pct']}% "
                            f"({len(output.get('cited_resources', []))} cited resources)"
                        )
                    if "domain_hour_allocations" in output:
                        allocs = output["domain_hour_allocations"]
                        if allocs:
                            st.markdown(
                                f"**Domain Hour Allocation:** "
                                + ", ".join(
                                    f"{d}: {h}h" for d, h in allocs.items()
                                )
                            )
                    if "overall_score_pct" in output:
                        st.markdown(
                            f"**Assessment Score:** "
                            f"{output['overall_score_pct']}% · "
                            f"Signal: `{output.get('readiness_signal', 'N/A')}`"
                        )
                    if "critic_review" in output:
                        cr = output["critic_review"]
                        if isinstance(cr, dict):
                            st.markdown(
                                f"**Critic Review:** Quality "
                                f"{cr.get('quality_score', 0)}% · "
                                f"{cr.get('feedback', '')}"
                            )

                    # Guardrail details
                    st.markdown("**🛡️ Guardrail Results:**")
                    if g.violations:
                        for v in g.violations:
                            st.error(f"❌ **{v['rule']}:** {v['message']}")
                    if g.warnings:
                        for w in g.warnings:
                            st.warning(f"⚠️ **{w['rule']}:** {w['message']}")
                    if not g.violations and not g.warnings:
                        st.success(
                            f"All {g.rules_checked} guardrail rules passed — "
                            "output is safe, grounded, and auditable."
                        )

    else:
        st.info("👈 Select a learner and click **▶️ Run Full Pipeline** to start the 6-agent reasoning chain.")
        st.markdown("""
        **Pipeline Flow:**
        ```
        Agent 1 (Profiler) → Agent 2 (Curator) → Agent 3 (Planner)
                                                         ↓
        Agent 6 (Decision) ← Agent 5 (Assessment) ← Agent 4 (Engagement)
        ```
        **Reasoning Patterns:**
        - Agent 3: **Planner → Executor** (Largest Remainder scheduling)
        - Agent 5: **Critic → Verifier** (grounded question quality control)
        - All agents: **Self-reflection** on low-confidence outputs
        """)


# ── Manager Dashboard ─────────────────────────────────────────
else:
    st.markdown("### 👥 Manager Dashboard — Team Certification Readiness")
    st.caption("⬡ Fabric IQ thresholds · Work IQ capacity signals · All 5 learners")

    with st.spinner("Running team-wide pipeline across all 5 learners..."):
        team_result = run_manager()

    team_summary = team_result.get("team_summary", {})

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Team Readiness", f"{team_summary.get('team_readiness_pct')}%")
    with col2:
        st.metric("✅ GO", team_summary.get("GO"))
    with col3:
        st.metric("⚡ Conditional", team_summary.get("CONDITIONAL_GO"))
    with col4:
        st.metric("✗ Not Yet", team_summary.get("NOT_YET"))

    # At risk + capacity warnings
    at_risk = team_result.get("at_risk_learners", [])
    capacity = team_result.get("capacity_constrained_learners", [])

    if at_risk:
        st.warning(f"⚠️ **At-Risk Learners:** {', '.join(at_risk)}")
    if capacity:
        st.info(f"📅 **Capacity Constrained (20+ meeting hrs/week):** {', '.join(capacity)}")

    # Manager actions
    st.markdown("**📋 Recommended Actions**")
    for action in team_result.get("manager_actions", []):
        st.write(action)

    st.divider()

    # Per-learner table
    st.markdown("**👤 Per-Learner Decisions**")
    for lr in team_result.get("learner_decisions", []):
        if "decision" not in lr:
            continue
        d = lr["decision"]
        decision_type = d.get("decision", "NOT_YET")
        color_map = {"GO": "🟢", "CONDITIONAL_GO": "🟡", "NOT_YET": "🔴"}
        icon = color_map.get(decision_type, "⚪")

        with st.expander(
            f"{icon} {lr.get('learner_name')} · {lr.get('target_cert')} · "
            f"{decision_type.replace('_', ' ')} · Score: {d.get('composite_score')}%"
        ):
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown("**Profile**")
                ps = lr.get("profile_summary", {})
                st.write(f"Skill Coverage: {ps.get('skill_coverage_pct')}%")
                st.write(f"Practice Score: {ps.get('practice_score')}%")
                st.write(f"Hours Studied: {ps.get('hours_studied')}h")
            with col2:
                st.markdown("**Assessment**")
                asm = lr.get("assessment_summary", {})
                st.write(f"Score: {asm.get('score_pct')}%")
                st.write(f"Signal: {asm.get('readiness_signal')}")
                if asm.get("weak_domains"):
                    st.write(f"Weak: {', '.join(asm['weak_domains'])}")
            with col3:
                st.markdown("**Engagement**")
                eng = lr.get("engagement_summary", {})
                st.write(f"On Track: {'✅' if eng.get('on_track') else '⚠️'}")
                st.write(f"At Risk: {'⚠️ Yes' if eng.get('at_risk') else '✓ No'}")
                st.write(f"Reminders: {eng.get('reminders_count')}")

            st.write(f"**Reason:** {d.get('reason')}")
            st.write(f"**Action:** {d.get('action')}")
            st.caption("🔒 Human confirmation required before exam booking")

    # Cert track breakdown
    st.divider()
    st.markdown("**📊 Readiness by Certification Track**")
    cert_breakdown = team_result.get("cert_track_breakdown", {})
    for cert, counts in cert_breakdown.items():
        total = sum(counts.values())
        st.write(
            f"**{cert}** — "
            f"🟢 {counts.get('GO', 0)} GO · "
            f"🟡 {counts.get('CONDITIONAL_GO', 0)} Conditional · "
            f"🔴 {counts.get('NOT_YET', 0)} Not Yet "
            f"({total} learner{'s' if total > 1 else ''})"
        )

    st.caption("⬡ Decisions use Fabric IQ semantic thresholds. ⬡ Work IQ capacity signals inform scheduling. All data is synthetic.")
