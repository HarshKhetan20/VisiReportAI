# ============================================================
# VisiReport AI — Industrial PCBA Inspection Dashboard
# Version: 2.0.0
# Authors: VisiReport AI Team | SRM Institute of Science & Technology
# Standard: ISO 13485:2016 (Cl. 8.3, Cl. 8.5.2)
# Dependencies: streamlit>=1.35.0 streamlit-option-menu opencv-python-headless Pillow numpy pandas plotly>=5.22.0 ultralytics fpdf2 pika jsonschema python-dateutil
# ============================================================

import streamlit as st
from streamlit_option_menu import option_menu
from config import CUSTOM_CSS
from state import init_session_state
from components.sidebar import render_sidebar
from tabs.inspection import render_inspection_tab
from tabs.defect_registry import render_defect_registry_tab
from tabs.cognitive_pipeline import render_cognitive_pipeline_tab
from tabs.compliance_export import render_compliance_export_tab
from tabs.system_performance import render_system_performance_tab

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# PAGE CONFIGURATION
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
st.set_page_config(
    page_title="VisiReport AI — PCBA Inspection Console",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply global CSS
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# MAIN APPLICATION
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def main():
    init_session_state()
    
    # Render Sidebar and get configuration
    conf_thresh, tile_size, overlap_margin = render_sidebar()

    # Main Navigation Menu
    selected_tab = option_menu(
        menu_title=None,
        options=["INSPECTION", "DEFECT REGISTRY", "COGNITIVE PIPELINE", "COMPLIANCE & EXPORT", "SYSTEM PERFORMANCE"],
        icons=["search", "list-check", "cpu", "file-earmark-text", "graph-up"],
        default_index=0,
        orientation="horizontal",
        styles={
            "container": {"padding": "0!important", "background-color": "var(--bg-secondary)", "border-bottom": "1px solid var(--border)", "margin-bottom": "1.5rem", "max-width": "100%"},
            "icon": {"color": "var(--accent-cyan)", "font-size": "14px"},
            "nav-link": {"font-family": "JetBrains Mono", "font-size": "11px", "text-transform": "uppercase", "letter-spacing": "0.12em", "color": "var(--text-secondary)", "padding": "15px 10px", "margin": "0"},
            "nav-link-selected": {"background-color": "transparent", "color": "var(--accent-cyan)", "border-bottom": "2px solid var(--accent-cyan)", "border-radius": "0"}
        }
    )

    # Render Selected Tab
    if selected_tab == "INSPECTION":
        render_inspection_tab(conf_thresh, tile_size, overlap_margin)
    elif selected_tab == "DEFECT REGISTRY":
        render_defect_registry_tab()
    elif selected_tab == "COGNITIVE PIPELINE":
        render_cognitive_pipeline_tab()
    elif selected_tab == "COMPLIANCE & EXPORT":
        render_compliance_export_tab()
    elif selected_tab == "SYSTEM PERFORMANCE":
        render_system_performance_tab()

if __name__ == "__main__":
    main()
