from pathlib import Path
import tempfile
import pandas as pd
import plotly.express as px
import streamlit as st
from clean import extract_posts, read_and_clean_excel


st.set_page_config(page_title="AMR ADEL | LinkedIn Analytics", page_icon="📊", layout="wide")

st.markdown(
    """
    <style>
    .main {background: linear-gradient(135deg, #f8fbff 0%, #eef6ff 100%);}
    .block-container {padding-top: 1rem; padding-bottom: 2rem;}
    .kpi-card {
        background: #ffffff;
        border-radius: 16px;
        padding: 16px 18px;
        border: 1px solid #e7edfa;
        box-shadow: 0 8px 20px rgba(13, 42, 97, 0.07);
        min-height: 120px;
    }
    .kpi-title {
        font-size: 0.88rem;
        color: #4a6289;
        margin-bottom: 8px;
        font-weight: 700;
    }
    .kpi-value {
        font-size: 1.7rem;
        color: #0d2f6a;
        font-weight: 800;
        line-height: 1.1;
    }
    .kpi-sub {
        margin-top: 7px;
        font-size: 0.80rem;
        color: #6f84a7;
    }
    .section-title {
        margin-top: 10px;
        margin-bottom: 8px;
        color: #0f2f66;
        font-weight: 900;
        font-size: 1.18rem;
    }
    .insight-box {
        border: 1px solid #d8e5ff;
        background: #f6faff;
        border-radius: 12px;
        padding: 12px 14px;
        margin-bottom: 8px;
        color: #1f3b66;
    }
    </style>
    """,
    unsafe_allow_html=True
)


PROFILE_HEADLINE_DEFAULT = "Business Data Scientist / Applied AI Engineer"
PROFILE_ABOUT_DEFAULT = (
    "Detail-oriented Applied AI Engineer with a strong foundation in Business Data Science and Data Engineering. "
    "3+ years of experience in the data lifecycle, progressing from building robust ETL pipelines to deploying "
    "production-ready Generative AI agents and optimization engines. Passionate about bridging the gap between "
    "business requirements and technical AI implementation using RAG, LLMs, and Operations Research."
)
POSTING_GOAL_DEFAULT = "Grow thought leadership, improve engagement quality, and increase relevant opportunities."
PROJECTS_CATALOG = [
    {
        "name": "Janssen AI Agent",
        "categories": ["NLP/LLM", "RAG", "Voice AI", "Real-time Systems", "MLOps/Deployment"],
        "goal": "Built a multimodal intelligent support agent for Janssen products with strict domain grounding.",
        "implementation": "Developed FastAPI APIs, integrated GPT-4o and Whisper, added retrieval with Qdrant, enforced response governance, persisted logs in MySQL, and packaged with Docker.",
        "stack": "Python, FastAPI, GPT-4o, Whisper-1, Qdrant, MySQL, Docker"
    },
    {
        "name": "C&S Data Pipeline",
        "categories": ["Data Engineering/ETL", "BI/Dashboarding"],
        "goal": "Transformed raw CRM service data into trusted analytics-ready datasets.",
        "implementation": "Designed separate pipelines for calls, customers, orders, and tickets; normalized JSON; generated IDs; standardized dates; and delivered final Excel analytical tables.",
        "stack": "Python, pandas, Jupyter, Excel, JSON"
    },
    {
        "name": "Executive Proposal Automation System",
        "categories": ["NLP/LLM", "Automation", "BI/Dashboarding"],
        "goal": "Converted PDF client requirements into executive-ready proposal outputs.",
        "implementation": "Extracted and structured PDF text with MECE logic, generated schema-based JSON, validated with Pydantic, and produced presentation output through MCP PowerPoint in a Streamlit workflow.",
        "stack": "Python, Streamlit, pdfplumber/PyPDF2, Pydantic, Ollama, MCP PowerPoint"
    },
    {
        "name": "Ecommerce Shipping Analysis & Delivery Time Prediction",
        "categories": ["Machine Learning", "BI/Dashboarding", "Data Engineering/ETL"],
        "goal": "Analyzed shipping delay drivers and prepared predictive delivery-time models.",
        "implementation": "Merged multi-source CSV datasets, performed quality checks and EDA, engineered predictive features, and built model-ready training datasets.",
        "stack": "Python, pandas, seaborn, matplotlib, scikit-learn, Jupyter"
    },
    {
        "name": "Healthcare Analytics",
        "categories": ["BI/Dashboarding", "Machine Learning", "NLP/LLM"],
        "goal": "Created a healthcare analytics platform for risk insights and AI-generated reporting.",
        "implementation": "Built modular data and visualization layers, delivered interactive Streamlit pages, implemented clustering and anomaly detection, and integrated Ollama summaries.",
        "stack": "Python, Streamlit, NiceGUI, Plotly, pandas, Ollama"
    },
    {
        "name": "Insurance Customer Data Analysis",
        "categories": ["Machine Learning", "BI/Dashboarding"],
        "goal": "Improved customer understanding, CLV estimation, and campaign decisions.",
        "implementation": "Ran end-to-end EDA, engineered business features, and prepared data for classification, regression, and clustering workflows tied to business KPIs.",
        "stack": "Python, pandas, numpy, matplotlib, seaborn, scikit-learn, Jupyter"
    },
    {
        "name": "JANSSEN CRM",
        "categories": ["CRM Analytics", "BI/Dashboarding", "Data Engineering/ETL"],
        "goal": "Built an analytics-first CRM platform to optimize service quality and SLA tracking.",
        "implementation": "Implemented customer/call/ticket analytics pages, performance dashboards, and Google Drive integration for synchronized data operations.",
        "stack": "Python, Streamlit, pandas, plotly, SQLAlchemy, Google Drive API"
    },
    {
        "name": "Truck Management System (Logistics)",
        "categories": ["Optimization/Operations Research", "Machine Learning", "BI/Dashboarding"],
        "goal": "Optimized fleet allocation and distribution planning using operational analytics.",
        "implementation": "Applied K-means for geo-clustering, OR-Tools for allocation logic, packing algorithms for loading constraints, and dashboard monitoring for decision support.",
        "stack": "Python, Streamlit, OR-Tools, pandas, scikit-learn, plotly, geopy"
    },
    {
        "name": "Economic News & Gold Price Prediction",
        "categories": ["NLP/LLM", "Time Series Forecasting", "Deep Learning", "Machine Learning"],
        "goal": "Predicted gold market direction by fusing economic news and market indicators.",
        "implementation": "Built NLP feature pipelines, trained ARIMA/Prophet/LSTM models, added PyTorch deep learning experiments, and generated market summaries with Ollama.",
        "stack": "Python, NLP, PyTorch, ARIMA, Prophet, LSTM, Ollama"
    },
    {
        "name": "Stock Analysis & Future Price Prediction",
        "categories": ["Time Series Forecasting", "Deep Learning", "BI/Dashboarding"],
        "goal": "Delivered stock forecasting through technical indicators and LSTM modeling.",
        "implementation": "Pulled Yahoo Finance data, computed 35 technical indicators, trained LSTM forecasting models, and built an interactive Streamlit interface.",
        "stack": "Python, Streamlit, yfinance, pandas, numpy, matplotlib, LSTM"
    },
    {
        "name": "Voice AI Agent (Real-time Assistant)",
        "categories": ["Voice AI", "NLP/LLM", "RAG", "Real-time Systems"],
        "goal": "Created a real-time voice assistant that listens, reasons with private context, and answers naturally.",
        "implementation": "Implemented FastAPI WebSocket streaming, STT with Wav2Vec2, RAG response generation with GPT-4o + Qdrant, and speech synthesis with OpenAI TTS.",
        "stack": "Python, FastAPI WebSockets, GPT-4o, OpenAI TTS, Qdrant, Wav2Vec2, NumPy"
    }
]


def fmt_int(value):
    if pd.isna(value):
        return "0"
    return f"{int(round(value)):,}"


def fmt_float(value, digits=2):
    if pd.isna(value):
        return f"{0:.{digits}f}"
    return f"{float(value):,.{digits}f}"


def fmt_pct(value, digits=2):
    if pd.isna(value):
        return f"{0:.{digits}f}%"
    return f"{float(value) * 100:.{digits}f}%"


def save_uploaded_file(uploaded_file, suffix):
    temp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    temp.write(uploaded_file.getbuffer())
    temp.flush()
    return temp.name


@st.cache_data(show_spinner=False)
def load_learning_content():
    guide_path = Path(__file__).resolve().parent / "LinkedIn_Content_Creation.md"
    if not guide_path.exists():
        return "Learning guide file not found."
    return guide_path.read_text(encoding="utf-8")


def build_scientific_prompt(guide_text, profile_headline, profile_about, posting_goal):
    return (
        "You are an evidence-based LinkedIn strategist.\n\n"
        f"Profile Headline: {profile_headline}\n"
        f"Profile About: {profile_about}\n"
        f"Publishing Goal: {posting_goal}\n\n"
        "Use the framework below as a strict methodology to produce a high-performance content plan:\n\n"
        f"{guide_text}\n\n"
        "Now deliver:\n"
        "1) A 14-day content plan.\n"
        "2) 10 post ideas mapped to funnel stages.\n"
        "3) 3 hook variants per idea.\n"
        "4) Keyword strategy (primary, secondary, LSI).\n"
        "5) A/B tests and success metrics.\n"
    )


@st.cache_data(show_spinner=False)
def load_data(posts_path: str, excel_path: str):
    posts_df = extract_posts(posts_path)
    merged_df, demographics_df = read_and_clean_excel(excel_path)
    posts_df = posts_df.copy()
    merged_df = merged_df.copy()
    demographics_df = demographics_df.copy()
    posts_df["actual_date"] = pd.to_datetime(posts_df["actual_date"], errors="coerce")
    merged_df["date"] = pd.to_datetime(merged_df["date"], errors="coerce")
    for col in ["likes", "comments", "impressions", "reposts", "is_text", "is_image", "is_link", "is_pdf", "arabic_word_count", "english_word_count", "emoji_count"]:
        posts_df[col] = pd.to_numeric(posts_df[col], errors="coerce").fillna(0)
    for col in ["impressions", "engagements", "new_followers"]:
        merged_df[col] = pd.to_numeric(merged_df[col], errors="coerce").fillna(0)
    demographics_df["percentage"] = pd.to_numeric(demographics_df["percentage"], errors="coerce").fillna(0)
    posts_df["engagement_actions"] = posts_df["likes"] + posts_df["comments"] + posts_df["reposts"]
    posts_df["engagement_rate"] = posts_df["engagement_actions"].div(posts_df["impressions"].replace(0, pd.NA)).fillna(0)
    posts_df["comments_rate"] = posts_df["comments"].div(posts_df["impressions"].replace(0, pd.NA)).fillna(0)
    posts_df["reposts_rate"] = posts_df["reposts"].div(posts_df["impressions"].replace(0, pd.NA)).fillna(0)
    posts_df["likes_rate"] = posts_df["likes"].div(posts_df["impressions"].replace(0, pd.NA)).fillna(0)
    posts_df["hook"] = posts_df["hook"].fillna("").astype(str)
    posts_df["hook_length"] = posts_df["hook"].str.len()
    posts_df["hook_word_count"] = posts_df["hook"].str.split().str.len().fillna(0)
    posts_df["hook_has_question"] = posts_df["hook"].str.contains(r"\?|؟", regex=True).astype(int)
    posts_df["hook_has_number"] = posts_df["hook"].str.contains(r"\d", regex=True).astype(int)
    posts_df["hook_has_emoji"] = posts_df["hook"].str.contains(r"[\U0001F300-\U0001FAFF]", regex=True).astype(int)
    posts_df["hook_has_alert_word"] = posts_df["hook"].str.contains(
        r"\b(why|how|what|when|urgent|stop|secret|mistake|truth|guide)\b|"
        r"(ليه|كيف|ازاي|لماذا|تحذير|سر|خطأ|دليل)",
        regex=True,
        case=False
    ).astype(int)
    posts_df["total_words"] = posts_df["arabic_word_count"] + posts_df["english_word_count"]
    posts_df["arabic_ratio"] = posts_df["arabic_word_count"].div(posts_df["total_words"].replace(0, pd.NA)).fillna(0)
    posts_df["english_ratio"] = posts_df["english_word_count"].div(posts_df["total_words"].replace(0, pd.NA)).fillna(0)
    merged_df["daily_engagement_rate"] = merged_df["engagements"].div(merged_df["impressions"].replace(0, pd.NA)).fillna(0)
    return posts_df, merged_df, demographics_df


def create_kpi_card(title, value, subtitle):
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-title">{title}</div>
            <div class="kpi-value">{value}</div>
            <div class="kpi-sub">{subtitle}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


def explode_post_types(df):
    out = df.copy()
    out["post_types"] = out["post_types"].fillna("Unknown")
    out["post_type"] = out["post_types"].str.split(",")
    out = out.explode("post_type")
    out["post_type"] = out["post_type"].astype(str).str.strip()
    return out[out["post_type"] != ""]


def behavior_by_hook_feature(df, feature):
    grouped = df.groupby(feature, as_index=False).agg(
        posts=("engagement_rate", "size"),
        avg_engagement_rate=("engagement_rate", "mean"),
        avg_impressions=("impressions", "mean"),
        avg_comments=("comments", "mean"),
        total_reposts=("reposts", "sum")
    )
    grouped[feature] = grouped[feature].map({0: "No", 1: "Yes"})
    return grouped


def compute_kpis(posts_df, merged_df):
    return {
        "Total posts": len(posts_df),
        "Total post impressions": posts_df["impressions"].sum(),
        "Total post interactions": posts_df["engagement_actions"].sum(),
        "Total likes": posts_df["likes"].sum(),
        "Total comments": posts_df["comments"].sum(),
        "Total reposts": posts_df["reposts"].sum(),
        "Average impressions per post": posts_df["impressions"].mean(),
        "Average interactions per post": posts_df["engagement_actions"].mean(),
        "Average post engagement rate": posts_df["engagement_rate"].mean(),
        "Average comment rate": posts_df["comments_rate"].mean(),
        "Average repost rate": posts_df["reposts_rate"].mean(),
        "Average like rate": posts_df["likes_rate"].mean(),
        "Total Arabic words": posts_df["arabic_word_count"].sum(),
        "Total English words": posts_df["english_word_count"].sum(),
        "Total emojis": posts_df["emoji_count"].sum(),
        "Average hook length": posts_df["hook_length"].mean(),
        "Average hook words": posts_df["hook_word_count"].mean(),
        "Question hooks ratio": posts_df["hook_has_question"].mean(),
        "Numeric hooks ratio": posts_df["hook_has_number"].mean(),
        "Emoji hooks ratio": posts_df["hook_has_emoji"].mean(),
        "Alert-word hooks ratio": posts_df["hook_has_alert_word"].mean(),
        "Total daily impressions": merged_df["impressions"].sum(),
        "Total daily engagements": merged_df["engagements"].sum(),
        "Total new followers": merged_df["new_followers"].sum(),
        "Average daily engagement rate": merged_df["daily_engagement_rate"].mean()
    }


def compute_weekly_kpis(merged_df):
    weekly = merged_df.copy()
    weekly["week_start"] = weekly["date"] - pd.to_timedelta(weekly["date"].dt.weekday, unit="D")
    weekly = weekly.groupby("week_start", as_index=False).agg(
        impressions=("impressions", "sum"),
        engagements=("engagements", "sum"),
        new_followers=("new_followers", "sum"),
        active_days=("date", "nunique")
    )
    weekly["weekly_engagement_rate"] = weekly["engagements"].div(weekly["impressions"].replace(0, pd.NA)).fillna(0)
    weekly["avg_daily_impressions"] = weekly["impressions"].div(weekly["active_days"].replace(0, pd.NA)).fillna(0)
    weekly["avg_daily_engagements"] = weekly["engagements"].div(weekly["active_days"].replace(0, pd.NA)).fillna(0)
    weekly["avg_daily_new_followers"] = weekly["new_followers"].div(weekly["active_days"].replace(0, pd.NA)).fillna(0)
    return weekly.sort_values("week_start")


def generate_insights(posts_df, merged_df, demographics_df):
    insights = []
    top_impression = posts_df.sort_values("impressions", ascending=False).iloc[0]
    top_engagement = posts_df.sort_values("engagement_rate", ascending=False).iloc[0]
    insights.append(f"Highest reach post: {top_impression['actual_date'].date()} with {fmt_int(top_impression['impressions'])} impressions.")
    insights.append(f"Highest engagement efficiency: {top_engagement['actual_date'].date()} at {fmt_pct(top_engagement['engagement_rate'])}.")
    hook_q = posts_df.groupby("hook_has_question", as_index=False)["engagement_rate"].mean()
    if len(hook_q) == 2:
        yes = hook_q.loc[hook_q["hook_has_question"] == 1, "engagement_rate"].iloc[0]
        no = hook_q.loc[hook_q["hook_has_question"] == 0, "engagement_rate"].iloc[0]
        insights.append(f"Question-style hooks impact engagement by {fmt_pct(yes - no)} compared to non-question hooks.")
    best_day = merged_df.sort_values("impressions", ascending=False).iloc[0]
    insights.append(f"Best daily reach: {best_day['date'].date()} with {fmt_int(best_day['impressions'])} impressions.")
    top_demo = demographics_df.sort_values("percentage", ascending=False).iloc[0]
    insights.append(f"Strongest audience segment: {top_demo['category']} / {top_demo['value']} at {fmt_pct(top_demo['percentage'])}.")
    return insights


def build_markdown_report(
    kpis,
    insights,
    top_posts,
    hooks_table,
    hook_feature_table,
    demographics_full,
    weekly_kpis_table,
    scientific_prompt,
    period_text,
    profile_headline,
    profile_about,
    posting_goal
):
    def df_to_md(df):
        if df.empty:
            return "| No data |\n|---|"
        safe_df = df.copy()
        for col in safe_df.columns:
            safe_df[col] = safe_df[col].astype(str).str.replace("|", "\\|", regex=False)
        header = "| " + " | ".join(safe_df.columns.astype(str)) + " |"
        separator = "| " + " | ".join(["---"] * len(safe_df.columns)) + " |"
        rows = ["| " + " | ".join(row) + " |" for row in safe_df.astype(str).values.tolist()]
        return "\n".join([header, separator] + rows)

    lines = []
    lines.append("# LinkedIn Deep Analytics Report")
    lines.append("")
    lines.append(f"**Analysis Period:** {period_text}")
    lines.append("")
    lines.append("## 0) Profile Context")
    lines.append("")
    lines.append(f"**Headline:** {profile_headline if profile_headline.strip() else 'Not provided'}")
    lines.append("")
    lines.append("**About:**")
    lines.append("")
    lines.append(profile_about if profile_about.strip() else "Not provided")
    lines.append("")
    lines.append(f"**Publishing Goal:** {posting_goal if posting_goal.strip() else 'Not provided'}")
    lines.append("")
    lines.append("## 1) KPI Dictionary + Values")
    lines.append("")
    lines.append("| KPI | Value |")
    lines.append("|---|---:|")
    for kpi_name, value in kpis.items():
        if "rate" in kpi_name.lower() or "ratio" in kpi_name.lower():
            value_text = fmt_pct(value)
        elif "average" in kpi_name.lower():
            value_text = fmt_float(value, 2)
        else:
            value_text = fmt_int(value)
        lines.append(f"| {kpi_name} | {value_text} |")
    lines.append("")
    lines.append("## 2) Key Insights")
    lines.append("")
    for item in insights:
        lines.append(f"- {item}")
    lines.append("")
    lines.append("## 3) Hook Performance Matrix")
    lines.append("")
    lines.append(df_to_md(hook_feature_table))
    lines.append("")
    lines.append("## 4) Top Posts")
    lines.append("")
    lines.append(df_to_md(top_posts))
    lines.append("")
    lines.append("## 5) Last 15 Hooks")
    lines.append("")
    lines.append(df_to_md(hooks_table))
    lines.append("")
    lines.append("## 6) Full Demographics Table")
    lines.append("")
    lines.append(df_to_md(demographics_full))
    lines.append("")
    lines.append("## 7) Weekly KPIs (from merged_df)")
    lines.append("")
    lines.append(df_to_md(weekly_kpis_table))
    lines.append("")
    lines.append("## 8) Scientific LLM Prompt for LinkedIn Content Creation")
    lines.append("")
    lines.append("```text")
    lines.append(scientific_prompt)
    lines.append("```")
    lines.append("")
    return "\n".join(lines)


def render_projects_portfolio():
    st.markdown("### Projects Portfolio")
    all_categories = sorted({cat for project in PROJECTS_CATALOG for cat in project["categories"]})
    st.markdown("#### Category Checklist")
    selected_categories = []
    cols = st.columns(4)
    for idx, category in enumerate(all_categories):
        with cols[idx % 4]:
            if st.checkbox(category, value=True, key=f"cat_{category}"):
                selected_categories.append(category)
    filtered_projects = [
        project for project in PROJECTS_CATALOG
        if any(cat in selected_categories for cat in project["categories"])
    ]
    st.write(f"Showing {len(filtered_projects)} of {len(PROJECTS_CATALOG)} projects.")
    for project in filtered_projects:
        with st.expander(project["name"], expanded=False):
            st.markdown(f"**Categories:** {', '.join(project['categories'])}")
            st.markdown(f"**Project Goal:** {project['goal']}")
            st.markdown(f"**Implementation Details:** {project['implementation']}")
            st.markdown(f"**Tech Stack:** {project['stack']}")


def render_about_page():
    st.title("About AMR ADEL")
    col_a, col_b = st.columns([1, 2])
    with col_a:
        st.markdown(
            """
            <div style="border:1px solid #e7edfa; border-radius:16px; padding:14px; background:white; text-align:center;">
                <img src="https://github.com/amradel18.png" style="width:200px; height:260px; object-fit:contain; border-radius:12px; background:#f5f8ff;" />
                <div style="font-size:12px; color:#6f84a7; margin-top:8px;">Profile Image</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with col_b:
        st.subheader("AMR ADEL")
        st.write("Business Data Scientist / Applied AI Engineer")
        st.write("📧 amr800mr90@gmail.com")
        st.write("📱 +20 1050994572")
        st.write("📍 Obour, Qalyubia, Egypt")
        st.write("🔗 LinkedIn: www.linkedin.com/in/amr-adel-4828452ab")
        st.write("🔗 GitHub: https://github.com/amradel18")
    st.markdown("### Profile")
    st.write(PROFILE_ABOUT_DEFAULT)
    st.markdown("### Work Style")
    st.markdown(
        """
        - Business-first problem framing before model selection.
        - End-to-end ownership from data engineering to deployment.
        - Practical AI delivery with measurable operational impact.
        - Strong focus on reliability, explainability, and stakeholder communication.
        """
    )
    st.markdown("### Education")
    st.write("Bachelor of Business Administration (BBA) — Institute of Cooperative and Administrative Studies, Cairo (01/2021 – 05/2025), Grade: Very Good.")
    st.markdown("### Professional Experience")
    st.markdown(
        """
        - Applied AI & Intelligent Automation Engineer, Bed Janssen (03/2024 – 01/2026)
        - Data Science & Optimization Analyst, Bed Janssen (08/2023 – 05/2024)
        - Business Analyst & Data Engineer
        """
    )
    render_projects_portfolio()
    st.markdown("### Skills")
    st.write("Python, FastAPI, Streamlit, Power BI, AWS, PyTorch, LLM, SQL, Docker, Pandas, Scikit-learn, NLP, Operations Research, Git/GitHub.")


def render_help_page():
    st.title("Help")

    st.markdown(
        """
        ### How to Use the Analytics Page
        1. Copy your **best LinkedIn posts** from the past 365 days and paste them into a text file named `posts_linkedin.txt`.
        2. Download your LinkedIn analytics report covering the **last 365 days** as an Excel file (it usually contains sheets: `DISCOVERY`, `ENGAGEMENT`, `FOLLOWERS`, `DEMOGRAPHICS`).
        3. Upload both files (`Content.xlsx` and `posts_linkedin.txt`) to the app.
        4. Fill in your profile context fields: **Headline**, **About**, and your **Publishing Goal**.
        5. Select the analysis date range.
        6. Review KPIs, charts, insights, hooks, demographics, and weekly KPIs.
        7. Download the generated Markdown report.
        8. Copy the report into any LLM (e.g., ChatGPT) and ask for:
           - A deeper page analysis
           - New content ideas
           - Practical steps for improvement
        """
    )
    st.title("Link to the tutorial video on Google Drive")
    st.markdown(
                '<a href="https://drive.google.com/file/d/1IS3D_q4NsTp6-3af80ZMZMl_KnBuYFn8/view?usp=drive_link" style="color:blue;">Open Help Video</a>',
                unsafe_allow_html=True
            )





def render_learn_page():
    st.title("Learn")
    st.caption("LinkedIn scientific content creation framework")
    guide_text = load_learning_content()
    st.markdown(guide_text)


def render_analytics_page():
    st.title("LinkedIn Deep Analytics App")
    st.caption("Built by AMR ADEL — Business Data Scientist / Applied AI Engineer")

    with st.sidebar:
        st.subheader("Data Source")
        uploaded_excel = st.file_uploader("Upload Content.xlsx", type=["xlsx"])
        uploaded_posts = st.file_uploader("Upload posts_linkedin.txt", type=["txt"])
        use_local = st.checkbox("Use local default files if no upload", value=True)
        st.subheader("Profile Context for Report")
        profile_headline = st.text_input("LinkedIn Headline", value=PROFILE_HEADLINE_DEFAULT)
        profile_about = st.text_area("LinkedIn About", value=PROFILE_ABOUT_DEFAULT, height=140)
        posting_goal = st.text_area("Publishing Goal", value=POSTING_GOAL_DEFAULT, height=90)

    excel_path = None
    posts_path = None
    base_dir = Path(__file__).resolve().parent
    local_excel = base_dir / "Content.xlsx"
    local_posts = base_dir / "posts_linkedin.txt"

    if uploaded_excel is not None:
        excel_path = save_uploaded_file(uploaded_excel, ".xlsx")
    elif use_local and local_excel.exists():
        excel_path = str(local_excel)

    if uploaded_posts is not None:
        posts_path = save_uploaded_file(uploaded_posts, ".txt")
    elif use_local and local_posts.exists():
        posts_path = str(local_posts)

    if not excel_path or not posts_path:
        st.info("Upload both files from the sidebar or enable local defaults.")
        return

    posts, merged_data, demographics_data = load_data(posts_path, excel_path)
    posts = posts.dropna(subset=["actual_date"]).copy()
    merged_data = merged_data.dropna(subset=["date"]).copy()

    if posts.empty or merged_data.empty:
        st.error("No sufficient data after cleaning.")
        return

    min_date = min(posts["actual_date"].min().date(), merged_data["date"].min().date())
    max_date = max(posts["actual_date"].max().date(), merged_data["date"].max().date())
    date_range = st.slider("Date range", min_value=min_date, max_value=max_date, value=(min_date, max_date))
    start_date = pd.to_datetime(date_range[0])
    end_date = pd.to_datetime(date_range[1])

    posts_filtered = posts[(posts["actual_date"] >= start_date) & (posts["actual_date"] <= end_date)].copy()
    merged_filtered = merged_data[(merged_data["date"] >= start_date) & (merged_data["date"] <= end_date)].copy()
    if posts_filtered.empty:
        posts_filtered = posts.copy()
    if merged_filtered.empty:
        merged_filtered = merged_data.copy()

    kpis = compute_kpis(posts_filtered, merged_filtered)
    st.markdown('<div class="section-title">Core KPIs</div>', unsafe_allow_html=True)
    kpi_items = [
        ("Total posts", fmt_int(kpis["Total posts"]), "Content volume"),
        ("Total impressions", fmt_int(kpis["Total post impressions"]), "Reach"),
        ("Total interactions", fmt_int(kpis["Total post interactions"]), "Likes + comments + reposts"),
        ("Avg engagement rate", fmt_pct(kpis["Average post engagement rate"]), "Interactions / impressions"),
        ("Total likes", fmt_int(kpis["Total likes"]), "Appreciation signal"),
        ("Total comments", fmt_int(kpis["Total comments"]), "Discussion depth"),
        ("Total reposts", fmt_int(kpis["Total reposts"]), "Distribution strength"),
        ("Avg comment rate", fmt_pct(kpis["Average comment rate"]), "Comments / impressions"),
        ("Arabic words", fmt_int(kpis["Total Arabic words"]), "Arabic footprint"),
        ("English words", fmt_int(kpis["Total English words"]), "English footprint"),
        ("Emojis", fmt_int(kpis["Total emojis"]), "Expression markers"),
        ("Avg hook length", fmt_float(kpis["Average hook length"], 1), "Characters")
    ]
    for i in range(0, len(kpi_items), 4):
        cols = st.columns(4)
        for col, item in zip(cols, kpi_items[i:i + 4]):
            with col:
                create_kpi_card(item[0], item[1], item[2])

    st.markdown('<div class="section-title">Visual Analytics</div>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    timeline = merged_filtered.melt(
        id_vars="date",
        value_vars=["impressions", "engagements", "new_followers"],
        var_name="metric",
        value_name="value"
    )
    fig_timeline = px.line(
        timeline,
        x="date",
        y="value",
        color="metric",
        markers=True,
        title="Daily trend: impressions, engagements, followers",
        template="plotly_white"
    )
    with col1:
        st.plotly_chart(fig_timeline, use_container_width=True)

    top_posts = posts_filtered.sort_values("impressions", ascending=False).head(12).copy()
    top_posts["label"] = top_posts["actual_date"].dt.strftime("%Y-%m-%d") + " | " + top_posts["hook"].str.slice(0, 48)
    fig_top_posts = px.bar(
        top_posts.sort_values("impressions"),
        x="impressions",
        y="label",
        color="engagement_rate",
        orientation="h",
        color_continuous_scale="Viridis",
        title="Top posts by reach",
        template="plotly_white"
    )
    with col2:
        st.plotly_chart(fig_top_posts, use_container_width=True)

    col3, col4 = st.columns(2)
    types_df = explode_post_types(posts_filtered)
    type_performance = types_df.groupby("post_type", as_index=False).agg(
        posts=("post_type", "size"),
        impressions=("impressions", "mean"),
        engagement_rate=("engagement_rate", "mean"),
        comments=("comments", "mean"),
        reposts=("reposts", "sum")
    )
    fig_type_perf = px.bar(
        type_performance.sort_values("engagement_rate", ascending=False),
        x="post_type",
        y="engagement_rate",
        color="comments",
        text=type_performance.sort_values("engagement_rate", ascending=False)["engagement_rate"].map(lambda x: f"{x*100:.2f}%"),
        title="Content type efficiency",
        template="plotly_white"
    )
    fig_type_perf.update_traces(textposition="outside")
    with col3:
        st.plotly_chart(fig_type_perf, use_container_width=True)

    corr_columns = ["impressions", "likes", "comments", "reposts", "arabic_word_count", "english_word_count", "emoji_count", "hook_length", "hook_word_count", "engagement_rate"]
    corr_df = posts_filtered[corr_columns].corr(numeric_only=True).round(2)
    fig_corr = px.imshow(corr_df, text_auto=True, color_continuous_scale="RdBu", zmin=-1, zmax=1, title="Correlation matrix")
    with col4:
        st.plotly_chart(fig_corr, use_container_width=True)

    st.markdown('<div class="section-title">Hook Analytics</div>', unsafe_allow_html=True)
    col5, col6 = st.columns(2)
    hook_features = ["hook_has_question", "hook_has_number", "hook_has_emoji", "hook_has_alert_word"]
    selected_hook_feature = st.selectbox("Select hook feature", options=hook_features)
    hook_behavior = behavior_by_hook_feature(posts_filtered, selected_hook_feature)
    fig_hook = px.bar(
        hook_behavior,
        x=selected_hook_feature,
        y="avg_engagement_rate",
        color="avg_impressions",
        text=hook_behavior["avg_engagement_rate"].map(lambda x: f"{x*100:.2f}%"),
        title=f"Impact of {selected_hook_feature}",
        template="plotly_white"
    )
    fig_hook.update_traces(textposition="outside")
    with col5:
        st.plotly_chart(fig_hook, use_container_width=True)

    hook_length_band = posts_filtered.copy()
    if hook_length_band["hook_length"].nunique() > 1:
        hook_length_band["hook_band"] = pd.qcut(hook_length_band["hook_length"], q=4, duplicates="drop")
    else:
        hook_length_band["hook_band"] = "Single-Band"
    band_perf = hook_length_band.groupby("hook_band", as_index=False).agg(
        posts=("hook_band", "size"),
        avg_engagement_rate=("engagement_rate", "mean"),
        avg_impressions=("impressions", "mean")
    )
    band_perf["hook_band"] = band_perf["hook_band"].astype(str)
    fig_hook_len = px.line(
        band_perf,
        x="hook_band",
        y=["avg_engagement_rate", "avg_impressions"],
        markers=True,
        title="Hook length effect",
        template="plotly_white"
    )
    with col6:
        st.plotly_chart(fig_hook_len, use_container_width=True)

    st.markdown('<div class="section-title">Text & Language Analytics</div>', unsafe_allow_html=True)
    col7, col8 = st.columns(2)
    lang_mix = posts_filtered.copy()
    lang_mix["language_bucket"] = pd.cut(lang_mix["arabic_ratio"], bins=[-0.01, 0.2, 0.6, 1], labels=["English-led", "Mixed", "Arabic-led"])
    lang_perf = lang_mix.groupby("language_bucket", as_index=False).agg(
        posts=("language_bucket", "size"),
        avg_engagement_rate=("engagement_rate", "mean"),
        avg_comments=("comments", "mean"),
        total_reposts=("reposts", "sum")
    )
    fig_lang = px.bar(
        lang_perf,
        x="language_bucket",
        y="avg_engagement_rate",
        color="avg_comments",
        text=lang_perf["avg_engagement_rate"].map(lambda x: f"{x*100:.2f}%"),
        title="Language pattern performance",
        template="plotly_white"
    )
    fig_lang.update_traces(textposition="outside")
    with col7:
        st.plotly_chart(fig_lang, use_container_width=True)

    emoji_band = posts_filtered.copy()
    emoji_band["emoji_bucket"] = pd.cut(emoji_band["emoji_count"], bins=[-0.01, 0, 2, 5, 100], labels=["0", "1-2", "3-5", "6+"])
    emoji_perf = emoji_band.groupby("emoji_bucket", as_index=False).agg(
        posts=("emoji_bucket", "size"),
        avg_engagement_rate=("engagement_rate", "mean"),
        avg_impressions=("impressions", "mean")
    )
    fig_emoji = px.bar(
        emoji_perf,
        x="emoji_bucket",
        y="avg_engagement_rate",
        color="avg_impressions",
        title="Emoji density impact",
        template="plotly_white"
    )
    with col8:
        st.plotly_chart(fig_emoji, use_container_width=True)

    insights = generate_insights(posts_filtered, merged_filtered, demographics_data)
    for insight in insights:
        st.markdown(f'<div class="insight-box">• {insight}</div>', unsafe_allow_html=True)

    st.markdown('<div class="section-title">Static Markdown Report</div>', unsafe_allow_html=True)
    with st.expander("Profile context included in report"):
        st.write("**Headline:**", profile_headline if profile_headline.strip() else "Not provided")
        st.write("**About:**")
        st.write(profile_about if profile_about.strip() else "Not provided")
        st.write("**Goal:**", posting_goal if posting_goal.strip() else "Not provided")

    top_posts_report = posts_filtered.sort_values("engagement_rate", ascending=False).head(10)[
        ["actual_date", "hook", "impressions", "likes", "comments", "reposts", "engagement_rate", "arabic_word_count", "english_word_count", "emoji_count"]
    ].copy()
    top_posts_report["actual_date"] = top_posts_report["actual_date"].dt.strftime("%Y-%m-%d")
    top_posts_report["engagement_rate"] = top_posts_report["engagement_rate"].map(lambda x: f"{x*100:.2f}%")

    hooks_table = posts_filtered.sort_values("actual_date", ascending=False).head(15)[
        ["actual_date", "hook", "post_types", "impressions", "engagement_rate"]
    ].copy()
    hooks_table["actual_date"] = hooks_table["actual_date"].dt.strftime("%Y-%m-%d")
    hooks_table["engagement_rate"] = hooks_table["engagement_rate"].map(lambda x: f"{x*100:.2f}%")

    hook_feature_table_parts = []
    for feature_name in hook_features:
        tmp = behavior_by_hook_feature(posts_filtered, feature_name).rename(columns={feature_name: "has_feature"})
        tmp["feature"] = feature_name
        hook_feature_table_parts.append(tmp[["feature", "has_feature", "posts", "avg_engagement_rate", "avg_impressions", "avg_comments", "total_reposts"]])
    hook_feature_table = pd.concat(hook_feature_table_parts, ignore_index=True)
    hook_feature_table["avg_engagement_rate"] = hook_feature_table["avg_engagement_rate"].map(lambda x: f"{x*100:.2f}%")
    hook_feature_table["avg_impressions"] = hook_feature_table["avg_impressions"].map(lambda x: f"{x:.1f}")
    hook_feature_table["avg_comments"] = hook_feature_table["avg_comments"].map(lambda x: f"{x:.2f}")
    hook_feature_table["total_reposts"] = hook_feature_table["total_reposts"].map(lambda x: f"{int(round(x)):,}")

    demographics_full = demographics_data.copy()
    demographics_full["percentage"] = demographics_full["percentage"].map(lambda x: f"{x*100:.2f}%")

    weekly_kpis = compute_weekly_kpis(merged_filtered)
    weekly_kpis_table = weekly_kpis.copy()
    weekly_kpis_table["week_start"] = weekly_kpis_table["week_start"].dt.strftime("%Y-%m-%d")
    weekly_kpis_table["weekly_engagement_rate"] = weekly_kpis_table["weekly_engagement_rate"].map(lambda x: f"{x*100:.2f}%")
    weekly_kpis_table["avg_daily_impressions"] = weekly_kpis_table["avg_daily_impressions"].map(lambda x: f"{x:.1f}")
    weekly_kpis_table["avg_daily_engagements"] = weekly_kpis_table["avg_daily_engagements"].map(lambda x: f"{x:.2f}")
    weekly_kpis_table["avg_daily_new_followers"] = weekly_kpis_table["avg_daily_new_followers"].map(lambda x: f"{x:.2f}")

    st.markdown("**Weekly KPIs (merged_df):**")
    st.dataframe(weekly_kpis_table, use_container_width=True)

    guide_text = load_learning_content()
    scientific_prompt = build_scientific_prompt(
        guide_text=guide_text,
        profile_headline=profile_headline,
        profile_about=profile_about,
        posting_goal=posting_goal
    )

    period_text = f"{start_date.date()} → {end_date.date()}"
    markdown_report = build_markdown_report(
        kpis=kpis,
        insights=insights,
        top_posts=top_posts_report,
        hooks_table=hooks_table,
        hook_feature_table=hook_feature_table,
        demographics_full=demographics_full,
        weekly_kpis_table=weekly_kpis_table,
        scientific_prompt=scientific_prompt,
        period_text=period_text,
        profile_headline=profile_headline,
        profile_about=profile_about,
        posting_goal=posting_goal
    )

    st.text_area("Markdown report preview", markdown_report, height=420)
    st.download_button(
        "Download static report (.md)",
        data=markdown_report.encode("utf-8"),
        file_name="linkedin_deep_analytics_report.md",
        mime="text/markdown"
    )


with st.sidebar:
    page = st.radio("Navigation", ["About", "Analytics", "Learn", "Help"], index=0)

if page == "About":
    render_about_page()
elif page == "Analytics":
    render_analytics_page()
elif page == "Learn":
    render_learn_page()
else:
    render_help_page()
