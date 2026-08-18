import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import io
import os
from cleaner import clean_data
from reporter import detect_anomalies, generate_summary_report, export_to_excel

# 1. Page Configuration
st.set_page_config(
    page_title="DataPulse Dashboard",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# 2. Theme Toggle Pattern
if "theme" not in st.session_state:
    st.session_state.theme = "light"  # Default to Light Mode

def toggle_theme():
    st.session_state.theme = "dark" if st.session_state.theme == "light" else "light"

IS_DARK = st.session_state.theme == "dark"

# Define CSS custom properties
bg = "#09090b" if IS_DARK else "#ffffff"
bg_subtle = "#0c0c0f" if IS_DARK else "#f9fafb"
card = "#0c0c0f" if IS_DARK else "#ffffff"
card_hover = "#131316" if IS_DARK else "#f4f4f5"
border = "#1e1e24" if IS_DARK else "#e4e4e7"
border_subtle = "#16161a" if IS_DARK else "#f0f0f2"
text = "#fafafa" if IS_DARK else "#09090b"
text_muted = "#a1a1aa" if IS_DARK else "#71717a"
text_dim = "#71717a" if IS_DARK else "#a1a1aa"
accent = "#2563eb"
green = "#22c55e" if IS_DARK else "#16a34a"
green_muted = "rgba(34,197,94,0.12)" if IS_DARK else "rgba(22,163,74,0.08)"
red = "#ef4444" if IS_DARK else "#dc2626"
red_muted = "rgba(239,68,68,0.12)" if IS_DARK else "rgba(220,38,38,0.08)"
amber = "#f59e0b" if IS_DARK else "#d97706"
amber_muted = "rgba(245,158,11,0.12)" if IS_DARK else "rgba(217,119,6,0.08)"
shadow = "none" if IS_DARK else "0 1px 3px rgba(0,0,0,0.04), 0 1px 2px rgba(0,0,0,0.03)"

css_styles = f"""
<style>
    :root {{
        --bg: {bg};
        --bg-subtle: {bg_subtle};
        --card: {card};
        --card-hover: {card_hover};
        --border: {border};
        --border-subtle: {border_subtle};
        --text: {text};
        --text-muted: {text_muted};
        --text-dim: {text_dim};
        --accent: {accent};
        --green: {green};
        --green-muted: {green_muted};
        --red: {red};
        --red-muted: {red_muted};
        --amber: {amber};
        --amber-muted: {amber_muted};
        --shadow: {shadow};
        --radius: 10px;
    }}
    
    /* Hide Streamlit chrome */
    header[data-testid="stHeader"], #MainMenu, footer, [data-testid="stToolbar"],
    [data-testid="stDecoration"], [data-testid="stStatusWidget"], .stDeployButton,
    div[data-testid="stSidebarCollapsedControl"] {{
        display: none !important;
    }}
    
    /* Global App Styling */
    html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"], .main, .block-container, section[data-testid="stMain"] {{
        background-color: var(--bg) !important;
        color: var(--text) !important;
        font-family: 'DM Sans', -apple-system, sans-serif !important;
    }}
    .block-container {{
        padding: 2rem 2.5rem 3rem !important;
        max-width: 1360px !important;
    }}
    
    /* Force all text/labels to use our color variable to fix Dark Mode visibility */
    p, span, label, h1, h2, h3, h4, h5, h6, 
    [data-testid="stMarkdownContainer"] p, 
    [data-testid="stWidgetLabel"] p, 
    div[class*="stMarkdown"] p,
    div[data-testid="stFileUploaderDropzone"] span,
    button[data-baseweb="tab"] span {{
        color: var(--text) !important;
    }}
    
    /* Small help text/file requirements text */
    small, div[data-testid="stCaptionContainer"] {{
        color: var(--text-muted) !important;
    }}
    
    /* Brand Header styling */
    .brand {{
        display: flex;
        flex-direction: column;
        margin-bottom: 1.5rem;
    }}
    .brand-name {{
        font-size: 1.8rem;
        font-weight: 800;
        letter-spacing: -0.04em;
        color: var(--text);
    }}
    .brand-sub {{
        font-size: 0.85rem;
        color: var(--text-muted);
    }}
    
    /* KPI Card styling */
    .metric-card {{
        background: var(--card);
        border: 1px solid var(--border);
        border-radius: var(--radius);
        padding: 1.25rem 1.4rem;
        box-shadow: var(--shadow);
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        min-height: 100px;
    }}
    .metric-label {{
        font-size: 0.78rem;
        color: var(--text-muted) !important;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }}
    .metric-value {{
        font-size: 1.75rem;
        font-weight: 700;
        color: var(--text) !important;
        letter-spacing: -0.03em;
        margin-top: 0.3rem;
    }}
    .metric-delta {{
        font-size: 0.75rem;
        font-weight: 500;
        margin-top: 0.4rem;
        padding: 2px 8px;
        border-radius: 6px;
        display: inline-flex;
        align-items: center;
        gap: 3px;
        align-self: flex-start;
    }}
    .delta-up {{ color: var(--green) !important; background: var(--green-muted); }}
    .delta-down {{ color: var(--red) !important; background: var(--red-muted); }}
    .delta-warn {{ color: var(--amber) !important; background: var(--amber-muted); }}
    
    /* Chart Wrap styling */
    .chart-wrap {{
        background: var(--card);
        border: 1px solid var(--border);
        border-radius: var(--radius);
        padding: 1.2rem;
        box-shadow: var(--shadow);
        margin-bottom: 1.25rem;
    }}
    .chart-title {{
        font-size: 0.88rem;
        font-weight: 600;
        color: var(--text) !important;
    }}
    .chart-subtitle {{
        font-size: 0.75rem;
        color: var(--text-dim) !important;
        margin-bottom: 0.8rem;
    }}
    
    /* Data Table (HTML) styling */
    .table-container {{
        overflow-x: auto;
        border: 1px solid var(--border);
        border-radius: var(--radius);
        background: var(--card);
        padding: 0.5rem;
        margin-bottom: 1.5rem;
    }}
    .data-table {{
        width: 100%;
        border-collapse: separate;
        border-spacing: 0;
        font-size: 0.8rem;
    }}
    .data-table th {{
        text-align: left;
        padding: 0.6rem 0.8rem;
        color: var(--text-muted) !important;
        font-weight: 500;
        font-size: 0.72rem;
        text-transform: uppercase;
        letter-spacing: 0.04em;
        border-bottom: 1px solid var(--border);
    }}
    .data-table td {{
        padding: 0.65rem 0.8rem;
        color: var(--text) !important;
        border-bottom: 1px solid var(--border-subtle);
    }}
    .data-table tr:last-child td {{
        border-bottom: none;
    }}
    
    /* Badges */
    .badge {{
        display: inline-block;
        padding: 2px 9px;
        border-radius: 6px;
        font-size: 0.72rem;
        font-weight: 500;
    }}
    .badge-green {{ color: var(--green) !important; background: var(--green-muted); }}
    .badge-red {{ color: var(--red) !important; background: var(--red-muted); }}
    .badge-amber {{ color: var(--amber) !important; background: var(--amber-muted); }}
    .badge-blue {{ color: var(--accent) !important; background: rgba(37,99,235,0.1); }}
    
    /* Tabs (pill-style) styling */
    button[data-baseweb="tab"] {{
        background: transparent !important;
        color: var(--text-muted) !important;
        font-size: 0.835rem !important;
        font-weight: 500 !important;
        padding: 0.55rem 1rem !important;
        border: 1px solid transparent !important;
        border-radius: 7px !important;
    }}
    button[data-baseweb="tab"][aria-selected="true"] {{
        color: var(--text) !important;
        background: var(--card) !important;
        border-color: var(--border) !important;
    }}
    [data-baseweb="tab-highlight"], [data-baseweb="tab-border"] {{
        display: none !important;
    }}
    [data-baseweb="tab-list"] {{
        gap: 4px !important;
        background: var(--bg-subtle) !important;
        border: 1px solid var(--border) !important;
        border-radius: 10px !important;
        padding: 3px;
        margin-bottom: 1.5rem;
    }}
    
    [data-testid="stHorizontalBlock"] {{ gap: 1.25rem !important; }}
</style>
"""
st.markdown(css_styles, unsafe_allow_html=True)

# 3. Define UI Helpers
def metric_card(label, value, delta=None, delta_type="up"):
    cls = f"delta-{delta_type}"
    arrow = "↑" if delta_type == "up" else ("↓" if delta_type == "down" else "→")
    delta_html = f'<div class="metric-delta {cls}">{arrow} {delta}</div>' if delta else ""
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">{label}</div>
        <div class="metric-value">{value}</div>
        {delta_html}
    </div>
    """, unsafe_allow_html=True)

def render_html_table(df, max_rows=15):
    df_slice = df.head(max_rows)
    cols = df_slice.columns
    header_html = "".join([f"<th>{col.upper()}</th>" for col in cols])
    
    rows_html = ""
    for idx, row in df_slice.iterrows():
        row_cells = ""
        for col in cols:
            val = row[col]
            if isinstance(val, float):
                row_cells += f"<td>{val:.2f}</td>"
            elif col == 'anomaly_reason' and pd.notna(val) and val != "":
                # Split multiple reasons
                reasons = [r.strip() for r in str(val).split(";")]
                badges = "".join([f'<span class="badge badge-red" style="margin-right: 4px;">{r}</span>' for r in reasons])
                row_cells += f'<td>{badges}</td>'
            elif col == 'is_anomaly':
                badge_class = "badge-red" if val else "badge-green"
                badge_text = "Yes" if val else "No"
                row_cells += f'<td><span class="badge {badge_class}">{badge_text}</span></td>'
            else:
                row_cells += f"<td>{str(val)}</td>"
        rows_html += f"<tr>{row_cells}</tr>"
        
    return f"""
    <div class="table-container">
        <table class="data-table">
            <thead><tr>{header_html}</tr></thead>
            <tbody>{rows_html}</tbody>
        </table>
    </div>
    """

# 4. Header Section
head_left, head_right = st.columns([8, 1.5])
with head_left:
    st.markdown("""
    <div class="brand">
        <span class="brand-name">⚡ DataPulse</span>
        <span class="brand-sub">Modern CSV Cleaning & Reporting Platform</span>
    </div>
    """, unsafe_allow_html=True)
with head_right:
    theme_label = "☀️ Light Mode" if IS_DARK else "🌙 Dark Mode"
    st.button(theme_label, on_click=toggle_theme, use_container_width=True)

# 5. Core Session State
if "raw_df" not in st.session_state:
    st.session_state.raw_df = None
if "cleaned_df" not in st.session_state:
    st.session_state.cleaned_df = None
if "anomalies_df" not in st.session_state:
    st.session_state.anomalies_df = None
if "stats" not in st.session_state:
    st.session_state.stats = None
if "report" not in st.session_state:
    st.session_state.report = None

# Navigation Tabs
tab1, tab2, tab3 = st.tabs(["⚡ Upload & Clean", "📊 Analytics Dashboard", "⚠️ Anomaly Log"])

# 6. Tab 1: Upload & Clean
with tab1:
    col_upload_left, col_upload_right = st.columns([3, 2])
    
    with col_upload_left:
        st.markdown("### 📥 Source Dataset")
        uploaded_file = st.file_uploader("Upload CSV sales or inventory data file", type=["csv"], help="Must contain column fields such as date, product, category, quantity, price")
        
        # Load Sample Button
        if st.button("💡 Load Sample CSV Dataset (Demo)", use_container_width=True):
            sample_path = "sample_data.csv"
            if os.path.exists(sample_path):
                st.session_state.raw_df = pd.read_csv(sample_path)
                st.toast("Loaded sample dataset successfully!")
            else:
                st.error("Sample dataset file not found.")

    with col_upload_right:
        st.markdown("### ⚙️ Pipeline Status")
        if uploaded_file is not None:
            st.session_state.raw_df = pd.read_csv(uploaded_file)
            st.success("File uploaded successfully!")
            
        if st.session_state.raw_df is not None:
            if st.button("🚀 Run Data Cleaning & Report Pipeline", type="primary", use_container_width=True):
                with st.spinner("Processing data cleanings, normalization & anomaly detection..."):
                    # Process Cleaning
                    clean_df, stats = clean_data(st.session_state.raw_df.copy())
                    
                    # Detect Anomalies
                    anom_df = detect_anomalies(clean_df)
                    
                    # Generate report aggregates on the clean records (non-anomalous if preferred, but let's do overall clean records)
                    # We will calculate summaries on non-anomalous rows for accurate business reporting
                    clean_reports_df = anom_df[~anom_df['is_anomaly']]
                    report = generate_summary_report(clean_reports_df)
                    
                    # Store to session state
                    st.session_state.cleaned_df = clean_df
                    st.session_state.anomalies_df = anom_df
                    st.session_state.stats = stats
                    st.session_state.report = report
                    st.toast("Pipeline executed successfully!")

    if st.session_state.stats is not None:
        st.markdown("---")
        st.markdown("### 📈 Processing Metrics")
        
        # Row metrics
        mc1, mc2, mc3, mc4 = st.columns(4)
        with mc1:
            metric_card("Original Rows", f"{st.session_state.stats['initial_rows']}")
        with mc2:
            metric_card("Duplicates Dropped", f"{st.session_state.stats['duplicates_removed']}", delta_type="down" if st.session_state.stats['duplicates_removed'] > 0 else "neutral")
        with mc3:
            total_anoms = int(st.session_state.anomalies_df['is_anomaly'].sum())
            metric_card("Anomalies Flagged", f"{total_anoms}", delta_type="warn" if total_anoms > 0 else "neutral")
        with mc4:
            metric_card("Final Clean Rows", f"{st.session_state.stats['final_rows']}")
            
        # Preview Tables
        st.markdown("### 🔍 Dataset Previews")
        prev_tab1, prev_tab2 = st.tabs(["Cleaned & Flagged Data Preview", "Raw Uploaded Data Preview"])
        
        with prev_tab1:
            st.markdown("<p style='font-size: 0.8rem; color: var(--text-muted);'>Showing top 15 cleaned records with anomaly flags:</p>", unsafe_allow_html=True)
            st.markdown(render_html_table(st.session_state.anomalies_df, 15), unsafe_allow_html=True)
            
            # Export downloads
            st.markdown("#### 📥 Download Exports")
            d_col1, d_col2 = st.columns(2)
            with d_col1:
                # CSV Export
                csv_buffer = io.StringIO()
                st.session_state.anomalies_df.to_csv(csv_buffer, index=False)
                st.download_button(
                    label="📄 Download Cleaned Data (CSV)",
                    data=csv_buffer.getvalue(),
                    file_name="cleaned_datapulse_export.csv",
                    mime="text/csv",
                    use_container_width=True
                )
            with d_col2:
                # Excel Export
                excel_buffer = export_to_excel(
                    st.session_state.cleaned_df,
                    st.session_state.anomalies_df,
                    st.session_state.report
                )
                st.download_button(
                    label="📊 Download Full Multi-Sheet Report (Excel)",
                    data=excel_buffer,
                    file_name="datapulse_analysis_report.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )
                
        with prev_tab2:
            st.markdown("<p style='font-size: 0.8rem; color: var(--text-muted);'>Showing top 15 records of raw data:</p>", unsafe_allow_html=True)
            st.markdown(render_html_table(st.session_state.raw_df, 15), unsafe_allow_html=True)
    else:
        st.markdown("---")
        st.info("Please upload a CSV file or load the sample dataset, then click 'Run Data Cleaning & Report Pipeline' to start.")

# 7. Tab 2: Analytics Dashboard
with tab2:
    if st.session_state.report is not None:
        st.markdown("### 📊 Business KPI Insights")
        st.markdown("<p style='font-size: 0.8rem; color: var(--text-muted); margin-bottom: 1.5rem;'>Aggregates computed excluding anomalous transaction records.</p>", unsafe_allow_html=True)
        
        rep = st.session_state.report
        
        # KPI Row
        rc1, rc2, rc3, rc4 = st.columns(4)
        with rc1:
            metric_card("Total Net Revenue", f"${rep.get('total_revenue', 0.0):,.2f}")
        with rc2:
            metric_card("Total Units Sold", f"{rep.get('total_units', 0):,}")
        with rc3:
            metric_card("Avg Item Unit Price", f"${rep.get('avg_unit_price', 0.0):,.2f}")
        with rc4:
            metric_card("Valid Transactions", f"{rep.get('total_transactions', 0):,}")
            
        st.markdown("---")
        
        # Plotly theme setup
        PLOT_LAYOUT = dict(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(family="DM Sans, sans-serif", color="#71717a" if not IS_DARK else "#a1a1aa", size=11),
            margin=dict(l=40, r=20, t=20, b=40),
            xaxis=dict(
                gridcolor="rgba(0,0,0,0.06)" if not IS_DARK else "rgba(255,255,255,0.06)",
                zerolinecolor="rgba(0,0,0,0.06)" if not IS_DARK else "rgba(255,255,255,0.06)",
                tickfont=dict(size=10, color="#71717a"),
            ),
            yaxis=dict(
                gridcolor="rgba(0,0,0,0.06)" if not IS_DARK else "rgba(255,255,255,0.06)",
                zerolinecolor="rgba(0,0,0,0.06)" if not IS_DARK else "rgba(255,255,255,0.06)",
                tickfont=dict(size=10, color="#71717a"),
            ),
        )
        
        chart_col1, chart_col2 = st.columns(2)
        
        with chart_col1:
            st.markdown("""
            <div class="chart-wrap">
                <div class="chart-title">Revenue Trends over Time</div>
                <div class="chart-subtitle">Daily aggregate net sales revenue</div>
            """, unsafe_allow_html=True)
            
            if 'date_summary' in rep and not rep['date_summary'].empty:
                df_date = rep['date_summary']
                date_col = df_date.columns[0]
                fig = px.line(
                    df_date, 
                    x=date_col, 
                    y='total_revenue',
                    markers=True,
                    template="plotly_dark" if IS_DARK else "plotly_white"
                )
                fig.update_traces(line=dict(color=accent, width=2.5), marker=dict(size=6, color=accent))
                fig.update_layout(**PLOT_LAYOUT)
                st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
            else:
                st.info("No date columns or data found for trend analysis.")
            st.markdown("</div>", unsafe_allow_html=True)
            
        with chart_col2:
            st.markdown("""
            <div class="chart-wrap">
                <div class="chart-title">Category Revenue Contribution</div>
                <div class="chart-subtitle">Distribution of net sales revenue by product category</div>
            """, unsafe_allow_html=True)
            
            if 'category_summary' in rep and not rep['category_summary'].empty:
                df_cat = rep['category_summary']
                fig = px.bar(
                    df_cat,
                    x='category',
                    y='total_revenue',
                    color='category',
                    color_discrete_sequence=px.colors.qualitative.Bold,
                    template="plotly_dark" if IS_DARK else "plotly_white"
                )
                fig.update_layout(**PLOT_LAYOUT, showlegend=False)
                st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
            else:
                st.info("No category summary data found.")
            st.markdown("</div>", unsafe_allow_html=True)
            
        # Additional visual tables
        st.markdown("### 🗂️ Category Performance Ledger")
        if 'category_summary' in rep:
            st.markdown(render_html_table(rep['category_summary'], 10), unsafe_allow_html=True)
    else:
        st.info("No pipeline calculations present. Please run the data pipeline in the 'Upload & Clean' tab first.")

# 8. Tab 3: Anomaly Log
with tab3:
    if st.session_state.anomalies_df is not None:
        anoms = st.session_state.anomalies_df[st.session_state.anomalies_df['is_anomaly']]
        
        st.markdown("### ⚠️ Flagged Anomalies Log")
        st.markdown(f"<p style='font-size: 0.8rem; color: var(--text-muted);'>Found {len(anoms)} transactions with pricing/quantity flags or statistical outliers.</p>", unsafe_allow_html=True)
        
        if not anoms.empty:
            st.markdown(render_html_table(anoms, 50), unsafe_allow_html=True)
        else:
            st.success("No anomalies detected in this dataset!")
    else:
        st.info("No anomalies analyzed. Please process a dataset in the 'Upload & Clean' tab first.")
