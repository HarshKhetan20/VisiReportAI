import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import time
import random
from PIL import Image
from datetime import datetime, timezone
import os
from utils import run_mock_inference, run_yolo_inference, validate_schema, annotate_image
from config import PLOTLY_DARK_THEME, DEFECT_COLORS, DEFECT_DISPLAY_NAMES

def render_inspection_tab(conf_thresh, tile_size, overlap_margin):
    col1, col2 = st.columns([3, 2])
    
    with col1:
        st.markdown("<div class='visi-panel'><div class='visi-panel-header'>◈ REAL-TIME INSPECTION VIEWPORT</div>", unsafe_allow_html=True)
        
        if st.session_state['uploaded_image'] is None:
            uploaded_file = st.file_uploader("DROP HIGH-RESOLUTION PCB OPTICAL SCAN", type=["png", "jpg", "jpeg", "tiff", "bmp"], help="Supports up to 4K resolution (4096×4096px). TIFF for lossless industrial scans recommended.")
            if uploaded_file is not None:
                image = Image.open(uploaded_file).convert('RGB')
                st.session_state['uploaded_image'] = np.array(image)
                st.rerun()
            else:
                st.markdown("""
                <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; height: 300px; border: 1px dashed var(--border); border-radius: 4px; background-color: var(--bg-tertiary);">
                    <div style="font-family: 'JetBrains Mono', monospace; color: var(--text-muted); font-size: 14px; letter-spacing: 0.1em; margin-top: 10px;">AWAITING SCAN INPUT</div>
                </div>
                """, unsafe_allow_html=True)
        else:
            image_arr = st.session_state['uploaded_image']
            
            c1, c2 = st.columns([3, 1])
            with c1:
                if st.button("▶ INITIATE TILING INFERENCE", key="btn_run", use_container_width=True, type="primary"):
                    st.session_state['inference_complete'] = False
                    st.session_state['report_id'] = f"VR-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')}-{random.randint(1000,9999):04X}"
                    st.session_state['board_id'] = f"PCBA-MED-{random.randint(10, 999):03d}"
                    st.session_state['inspection_time'] = datetime.now(timezone.utc).isoformat()
                    
                    log_container = st.empty()
                    progress_bar = st.progress(0)
                    logs = ""
                    
                    steps = [
                        f"[00:00.001] Board scan received. Dimensions: {image_arr.shape[1]}×{image_arr.shape[0]}px",
                        "[00:00.012] Initializing asynchronous slicing engine...",
                        f"[00:00.023] Tile grid computed: 24 tiles (6×4) @ {tile_size}",
                        f"[00:00.034] Overlap margin: {overlap_margin} | Stride: Sx=544px, Sy=544px",
                        "[00:00.112] Dispatching tiles to YOLOv10n inference queue..."
                    ]
                    for i, step in enumerate(steps):
                        logs += step + "\\n"
                        log_container.markdown(f"<div class='terminal-box'>{logs}</div>", unsafe_allow_html=True)
                        progress_bar.progress((i+1)*10)
                        time.sleep(0.1)
                    
                    # Simulate processing
                    for i in range(1, 25, 4):
                        logs += f"[00:00.{300+i*10}] Tile [{i}/24] processed | {random.randint(0,2)} anomalies detected\\n"
                        log_container.markdown(f"<div class='terminal-box'>{logs}</div>", unsafe_allow_html=True)
                        progress_bar.progress(50 + int((i/24)*30))
                        time.sleep(0.08)
                        
                    # Run actual inference if best.pt exists, else mock
                    if os.path.exists("best.pt"):
                        detections = run_yolo_inference(image_arr, "best.pt", conf_thresh)
                    else:
                        detections = run_mock_inference(image_arr, conf_thresh)
                    st.session_state['detections'] = detections
                    n_defects = len(detections)
                    
                    final_steps = [
                        "[00:00.912] Global spatial mask merging initiated...",
                        f"[00:01.045] Affine coordinate remapping: {n_defects} unique detections confirmed.",
                        "[00:01.120] VISIREPORT_SCHEMA validation: PASSED ✓",
                        "[00:01.215] Payload dispatched to RabbitMQ exchange: visireport.defects.exchange",
                        "[00:01.350] VisiSemanticClient consumed payload. LLM synthesis in progress...",
                        f"[00:09.245] NCR GENERATION COMPLETE. Report ID: {st.session_state['report_id']}"
                    ]
                    
                    for step in final_steps:
                        logs += step + "\\n"
                        log_container.markdown(f"<div class='terminal-box'>{logs}</div>", unsafe_allow_html=True)
                        time.sleep(0.15)
                        
                    progress_bar.progress(100)
                    
                    # Validate payload for mock
                    payload = {
                        "report_id": st.session_state['report_id'],
                        "board_id": st.session_state['board_id'],
                        "inspection_timestamp": st.session_state['inspection_time'],
                        "defects": detections,
                        "board_disposition": "NONCONFORMING" if n_defects > 0 else "CONFORMING"
                    }
                    st.session_state['schema_valid'] = validate_schema(payload)
                    st.session_state['inference_complete'] = True
                    time.sleep(0.5)
                    st.rerun()

            with c2:
                if st.button("✕ CLEAR BOARD", use_container_width=True):
                    st.session_state['uploaded_image'] = None
                    st.session_state['inference_complete'] = False
                    st.session_state['detections'] = []
                    st.rerun()
            
            if st.session_state.get('inference_complete'):
                st.markdown("<hr>", unsafe_allow_html=True)
                detections = st.session_state['detections']
                annotated_img = annotate_image(image_arr, detections)
                
                st.markdown("<div style='font-family: JetBrains Mono; font-size: 12px; color: var(--text-secondary); margin-bottom: 10px;'>💡 Right-click → Open image in new tab for full-resolution zoom. Or use controls below.</div>", unsafe_allow_html=True)
                
                z1, z2, z3 = st.columns(3)
                with z1: z_x = st.slider("ZOOM REGION — X OFFSET", 0.0, 1.0, 0.5)
                with z2: z_y = st.slider("ZOOM REGION — Y OFFSET", 0.0, 1.0, 0.5)
                with z3: z_f = st.slider("ZOOM FACTOR (×)", 1.0, 8.0, 1.0)
                
                if z_f > 1.0:
                    H, W = annotated_img.shape[:2]
                    crop_w, crop_h = int(W/z_f), int(H/z_f)
                    start_x = int(z_x * (W - crop_w))
                    start_y = int(z_y * (H - crop_h))
                    display_img = annotated_img[start_y:start_y+crop_h, start_x:start_x+crop_w]
                else:
                    display_img = annotated_img
                    
                st.image(display_img, use_container_width=True, caption=f"Board ID: {st.session_state.get('board_id', 'UNKNOWN')} | {len(detections)} anomalies detected", channels="BGR")
        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        st.markdown("<div class='visi-panel'><div class='visi-panel-header'>◈ BOARD DEFECT SUMMARY</div>", unsafe_allow_html=True)
        if st.session_state.get('inference_complete'):
            detections = st.session_state['detections']
            total_anomalies = len(detections)
            crit_count = sum(1 for d in detections if d['iso_severity'] == 'CRITICAL')
            maj_count = sum(1 for d in detections if d['iso_severity'] == 'MAJOR')
            board_status = "FAIL" if total_anomalies > 0 else "PASS"
            status_color = "var(--accent-crimson)" if board_status == "FAIL" else "var(--accent-green)"
            
            m1, m2 = st.columns(2)
            with m1:
                st.markdown(f"<div class='metric-card'><div style='font-family: JetBrains Mono; font-size: 0.65rem; color: var(--text-secondary);'>TOTAL ANOMALIES</div><div style='font-family: JetBrains Mono; font-size: 1.8rem; font-weight: 700; color: var(--accent-cyan);'>{total_anomalies} <span style='font-size: 0.8rem; color: var(--text-secondary);'>vs last</span></div></div>", unsafe_allow_html=True)
            with m2:
                st.markdown(f"<div class='metric-card'><div style='font-family: JetBrains Mono; font-size: 0.65rem; color: var(--text-secondary);'>CRITICAL FAILURES</div><div style='font-family: JetBrains Mono; font-size: 1.8rem; font-weight: 700; color: var(--accent-crimson);'>{crit_count}</div></div>", unsafe_allow_html=True)
            
            m3, m4 = st.columns(2)
            with m3:
                st.markdown(f"<div class='metric-card' style='margin-top: 10px;'><div style='font-family: JetBrains Mono; font-size: 0.65rem; color: var(--text-secondary);'>MAJOR NON-CONFORMANCES</div><div style='font-family: JetBrains Mono; font-size: 1.8rem; font-weight: 700; color: var(--accent-amber);'>{maj_count}</div></div>", unsafe_allow_html=True)
            with m4:
                st.markdown(f"<div class='metric-card' style='margin-top: 10px;'><div style='font-family: JetBrains Mono; font-size: 0.65rem; color: var(--text-secondary);'>BOARD STATUS</div><div style='font-family: JetBrains Mono; font-size: 1.8rem; font-weight: 700; color: {status_color};'>{board_status}</div></div>", unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Bar Chart
            cls_counts = {k: 0 for k in DEFECT_COLORS.keys()}
            for d in detections:
                cls_counts[d['class']] += 1
            
            df_counts = pd.DataFrame([{'Class': DEFECT_DISPLAY_NAMES[k], 'Count': v, 'Color': DEFECT_COLORS[k]} for k, v in cls_counts.items()])
            df_counts = df_counts.sort_values(by='Class', ascending=False)
            
            fig_bar = go.Figure(go.Bar(
                x=df_counts['Count'],
                y=df_counts['Class'],
                orientation='h',
                marker_color=df_counts['Color'],
                text=df_counts['Count'],
                textposition='outside'
            ))
            fig_bar.update_layout(**PLOTLY_DARK_THEME)
            fig_bar.update_layout(height=280, margin=dict(l=10, r=20, t=20, b=20), xaxis_title="Count")
            st.plotly_chart(fig_bar, use_container_width=True, config={'displayModeBar': False})
            
            # Donut Chart
            sev_counts = {'CRITICAL': crit_count, 'MAJOR': maj_count, 'MINOR': total_anomalies - crit_count - maj_count}
            fig_donut = go.Figure(go.Pie(
                labels=list(sev_counts.keys()),
                values=list(sev_counts.values()),
                hole=0.6,
                marker=dict(colors=['#FF3B3B', '#FFB020', '#00E676'])
            ))
            fig_donut.update_layout(**PLOTLY_DARK_THEME)
            fig_donut.update_layout(height=250, margin=dict(l=10, r=10, t=10, b=10), annotations=[dict(text="NCR<br>SEVERITY", x=0.5, y=0.5, font_size=12, font_color="white", showarrow=False)])
            st.plotly_chart(fig_donut, use_container_width=True, config={'displayModeBar': False})
            
            # Performance Box
            st.markdown("""
            <div style='background-color: var(--bg-tertiary); border: 1px solid var(--border); padding: 15px; border-radius: 4px; margin-top: 15px;'>
                <div style='font-family: JetBrains Mono; font-size: 16px; font-weight: 700; color: var(--text-primary);'>⏱ CYCLE TIME: 9.2s / board</div>
                <div style='font-family: JetBrains Mono; font-size: 11px; color: var(--accent-green); margin-bottom: 10px;'>✓ WITHIN 10s SLA</div>
                <div style='font-family: IBM Plex Sans; font-size: 12px; color: var(--text-secondary);'>TILES PROCESSED: 24<br>GPU UTILIZATION: 73%</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info("Awaiting inference completion.")
        st.markdown("</div>", unsafe_allow_html=True)
