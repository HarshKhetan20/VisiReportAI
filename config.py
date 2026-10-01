# config.py
CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@300;400;500;600&family=JetBrains+Mono:wght@400;600;700&family=Fira+Code:wght@400;500&display=swap');

:root {
   --bg-primary: #0A0C0F;
   --bg-secondary: #111418;
   --bg-tertiary: #1A1F26;
   --border: #252C36;
   --accent-cyan: #00D4FF;
   --accent-amber: #FFB020;
   --accent-crimson: #FF3B3B;
   --accent-green: #00E676;
   --accent-purple: #9B6DFF;
   --text-primary: #E8EDF5;
   --text-secondary: #8896A8;
   --text-muted: #4A5568;
}

/* Streamlit overrides */
.stApp {
    background-color: var(--bg-primary);
}
.stBlock, .stMarkdown, .stText, p, span, div {
    font-family: 'IBM Plex Sans', sans-serif;
    color: var(--text-primary);
}
[data-testid="stSidebar"] {
    background-color: var(--bg-secondary) !important;
    border-right: 1px solid var(--border);
}
.stButton > button {
    background-color: transparent !important;
    border: 1px solid var(--accent-cyan) !important;
    color: var(--accent-cyan) !important;
    font-family: 'JetBrains Mono', monospace !important;
    letter-spacing: 0.08em !important;
    text-transform: uppercase !important;
    border-radius: 2px !important;
    transition: all 0.2s !important;
}
.stButton > button:hover {
    background-color: var(--accent-cyan) !important;
    color: var(--bg-primary) !important;
}
/* Primary Action Buttons Target */
button[kind="primary"] {
    background: linear-gradient(135deg, var(--accent-cyan) 0%, #0099BB 100%) !important;
    color: var(--bg-primary) !important;
    font-weight: 700 !important;
    border: none !important;
}
[data-testid="stDataFrame"] {
    background-color: var(--bg-tertiary);
    border: 1px solid var(--border);
    font-family: 'Fira Code', monospace;
    font-size: 0.8rem;
}
.stTabs [data-baseweb="tab-list"] button {
    font-family: 'JetBrains Mono', monospace;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    font-size: 0.75rem;
}
h1, h2, h3 {
    font-family: 'JetBrains Mono', monospace !important;
    font-weight: 700 !important;
    letter-spacing: -0.02em !important;
    color: var(--text-primary) !important;
}
[data-testid="stMetricLabel"] {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.65rem !important;
    text-transform: uppercase !important;
    letter-spacing: 0.15em !important;
    color: var(--text-secondary) !important;
}
[data-testid="stMetricValue"] {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 1.8rem !important;
    font-weight: 700 !important;
    color: var(--accent-cyan) !important;
}
.stProgress > div > div > div > div {
    background-color: var(--accent-cyan) !important;
}
.stSuccess {
    background-color: rgba(0,230,118,0.08) !important;
    border-left: 3px solid var(--accent-green) !important;
    color: var(--text-primary) !important;
}
.stWarning {
    background-color: rgba(255,176,32,0.08) !important;
    border-left: 3px solid var(--accent-amber) !important;
    color: var(--text-primary) !important;
}
.stError {
    background-color: rgba(255,59,59,0.08) !important;
    border-left: 3px solid var(--accent-crimson) !important;
    color: var(--text-primary) !important;
}
.stTextInput input, .stSelectbox select, .stTextArea textarea, .stNumberInput input {
    background-color: var(--bg-tertiary) !important;
    border: 1px solid var(--border) !important;
    color: var(--text-primary) !important;
    border-radius: 2px !important;
}
.streamlit-expanderHeader {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.8rem !important;
    text-transform: uppercase !important;
    color: var(--text-primary) !important;
}

/* Reusable classes */
.visi-panel {
    background-color: var(--bg-secondary);
    border: 1px solid var(--border);
    border-radius: 4px;
    padding: 1.5rem;
    margin-bottom: 1rem;
}
.visi-panel-header {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.7rem;
    text-transform: uppercase;
    letter-spacing: 0.2em;
    color: var(--accent-cyan);
    margin-bottom: 1rem;
    padding-bottom: 0.5rem;
    border-bottom: 1px solid var(--border);
}
.defect-badge {
    display: inline-block;
    padding: 2px 6px;
    border-radius: 2px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.7rem;
    font-weight: 600;
    color: #FFFFFF;
}
.schema-valid {
    display: inline-block;
    width: 8px;
    height: 8px;
    background-color: var(--accent-green);
    border-radius: 50%;
    box-shadow: 0 0 8px var(--accent-green);
    animation: pulse 2s infinite;
}
.schema-invalid {
    display: inline-block;
    width: 8px;
    height: 8px;
    background-color: var(--accent-crimson);
    border-radius: 50%;
    box-shadow: 0 0 8px var(--accent-crimson);
    animation: pulse 2s infinite;
}
@keyframes pulse {
    0% { opacity: 0.6; }
    50% { opacity: 1; }
    100% { opacity: 0.6; }
}
.metric-card {
    border: 1px solid var(--border);
    border-top: 1px solid var(--accent-cyan);
    padding: 1rem;
    background-color: var(--bg-tertiary);
}
.status-tag {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.7rem;
    padding: 2px 4px;
    border-radius: 2px;
}
.terminal-box {
    background-color: #050709;
    border: 1px solid var(--border);
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.75rem;
    color: #00FF88;
    padding: 1rem;
    height: 200px;
    overflow-y: auto;
    border-radius: 2px;
    white-space: pre-wrap;
}
.coord-text {
    font-family: 'Fira Code', monospace;
    color: var(--text-secondary);
    font-size: 0.78rem;
}
hr {
    border-color: var(--border);
}
</style>
"""

DEFECT_COLORS = {
    'open': '#2979FF',        # Open Circuit
    'short': '#FF3B3B',       # Short Circuit
    'mousebite': '#FF6EC7',   # Mousebite
    'spur': '#FFB020',        # Spur
    'copper': '#FF6D00',      # Spurious Copper
    'pin-hole': '#00E676'     # Pin-hole
}

DEFECT_DISPLAY_NAMES = {
    'open': 'Open Circuit',
    'short': 'Short Circuit',
    'mousebite': 'Mousebite',
    'spur': 'Spur',
    'copper': 'Spurious Copper',
    'pin-hole': 'Pin-hole'
}

PLOTLY_DARK_THEME = dict(
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(26,31,38,0.8)',
    font=dict(family='JetBrains Mono', color='#8896A8', size=11),
    xaxis=dict(gridcolor='#252C36', color='#8896A8', zerolinecolor='#252C36'),
    yaxis=dict(gridcolor='#252C36', color='#8896A8', zerolinecolor='#252C36'),
    margin=dict(l=40, r=20, t=40, b=40)
)

VISIREPORT_SCHEMA = {
    "type": "object",
    "required": ["report_id", "board_id", "inspection_timestamp", "defects", "board_disposition"],
    "properties": {
        "report_id": {"type": "string"},
        "board_id": {"type": "string"},
        "inspection_timestamp": {"type": "string", "format": "date-time"},
        "defects": {"type": "array"},
        "board_disposition": {"type": "string", "enum": ["CONFORMING", "NONCONFORMING"]}
    }
}
