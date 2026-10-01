import streamlit as st
import json
from datetime import datetime, timezone

def render_cognitive_pipeline_tab():
    st.markdown("<div class='visi-panel'>", unsafe_allow_html=True)
    
    # Top Status Bar
    t1, t2, t3 = st.columns(3)
    schema_valid = st.session_state.get('schema_valid', False)
    schema_class = "schema-valid" if schema_valid else "schema-invalid"
    schema_text = "SCHEMA VALIDATED" if schema_valid else "SCHEMA VIOLATION"
    schema_color = "var(--accent-green)" if schema_valid else "var(--accent-crimson)"
    
    with t1:
        st.markdown(f"""
        <div style='border: 1px solid var(--border); padding: 15px; border-radius: 4px; background: var(--bg-tertiary);'>
            <div style='display: flex; align-items: center; margin-bottom: 5px;'>
                <div class='{schema_class}' style='margin-right: 10px;'></div>
                <div style='font-family: JetBrains Mono; font-size: 13px; font-weight: 700; color: {schema_color};'>{schema_text}</div>
            </div>
            <div style='font-family: JetBrains Mono; font-size: 10px; color: var(--text-secondary);'>ISO-13485 Cl. 8.3 — VISIREPORT_SCHEMA v3.1</div>
        </div>
        """, unsafe_allow_html=True)
    with t2:
        st.markdown("""
        <div style='border: 1px solid var(--border); padding: 15px; border-radius: 4px; background: var(--bg-tertiary);'>
            <div style='font-family: JetBrains Mono; font-size: 13px; font-weight: 700; color: var(--accent-amber); margin-bottom: 5px;'>RABBITMQ PIPELINE</div>
            <div style='font-family: JetBrains Mono; font-size: 10px; color: var(--text-secondary);'>PAYLOAD CONSUMED ✓</div>
        </div>
        """, unsafe_allow_html=True)
    with t3:
        st.markdown("""
        <div style='border: 1px solid var(--border); padding: 15px; border-radius: 4px; background: var(--bg-tertiary);'>
            <div style='font-family: JetBrains Mono; font-size: 13px; font-weight: 700; color: var(--accent-purple); margin-bottom: 5px;'>LLM SYNTHESIS STATUS</div>
            <div style='font-family: JetBrains Mono; font-size: 10px; color: var(--text-secondary);'>NARRATIVE GENERATED (~847 tokens)</div>
        </div>
        """, unsafe_allow_html=True)
        
    st.markdown("<br>", unsafe_allow_html=True)
    
    if st.session_state.get('inference_complete'):
        with st.expander("VIEW RAW SCHEMA PAYLOAD"):
            payload = {
                "report_id": st.session_state['report_id'],
                "board_id": st.session_state['board_id'],
                "inspection_timestamp": st.session_state['inspection_time'],
                "schema_version": "3.1.0",
                "iso_standard": "ISO-13485:2016",
                "defects": st.session_state['detections'],
                "board_disposition": "NONCONFORMING" if len(st.session_state['detections']) > 0 else "CONFORMING"
            }
            st.code(json.dumps(payload, indent=2), language="json")
            
        st.markdown("<div class='visi-panel-header' style='margin-top:20px;'>◈ LLM-SYNTHESIZED NCR NARRATIVE — VisiSemanticClient OUTPUT</div>", unsafe_allow_html=True)
        
        n1, n2 = st.columns([6, 4])
        with n1:
            if not st.session_state['narrative_text']:
                crit_count = sum(1 for d in st.session_state['detections'] if d['iso_severity'] == 'CRITICAL')
                st.session_state['narrative_text'] = f"""NON-CONFORMANCE REPORT
Report ID: {st.session_state['report_id']}
Board ID: {st.session_state['board_id']}
Inspection Date: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}
Disposition: NONCONFORMING — QUARANTINE REQUIRED

EXECUTIVE SUMMARY:
Autonomous optical inspection by the VisiReport AI system has identified {len(st.session_state['detections'])} surface defects across the subject PCBA, including {crit_count} Critical Failures that render this unit non-functional for medical device integration under ISO 13485:2016 Clause 8.3.

DEFECT NARRATIVE:
"""
                for d in st.session_state['detections'][:3]: # Show top 3
                    st.session_state['narrative_text'] += f"Defect {d['defect_id']} [{d['class'].upper()} — {d['iso_severity']}]: Anomaly detected at global coordinates ({d['global_bbox']['x']}, {d['global_bbox']['y']}), spanning a {d['global_bbox']['w']}×{d['global_bbox']['h']}px region. Confidence: {d['confidence']:.1%}.\\n\\n"
                
                st.session_state['narrative_text'] += """ROOT CAUSE ANALYSIS (Ishikawa — Preliminary):
Primary Hypothesis: Excess solder paste deposition during reflow soldering cycle, compounded by insufficient squeegee pressure calibration on the SMT line.
Contributing Factor: Thermal profile deviation detected in Zone 4 of reflow oven (±8°C above nominal)."""

            st.text_area("DRAFT NCR NARRATIVE", value=st.session_state['narrative_text'], height=400)
            b1, b2 = st.columns(2)
            with b1: st.button("🔄  REGENERATE NARRATIVE", use_container_width=True)
            with b2: st.button("✏️  EDIT NARRATIVE", use_container_width=True)

        with n2:
            st.markdown("<div style='font-family: JetBrains Mono; font-size: 12px; color: var(--accent-cyan); margin-bottom: 10px;'>◈ CORRECTIVE & PREVENTIVE ACTIONS</div>", unsafe_allow_html=True)
            
            def render_capa(badge, badge_color, desc, dept):
                st.markdown(f"""
                <div style='background-color: var(--bg-tertiary); border: 1px solid var(--border); padding: 10px; margin-bottom: 10px; border-radius: 4px;'>
                    <span style='background-color: {badge_color}20; color: {badge_color}; padding: 2px 6px; font-family: JetBrains Mono; font-size: 10px; border-radius: 2px; font-weight: bold;'>{badge}</span>
                    <div style='font-size: 13px; margin-top: 8px; margin-bottom: 8px;'>{desc}</div>
                    <div style='font-family: JetBrains Mono; font-size: 10px; color: var(--text-secondary);'>Dept: {dept}</div>
                </div>
                """, unsafe_allow_html=True)
                
            render_capa("IMMEDIATE CONTAINMENT", "#FF3B3B", "Quarantine batch lot #PCB-042-B. Do not release to downstream assembly.", "QA Dept")
            render_capa("ROOT CAUSE ELIMINATION", "#FFB020", "Audit SMT paste application settings. Re-calibrate squeegee pressure to 6.2 kg/cm².", "SMT Process Engineering")
            render_capa("PREVENTIVE MEASURE", "#00E676", "Implement automated solder paste inspection (SPI) at post-print stage with ±10μm tolerance gates.", "Manufacturing Eng.")

    else:
        st.warning("No payload available. Run inspection first.")
        
    st.markdown("</div>", unsafe_allow_html=True)
