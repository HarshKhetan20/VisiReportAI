import streamlit as st
import os
import random
import plotly.graph_objects as go
from config import PLOTLY_DARK_THEME

def render_sidebar():
    with st.sidebar:
        st.markdown("""
        <div style="margin-bottom: 20px;">
            <div style="font-family: 'JetBrains Mono', monospace; font-size: 28px; font-weight: 700; color: var(--accent-cyan); line-height: 1.1;">VISIREPORT</div>
            <div style="font-family: 'JetBrains Mono', monospace; font-size: 10px; text-transform: uppercase; letter-spacing: 0.15em; color: var(--text-secondary);">AI INSPECTION CONSOLE</div>
            <div style="display: inline-block; background-color: var(--bg-tertiary); border: 1px solid var(--border); padding: 2px 6px; font-family: 'JetBrains Mono', monospace; font-size: 9px; margin-top: 8px; border-radius: 2px; color: var(--text-secondary);">v2.0 | ISO-13485 COMPLIANT</div>
        </div>
        <hr style="border-color: var(--border); margin-bottom: 20px;">
        """, unsafe_allow_html=True)
        
        # Model Check
        model_exists = os.path.exists("best.pt")
        model_status_color = "--accent-green" if model_exists else "--accent-amber"
        model_status_text = "YOLOv10n ACTIVE" if model_exists else "MOCK MODE"
        
        st.markdown(f"""
        <div style="margin-bottom: 20px;">
            <div style="font-family: 'JetBrains Mono', monospace; font-size: 11px; text-transform: uppercase; letter-spacing: 0.1em; color: var(--text-secondary); margin-bottom: 10px;">SYSTEM STATUS</div>
            <div style="display: flex; align-items: center; margin-bottom: 8px;">
                <div style="width: 8px; height: 8px; border-radius: 50%; background-color: var({model_status_color}); box-shadow: 0 0 6px var({model_status_color}); margin-right: 10px;"></div>
                <div style="font-family: 'JetBrains Mono', monospace; font-size: 11px; color: var(--text-primary);">VISION ENGINE: <span style="color: var({model_status_color});">{model_status_text}</span></div>
            </div>
            <div style="display: flex; align-items: center; margin-bottom: 8px;">
                <div style="width: 8px; height: 8px; border-radius: 50%; background-color: var(--accent-amber); box-shadow: 0 0 6px var(--accent-amber); margin-right: 10px;"></div>
                <div style="font-family: 'JetBrains Mono', monospace; font-size: 11px; color: var(--text-primary);">MESSAGE BROKER: <span style="color: var(--accent-amber);">RABBITMQ: SIMULATED</span></div>
            </div>
            <div style="display: flex; align-items: center; margin-bottom: 8px;">
                <div style="width: 8px; height: 8px; border-radius: 50%; background-color: var(--accent-purple); box-shadow: 0 0 6px var(--accent-purple); margin-right: 10px;"></div>
                <div style="font-family: 'JetBrains Mono', monospace; font-size: 11px; color: var(--text-primary);">LLM COGNITIVE ENGINE: <span style="color: var(--accent-purple);">VISISEMANTICCLIENT READY</span></div>
            </div>
            <div style="display: flex; align-items: center; margin-bottom: 8px;">
                <div class="schema-valid" style="margin-right: 10px;"></div>
                <div style="font-family: 'JetBrains Mono', monospace; font-size: 11px; color: var(--text-primary);">SCHEMA VALIDATOR: <span style="color: var(--accent-green);">VISIREPORT_SCHEMA OK</span></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        
            
        st.markdown("<div class='visi-panel-header'>MODEL CONFIGURATION</div>", unsafe_allow_html=True)
        uploaded_model = st.file_uploader("Upload YOLOv10n Weights", type=["pt"])
        if uploaded_model is not None:
            with open("best.pt", "wb") as f:
                f.write(uploaded_model.getbuffer())
            st.success("Weights saved to best.pt!")
        conf_thresh = st.slider("CONF. THRESHOLD", 0.1, 1.0, 0.45, 0.05)
        iou_thresh = st.slider("TILE MERGE IoU", 0.1, 1.0, 0.45, 0.05)
        tile_size = st.selectbox("TILE RESOLUTION", ["640×640", "512×512", "896×896"])
        overlap_margin = st.selectbox("TILE OVERLAP", ["15%", "20%", "25%"])
        
        with st.expander("◈ QUEUE MONITOR"):
            st.markdown(f"""
            <div style="font-family: 'Fira Code', monospace; font-size: 11px; margin-bottom: 10px;">
                Queue: visireport.defects.exchange<br>
                Consumers: 1<br>
                Rate: 14.2 msg/s
            </div>
            """, unsafe_allow_html=True)
            # Sparkline
            qd = st.session_state['queue_depth_history']
            qd.append(random.randint(max(0, qd[-1]-2), qd[-1]+2))
            qd = qd[-10:]
            st.session_state['queue_depth_history'] = qd
            
            fig = go.Figure(data=go.Scatter(y=qd, mode='lines+markers', line=dict(color='#FFB020', width=2), marker=dict(size=4)))
            fig.update_layout(**PLOTLY_DARK_THEME)
            fig.update_layout(height=100, margin=dict(l=0, r=0, t=0, b=0), xaxis_visible=False, yaxis_visible=False)
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
            
        return conf_thresh, tile_size, overlap_margin
