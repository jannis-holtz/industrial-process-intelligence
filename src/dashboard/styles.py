PLOTLY_TEMPLATE = "plotly_dark"

CUSTOM_CSS = """
<style>
    /* Global layout */
    .main {
        background: #070b14;
    }

    .block-container {
        max-width: none;
        width: 100%;
        padding-top: 1.25rem;
        padding-left: 1.5rem;
        padding-right: 1.5rem;
        padding-bottom: 2rem;
    }

    header[data-testid="stHeader"] {
        background: transparent;
    }

    section[data-testid="stSidebar"] {
        background: #07111f;
        border-right: 1px solid rgba(148, 163, 184, 0.18);
    }

    h1, h2, h3 {
        color: #f8fafc;
        letter-spacing: -0.035em;
    }

    h1 {
        font-size: 2.4rem;
        margin-bottom: 0.15rem;
    }

    h2 {
        font-size: 1.45rem;
        margin-top: 0.6rem;
    }

    h3 {
        font-size: 1.05rem;
    }

    p, li, span, div {
        font-family: "Inter", "Segoe UI", sans-serif;
    }

    .subtitle {
        color: #94a3b8;
        font-size: 0.9rem;
        margin-bottom: 1.1rem;
    }

    /* Header */
    .top-bar {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        gap: 1rem;
        margin-bottom: 1.1rem;
    }

    .top-actions {
        display: flex;
        justify-content: flex-end;
        gap: 0.55rem;
        align-items: center;
        flex-wrap: wrap;
        margin-top: 0.35rem;
    }

    .action-button {
        background: #0f172a;
        color: #cbd5e1;
        border: 1px solid rgba(148, 163, 184, 0.25);
        border-radius: 0.7rem;
        padding: 0.48rem 0.75rem;
        font-size: 0.76rem;
        white-space: nowrap;
    }

    .export-button {
        background: #2563eb;
        color: white;
        border: 1px solid rgba(96, 165, 250, 0.5);
        border-radius: 0.7rem;
        padding: 0.48rem 0.8rem;
        font-size: 0.76rem;
        font-weight: 700;
        white-space: nowrap;
    }

    /* Sidebar */
    .sidebar-logo {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        margin-bottom: 1.4rem;
        padding: 0.4rem 0.2rem 0.8rem 0.2rem;
    }

    .sidebar-logo-mark {
        width: 2.2rem;
        height: 2.2rem;
        background: linear-gradient(135deg, #2563eb, #14b8a6);
        border-radius: 0.65rem;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-weight: 800;
        font-size: 0.78rem;
        letter-spacing: -0.03em;
        box-shadow: 0 8px 18px rgba(37, 99, 235, 0.35);
    }

    .sidebar-title {
        color: #f8fafc;
        font-weight: 800;
        font-size: 0.9rem;
        line-height: 1.1;
    }

    .sidebar-subtitle {
        color: #64748b;
        font-size: 0.68rem;
        margin-top: 0.15rem;
    }

    .sidebar-section-label {
        color: #64748b;
        font-size: 0.68rem;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        font-weight: 700;
        margin: 0.6rem 0 0.45rem 0.2rem;
    }

    section[data-testid="stSidebar"] div[data-testid="stButton"] > button {
        width: 100%;
        justify-content: flex-start;
        border-radius: 0.85rem;
        padding: 0.72rem 0.85rem;
        margin-bottom: 0.35rem;
        font-size: 0.88rem;
        font-weight: 700;
        border: 1px solid rgba(148, 163, 184, 0.16);
        background: #0f172a;
        color: #cbd5e1;
        box-shadow: none;
        transition: all 0.15s ease-in-out;
    }

    section[data-testid="stSidebar"] div[data-testid="stButton"] > button:hover {
        background: rgba(37, 99, 235, 0.18);
        border-color: rgba(96, 165, 250, 0.38);
        color: #f8fafc;
        transform: translateX(2px);
    }

    section[data-testid="stSidebar"] div[data-testid="stButton"] > button[kind="primary"] {
        background: linear-gradient(135deg, #2563eb, #1d4ed8);
        color: white;
        border-color: rgba(96, 165, 250, 0.65);
        box-shadow: 0 8px 18px rgba(37, 99, 235, 0.32);
    }

    section[data-testid="stSidebar"] div[data-testid="stButton"] > button[kind="primary"]:hover {
        background: linear-gradient(135deg, #3b82f6, #2563eb);
        color: white;
        transform: translateX(2px);
    }

    .sidebar-status-card {
        display: flex;
        align-items: center;
        gap: 0.65rem;
        background: rgba(20, 184, 166, 0.12);
        border: 1px solid rgba(20, 184, 166, 0.32);
        border-radius: 0.9rem;
        padding: 0.85rem;
        margin-top: 0.5rem;
    }

    .status-dot {
        width: 0.65rem;
        height: 0.65rem;
        background: #22c55e;
        border-radius: 999px;
        box-shadow: 0 0 12px rgba(34, 197, 94, 0.75);
        flex-shrink: 0;
    }

    .status-title-small {
        color: #bbf7d0;
        font-size: 0.78rem;
        font-weight: 800;
    }

    .status-text-small {
        color: #94a3b8;
        font-size: 0.68rem;
        margin-top: 0.1rem;
    }

    /* Section / module cards */
    .module-shell {
        background: #0f172a;
        border: 1px solid rgba(148,163,184,0.18);
        border-radius: 1rem;
        padding: 1rem 1rem 0.8rem 1rem;
        box-shadow: 0 10px 28px rgba(0,0,0,0.22);
        margin-bottom: 1rem;
    }

    .module-header {
        margin-bottom: 0.8rem;
    }

    .module-eyebrow {
        color: #60a5fa;
        font-size: 0.72rem;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        font-weight: 700;
        margin-bottom: 0.3rem;
    }

    .module-main-title {
        color: #f8fafc;
        font-size: 1.02rem;
        font-weight: 800;
        margin-bottom: 0.2rem;
    }

    .module-main-subtitle {
        color: #94a3b8;
        font-size: 0.76rem;
        line-height: 1.4;
    }

    .subsection-divider {
        border-top: 1px solid rgba(148,163,184,0.12);
        margin: 0.8rem 0 0.9rem 0;
    }

    .hero-card {
        background: linear-gradient(135deg, rgba(30, 64, 175, 0.35), rgba(13, 148, 136, 0.28));
        padding: 1.15rem 1.35rem;
        border-radius: 1rem;
        border: 1px solid rgba(45, 212, 191, 0.28);
        box-shadow: 0 12px 34px rgba(0,0,0,0.25);
        margin-bottom: 1rem;
    }

    .hero-card h2 {
        margin: 0;
        color: #ffffff;
        font-size: 1.05rem;
    }

    .hero-card p {
        color: #cbd5e1;
        margin-top: 0.45rem;
        margin-bottom: 0;
        line-height: 1.45;
        font-size: 0.85rem;
    }

    .kpi-card {
        background: #0f172a;
        border: 1px solid rgba(148, 163, 184, 0.22);
        border-radius: 0.95rem;
        padding: 0.95rem 1rem;
        min-height: 112px;
        box-shadow: 0 8px 24px rgba(0,0,0,0.22);
    }

    .kpi-icon {
        color: #60a5fa;
        font-size: 1.15rem;
        margin-bottom: 0.25rem;
    }

    .kpi-label {
        color: #cbd5e1;
        font-size: 0.78rem;
        font-weight: 650;
        margin-bottom: 0.35rem;
    }

    .kpi-value {
        color: #f8fafc;
        font-size: 1.45rem;
        font-weight: 800;
        letter-spacing: -0.03em;
        margin-bottom: 0.25rem;
    }

    .kpi-delta-positive {
        color: #34d399;
        font-size: 0.72rem;
    }

    .kpi-delta-negative {
        color: #f87171;
        font-size: 0.72rem;
    }

    .module-card-small {
        background: #0f172a;
        border: 1px solid rgba(148, 163, 184, 0.22);
        border-radius: 0.95rem;
        padding: 0.95rem;
        min-height: 230px;
        box-shadow: 0 8px 24px rgba(0,0,0,0.22);
    }

    .module-title {
        color: #f8fafc;
        font-size: 0.9rem;
        font-weight: 800;
        margin-bottom: 0.35rem;
    }

    .module-subtitle {
        color: #94a3b8;
        font-size: 0.72rem;
        margin-bottom: 0.7rem;
    }

    .module-button {
        margin-top: 0.7rem;
        background: rgba(37, 99, 235, 0.16);
        border: 1px solid rgba(96, 165, 250, 0.32);
        color: #bfdbfe;
        border-radius: 0.65rem;
        padding: 0.45rem 0.65rem;
        font-size: 0.72rem;
        text-align: center;
    }

    .layer-card {
        background: #0f172a;
        border: 1px solid rgba(148,163,184,0.22);
        border-radius: 0.85rem;
        padding: 0.78rem 0.9rem;
        margin-bottom: 0.55rem;
        box-shadow: 0 8px 22px rgba(0,0,0,0.20);
    }

    .layer-number {
        display: inline-block;
        background: #2563eb;
        color: white;
        border-radius: 999px;
        padding: 0.1rem 0.45rem;
        font-size: 0.72rem;
        font-weight: 700;
        margin-right: 0.45rem;
    }

    .layer-title {
        color: #f8fafc;
        font-weight: 700;
        font-size: 0.84rem;
    }

    .layer-text {
        color: #94a3b8;
        margin-top: 0.25rem;
        font-size: 0.72rem;
        line-height: 1.35;
    }

    /* Status / decision blocks */
    .status-banner {
        display: grid;
        grid-template-columns: 2fr repeat(4, 1fr) 0.9fr;
        gap: 1rem;
        align-items: center;
        background: rgba(13, 148, 136, 0.13);
        border: 1px solid rgba(45, 212, 191, 0.38);
        border-radius: 0.95rem;
        padding: 1rem 1.15rem;
        margin: 1rem 0 1rem 0;
    }

    .status-title {
        color: #f8fafc;
        font-weight: 800;
        font-size: 0.95rem;
    }

    .status-text {
        color: #cbd5e1;
        font-size: 0.78rem;
        margin-top: 0.2rem;
    }

    .quality-metric-label {
        color: #94a3b8;
        font-size: 0.72rem;
    }

    .quality-metric-value {
        color: #f8fafc;
        font-weight: 800;
        font-size: 0.95rem;
        margin-top: 0.15rem;
    }

    .quality-bar {
        height: 3px;
        background: linear-gradient(90deg, #14b8a6, #38bdf8);
        border-radius: 999px;
        margin-top: 0.45rem;
    }

    .mini-button {
        background: #0f172a;
        color: #e2e8f0;
        border: 1px solid rgba(148, 163, 184, 0.32);
        border-radius: 0.65rem;
        padding: 0.55rem 0.75rem;
        text-align: center;
        font-size: 0.78rem;
    }

    .decision-box {
        background: rgba(13, 148, 136, 0.13);
        border: 1px solid rgba(45, 212, 191, 0.35);
        border-radius: 0.95rem;
        padding: 1rem 1.1rem;
        margin-bottom: 1rem;
        color: #ccfbf1;
    }

    .warning-box {
        background: rgba(245, 158, 11, 0.11);
        border: 1px solid rgba(245, 158, 11, 0.35);
        border-radius: 0.95rem;
        padding: 1rem 1.1rem;
        margin-bottom: 1rem;
        color: #fde68a;
    }

    /* Tables */
    .table-card-info {
        color: #94a3b8;
        font-size: 0.74rem;
        margin-bottom: 0.6rem;
    }

    .stDataFrame {
        border-radius: 0.95rem !important;
        overflow: hidden !important;
        border: 1px solid rgba(148,163,184,0.14);
        background: #0b1220;
    }

    .stDataFrame [data-testid="stDataFrameResizable"] {
        border-radius: 0.95rem !important;
    }

    /* Metrics fallback */
    div[data-testid="stMetric"] {
        background: #0f172a;
        border: 1px solid rgba(148,163,184,0.22);
        padding: 0.95rem;
        border-radius: 0.95rem;
        box-shadow: 0 8px 24px rgba(0,0,0,0.20);
    }

    div[data-testid="stMetricLabel"] {
        color: #94a3b8;
    }

    div[data-testid="stMetricValue"] {
        color: #f8fafc;
    }

    .module-grid-spacer {
        height: 1.1rem;
    }

    .footer-status {
        color: #94a3b8;
        font-size: 0.75rem;
        margin-top: 1.5rem;
        border-top: 1px solid rgba(148,163,184,0.15);
        padding-top: 0.8rem;
    }
</style>
"""