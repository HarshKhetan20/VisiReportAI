import streamlit as st
import random
from utils import generate_mock_audit_log

def init_session_state():
    """Initialize necessary session state variables."""
    if 'uploaded_image' not in st.session_state:
        st.session_state['uploaded_image'] = None
    if 'detections' not in st.session_state:
        st.session_state['detections'] = []
    if 'report_id' not in st.session_state:
        st.session_state['report_id'] = None
    if 'board_id' not in st.session_state:
        st.session_state['board_id'] = None
    if 'inspection_time' not in st.session_state:
        st.session_state['inspection_time'] = None
    if 'inference_complete' not in st.session_state:
        st.session_state['inference_complete'] = False
    if 'validation_actions' not in st.session_state:
        st.session_state['validation_actions'] = {}
    if 'audit_log' not in st.session_state:
        st.session_state['audit_log'] = generate_mock_audit_log()
    if 'queue_depth_history' not in st.session_state:
        st.session_state['queue_depth_history'] = [random.randint(0, 12) for _ in range(10)]
    if 'narrative_text' not in st.session_state:
        st.session_state['narrative_text'] = ""
    if 'schema_valid' not in st.session_state:
        st.session_state['schema_valid'] = False
