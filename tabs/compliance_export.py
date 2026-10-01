import streamlit as st
import pandas as pd
import time
import plotly.graph_objects as go
from datetime import datetime, timezone
from utils import generate_pdf_report
from config import PLOTLY_DARK_THEME

def render_compliance_export_tab():
    c_left, c_right = st.columns([2, 1])
    
    with c_left:
        st.markdown("<div class='visi-panel'><div class='visi-panel-header'>◈ ISO-13485 AUDIT LOG — FULL TRACEABILITY CHAIN</div>", unsafe_allow_html=True)
        
        df_audit = pd.DataFrame(st.session_state['audit_log'])
        st.dataframe(df_audit, use_container_width=True, height=250)
        
        csv = df_audit.to_csv(index=False).encode('utf-8')
        st.download_button("⬇ EXPORT AUDIT LOG (CSV)", csv, "audit_log.csv", "text/csv", use_container_width=True)
        
        st.markdown("""
        <div style='background-color: var(--bg-tertiary); padding: 10px; font-size: 11px; color: var(--text-secondary); margin-top: 10px; border-radius: 4px;'>
            <b>Note:</b> This log constitutes the traceable inspection record required under ISO 13485:2016 Clause 8.3.4 (Records of nonconforming product). Retain for minimum 15 years post-device lifetime.
        </div>
        """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown("<div class='visi-panel'><div class='visi-panel-header'>◈ PDF EXPORT ENGINE — ISO-13485 NCR GENERATION</div>", unsafe_allow_html=True)
        
        if st.session_state.get('inference_complete'):
            if st.button("📄 GENERATE & DOWNLOAD NCR PDF", use_container_width=True, type="primary"):
                pdf = generate_pdf_report(
                    report_id=st.session_state['report_id'],
                    board_id=st.session_state['board_id'],
                    date_str=datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC'),
                    disposition="NONCONFORMING" if len(st.session_state['detections']) > 0 else "CONFORMING",
                    defects=st.session_state['detections'],
                    narrative=st.session_state['narrative_text']
                )
                pdf_bytes = bytes(pdf.output(dest='S'))
                st.download_button(
                    label="⬇ SAVE PDF",
                    data=pdf_bytes,
                    file_name=f"NCR_{st.session_state['report_id']}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
        else:
            st.warning("Run inspection to generate an active report.")
        st.markdown("</div>", unsafe_allow_html=True)
        
    with c_right:
        st.markdown("<div class='visi-panel'><div class='visi-panel-header'>◈ QUEUE & THROUGHPUT MONITOR</div>", unsafe_allow_html=True)
        
        # Queue Gauge
        qd = st.session_state['queue_depth_history'][-1]
        fig_q = go.Figure(go.Indicator(
            mode="gauge+number",
            value=qd,
            title={'text': "RABBITMQ QUEUE DEPTH", 'font': {'size': 12, 'family': 'JetBrains Mono'}},
            gauge={
                'axis': {'range': [0, 50], 'tickwidth': 1, 'tickcolor': "white"},
                'bar': {'color': "rgba(0,0,0,0)"},
                'bgcolor': "var(--bg-tertiary)",
                'borderwidth': 2,
                'bordercolor': "gray",
                'steps': [
                    {'range': [0, 10], 'color': '#00E676'},
                    {'range': [10, 30], 'color': '#FFB020'},
                    {'range': [30, 50], 'color': '#FF3B3B'}],
                'threshold': {'line': {'color': "white", 'width': 4}, 'thickness': 0.75, 'value': qd}
            }
        ))
        fig_q.update_layout(**PLOTLY_DARK_THEME)
        fig_q.update_layout(height=200, margin=dict(t=30, b=10, l=10, r=10))
        st.plotly_chart(fig_q, use_container_width=True, config={'displayModeBar': False})
        
        # Cycle Time Gauge
        ct = 9.2
        fig_c = go.Figure(go.Indicator(
            mode="gauge+number",
            value=ct,
            title={'text': "CYCLE TIME (s/board)", 'font': {'size': 12, 'family': 'JetBrains Mono'}},
            gauge={
                'axis': {'range': [0, 20]},
                'bar': {'color': "rgba(0,0,0,0)"},
                'steps': [
                    {'range': [0, 10], 'color': '#00E676'},
                    {'range': [10, 15], 'color': '#FFB020'},
                    {'range': [15, 20], 'color': '#FF3B3B'}],
                'threshold': {'line': {'color': "white", 'width': 4}, 'thickness': 0.75, 'value': ct}
            }
        ))
        fig_c.update_layout(**PLOTLY_DARK_THEME)
        fig_c.update_layout(height=200, margin=dict(t=30, b=10, l=10, r=10))
        st.plotly_chart(fig_c, use_container_width=True, config={'displayModeBar': False})
        
        if st.toggle("AUTO-REFRESH MONITOR (5s)"):
            time.sleep(5)
            st.rerun()
            
        st.markdown("</div>", unsafe_allow_html=True)
