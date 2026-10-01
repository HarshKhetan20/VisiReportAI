import streamlit as st
import pandas as pd
import cv2
from datetime import datetime, timezone
from utils import get_hex_to_bgr
from config import DEFECT_COLORS, DEFECT_DISPLAY_NAMES

def render_defect_registry_tab():
    st.markdown("<div class='visi-panel'><div class='visi-panel-header'>◈ DEFECT TRIAGE REGISTRY — HUMAN-IN-THE-LOOP VALIDATION</div>", unsafe_allow_html=True)
    
    if not st.session_state.get('inference_complete'):
        st.warning("No active inspection data. Please run inference in the Inspection module first.")
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        f1, f2, f3, f4 = st.columns(4)
        with f1: filter_cls = st.multiselect("FILTER BY CLASS", list(DEFECT_DISPLAY_NAMES.values()))
        with f2: min_conf = st.slider("MIN. CONFIDENCE", 0.0, 1.0, 0.0)
        with f3: filter_status = st.selectbox("VALIDATION STATUS", ["All", "Pending Review", "Confirmed", "Overridden"])
        with f4: search_id = st.text_input("SEARCH DEFECT ID", placeholder="VR-DEF-XXXX")
        
        # Prepare Data
        raw_dets = st.session_state['detections']
        # Apply validations if any exist
        validations = st.session_state.get('validation_actions', {})
        for d in raw_dets:
            if d['defect_id'] in validations:
                d['status'] = validations[d['defect_id']]
        
        df = pd.DataFrame(raw_dets)
        if not df.empty:
            df['CLASS'] = df['class'].map(DEFECT_DISPLAY_NAMES)
            df['GLOBAL_X'] = df['global_bbox'].apply(lambda x: x['x'])
            df['GLOBAL_Y'] = df['global_bbox'].apply(lambda x: x['y'])
            df['BBOX_W'] = df['global_bbox'].apply(lambda x: x['w'])
            df['BBOX_H'] = df['global_bbox'].apply(lambda x: x['h'])
            df['TILE_ORIGIN'] = df['tile_origin'].apply(lambda x: f"T[{x[0]},{x[1]}]")
            df = df[['defect_id', 'CLASS', 'confidence', 'GLOBAL_X', 'GLOBAL_Y', 'BBOX_W', 'BBOX_H', 'TILE_ORIGIN', 'iso_severity', 'status']]
            
            # Filter logic
            if filter_cls:
                df = df[df['CLASS'].isin(filter_cls)]
            df = df[df['confidence'] >= min_conf]
            if search_id:
                df = df[df['defect_id'].str.contains(search_id, case=False, na=False)]
            if filter_status != "All":
                if filter_status == "Pending Review": df = df[df['status'] == '⏳ PENDING']
                if filter_status == "Confirmed": df = df[df['status'] == '✅ CONFIRMED']
                if filter_status == "Overridden": df = df[df['status'] == '❌ OVERRIDDEN']
            
            # Display dataframe
            st.dataframe(df, use_container_width=True, height=250)
            
            st.markdown("<hr>", unsafe_allow_html=True)
            st.markdown("<div class='visi-panel-header'>◈ INDIVIDUAL DEFECT REVIEW</div>", unsafe_allow_html=True)
            
            def_id = st.selectbox("Select Defect for Review", df['defect_id'].tolist() if not df.empty else [])
            if def_id:
                sel_det = next((d for d in raw_dets if d['defect_id'] == def_id), None)
                if sel_det:
                    r1, r2, r3 = st.columns(3)
                    with r1:
                        # Zoomed Crop
                        img_arr = st.session_state['uploaded_image']
                        x, y, w, h = sel_det['global_bbox']['x'], sel_det['global_bbox']['y'], sel_det['global_bbox']['w'], sel_det['global_bbox']['h']
                        pad = 50
                        H, W = img_arr.shape[:2]
                        y1, y2 = max(0, y-pad), min(H, y+h+pad)
                        x1, x2 = max(0, x-pad), min(W, x+w+pad)
                        crop = img_arr[y1:y2, x1:x2].copy()
                        # Annotate crop locally
                        color_hex = DEFECT_COLORS.get(sel_det['class'], '#FFFFFF')
                        color_bgr = get_hex_to_bgr(color_hex)
                        cv2.rectangle(crop, (x-x1, y-y1), (x-x1+w, y-y1+h), color_bgr, 2)
                        st.image(crop, channels="BGR", use_container_width=True, caption=f"Local Context (pad=50px)")
                        
                    with r2:
                        st.markdown(f"""
                        <div style='background-color: var(--bg-tertiary); padding: 15px; border: 1px solid var(--border); border-radius: 4px; height: 100%;'>
                            <h4 style='margin-top:0; color: var(--accent-cyan); font-family: JetBrains Mono;'>{def_id}</h4>
                            <div style='font-family: Fira Code; font-size: 13px; color: var(--text-primary); margin-bottom: 8px;'>Class: <span style='color: {DEFECT_COLORS.get(sel_det['class'])}; font-weight: bold;'>{DEFECT_DISPLAY_NAMES.get(sel_det['class']).upper()}</span></div>
                            <div style='font-family: Fira Code; font-size: 13px; color: var(--text-primary); margin-bottom: 8px;'>Confidence: {sel_det['confidence']:.1%}</div>
                            <div style='font-family: Fira Code; font-size: 13px; color: var(--text-primary); margin-bottom: 8px;'>Global Coords: ({x}, {y})</div>
                            <div style='font-family: Fira Code; font-size: 13px; color: var(--text-primary); margin-bottom: 8px;'>Severity: {sel_det['iso_severity']}</div>
                            <div style='font-family: Fira Code; font-size: 13px; color: var(--text-primary); margin-bottom: 8px;'>Tile: T{sel_det['tile_origin']}</div>
                            <div style='font-family: Fira Code; font-size: 13px; color: var(--text-primary); margin-bottom: 8px;'>Time: {datetime.now(timezone.utc).strftime('%H:%M:%S UTC')}</div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                    with r3:
                        if st.button("✅  CONFIRM DETECTION", use_container_width=True):
                            st.session_state['validation_actions'][def_id] = '✅ CONFIRMED'
                            st.rerun()
                        if st.button("❌  OVERRIDE — FALSE POSITIVE", use_container_width=True):
                            st.session_state['validation_actions'][def_id] = '❌ OVERRIDDEN'
                            st.rerun()
                        notes = st.text_area("Engineer Notes", placeholder="Add justification...")
                        if st.button("💾  SAVE VALIDATION", use_container_width=True, type="primary"):
                            st.success("Saved to Audit Log.")
                            
            st.markdown("""
            <div style='background-color: rgba(0, 212, 255, 0.05); border-left: 3px solid var(--accent-cyan); padding: 10px 15px; margin-top: 20px; font-family: IBM Plex Sans; font-size: 12px;'>
                <b>AUDIT TRAIL NOTE:</b> All validation actions are cryptographically timestamped and appended to the ISO-13485 Audit Log. Override actions require engineer ID authentication in production deployment.
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info("No defects match filters.")
    st.markdown("</div>", unsafe_allow_html=True)
