from pathlib import Path
import tempfile
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from clean import extract_posts, read_and_clean_excel


st.set_page_config(page_title="LinkedIn Deep Analytics", page_icon="📊", layout="wide")

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
        avg_reposts=("reposts", "mean")
    )
    grouped[feature] = grouped[feature].map({0: "No", 1: "Yes"})
    return grouped


def compute_kpis(posts_df, merged_df):
    kpis = {
        "عدد المنشورات": len(posts_df),
        "إجمالي الظهور للمنشورات": posts_df["impressions"].sum(),
        "إجمالي التفاعلات": posts_df["engagement_actions"].sum(),
        "إجمالي اللايكات": posts_df["likes"].sum(),
        "إجمالي التعليقات": posts_df["comments"].sum(),
        "إجمالي إعادة النشر": posts_df["reposts"].sum(),
        "متوسط الظهور لكل منشور": posts_df["impressions"].mean(),
        "متوسط التفاعل لكل منشور": posts_df["engagement_actions"].mean(),
        "معدل التفاعل العام للمنشورات": posts_df["engagement_rate"].mean(),
        "معدل التعليقات العام": posts_df["comments_rate"].mean(),
        "معدل إعادة النشر العام": posts_df["reposts_rate"].mean(),
        "معدل اللايكات العام": posts_df["likes_rate"].mean(),
        "إجمالي الكلمات العربية": posts_df["arabic_word_count"].sum(),
        "إجمالي الكلمات الإنجليزية": posts_df["english_word_count"].sum(),
        "إجمالي الإيموجي": posts_df["emoji_count"].sum(),
        "متوسط طول الهوك": posts_df["hook_length"].mean(),
        "متوسط كلمات الهوك": posts_df["hook_word_count"].mean(),
        "نسبة الهوكات الاستفهامية": posts_df["hook_has_question"].mean(),
        "نسبة الهوكات الرقمية": posts_df["hook_has_number"].mean(),
        "نسبة الهوكات بالإيموجي": posts_df["hook_has_emoji"].mean(),
        "نسبة الهوكات بكلمات جذب": posts_df["hook_has_alert_word"].mean(),
        "إجمالي الظهور اليومي": merged_df["impressions"].sum(),
        "إجمالي التفاعل اليومي": merged_df["engagements"].sum(),
        "إجمالي المتابعين الجدد": merged_df["new_followers"].sum(),
        "متوسط معدل التفاعل اليومي": merged_df["daily_engagement_rate"].mean()
    }
    return kpis


def compute_weekly_change(merged_df):
    weekly = merged_df.copy()
    weekly["week_start"] = weekly["date"] - pd.to_timedelta(weekly["date"].dt.weekday, unit="D")
    weekly = weekly.groupby("week_start", as_index=False).agg(
        impressions=("impressions", "sum"),
        engagements=("engagements", "sum"),
        new_followers=("new_followers", "sum")
    )
    weekly["weekly_engagement_rate"] = weekly["engagements"].div(weekly["impressions"].replace(0, pd.NA)).fillna(0)
    for col in ["impressions", "engagements", "new_followers", "weekly_engagement_rate"]:
        weekly[f"{col}_wow_change"] = weekly[col].pct_change().fillna(0)
    return weekly.sort_values("week_start")


def generate_deep_insights(posts_df, merged_df, demographics_df):
    insights = []
    top_impression = posts_df.sort_values("impressions", ascending=False).iloc[0]
    top_engagement = posts_df.sort_values("engagement_rate", ascending=False).iloc[0]
    insights.append(f"أعلى وصول: منشور بتاريخ {top_impression['actual_date'].date()} وصل إلى {fmt_int(top_impression['impressions'])} ظهور.")
    insights.append(f"أعلى كفاءة تفاعل: منشور بتاريخ {top_engagement['actual_date'].date()} بمعدل {fmt_pct(top_engagement['engagement_rate'])}.")
    hook_q = posts_df.groupby("hook_has_question", as_index=False)["engagement_rate"].mean()
    if len(hook_q) == 2:
        yes = hook_q.loc[hook_q["hook_has_question"] == 1, "engagement_rate"].iloc[0]
        no = hook_q.loc[hook_q["hook_has_question"] == 0, "engagement_rate"].iloc[0]
        diff = yes - no
        insights.append(f"الهوك الاستفهامي يغيّر معدل التفاعل بمقدار {fmt_pct(diff)} مقارنة بغير الاستفهامي.")
    hook_num = posts_df.groupby("hook_has_number", as_index=False)["engagement_rate"].mean()
    if len(hook_num) == 2:
        yes = hook_num.loc[hook_num["hook_has_number"] == 1, "engagement_rate"].iloc[0]
        no = hook_num.loc[hook_num["hook_has_number"] == 0, "engagement_rate"].iloc[0]
        insights.append(f"الهوك الذي يحتوي أرقام يحقق {fmt_pct(yes)} مقابل {fmt_pct(no)} بدون أرقام.")
    lang_perf = posts_df.groupby(pd.cut(posts_df["arabic_ratio"], bins=[-0.01, 0.2, 0.6, 1], labels=["English-led", "Mixed", "Arabic-led"]))["engagement_rate"].mean()
    if not lang_perf.empty:
        best_bucket = lang_perf.sort_values(ascending=False).index[0]
        best_bucket_rate = lang_perf.sort_values(ascending=False).iloc[0]
        insights.append(f"أفضل نمط لغة حاليًا: {best_bucket} بمتوسط تفاعل {fmt_pct(best_bucket_rate)}.")
    best_day = merged_df.sort_values("impressions", ascending=False).iloc[0]
    insights.append(f"أعلى يوم وصول يوم {best_day['date'].date()} بظهور يومي {fmt_int(best_day['impressions'])}.")
    top_demo = demographics_df.sort_values("percentage", ascending=False).iloc[0]
    insights.append(f"الشريحة الأقوى حاليًا: {top_demo['category']} / {top_demo['value']} بنسبة {fmt_pct(top_demo['percentage'])}.")
    return insights


def build_markdown_report(
    kpis,
    insights,
    top_posts,
    raw_recent_posts,
    hook_feature_table,
    demographics_full,
    weekly_change_table,
    period_text,
    profile_headline,
    profile_about,
    posting_goal
):
    def df_to_md(df):
        if df.empty:
            return "| لا توجد بيانات |\n|---|"
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
    lines.append(f"**الفترة التحليلية:** {period_text}")
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
    lines.append("| KPI | Value | التعريف |")
    lines.append("|---|---:|---|")
    definitions = {
        "عدد المنشورات": "إجمالي عدد المنشورات في الفترة.",
        "إجمالي الظهور للمنشورات": "مجموع impressions في جدول المنشورات.",
        "إجمالي التفاعلات": "likes + comments + reposts.",
        "إجمالي اللايكات": "إجمالي likes لكل المنشورات.",
        "إجمالي التعليقات": "إجمالي comments لكل المنشورات.",
        "إجمالي إعادة النشر": "إجمالي reposts لكل المنشورات.",
        "متوسط الظهور لكل منشور": "متوسط impressions لكل منشور.",
        "متوسط التفاعل لكل منشور": "متوسط التفاعلات لكل منشور.",
        "معدل التفاعل العام للمنشورات": "متوسط (التفاعلات ÷ impressions).",
        "معدل التعليقات العام": "متوسط (comments ÷ impressions).",
        "معدل إعادة النشر العام": "متوسط (reposts ÷ impressions).",
        "معدل اللايكات العام": "متوسط (likes ÷ impressions).",
        "إجمالي الكلمات العربية": "مجموع arabic_word_count.",
        "إجمالي الكلمات الإنجليزية": "مجموع english_word_count.",
        "إجمالي الإيموجي": "مجموع emoji_count.",
        "متوسط طول الهوك": "متوسط عدد الأحرف داخل hook.",
        "متوسط كلمات الهوك": "متوسط عدد الكلمات داخل hook.",
        "نسبة الهوكات الاستفهامية": "نسبة hooks التي تحتوي ؟ أو ?.",
        "نسبة الهوكات الرقمية": "نسبة hooks التي تحتوي رقم.",
        "نسبة الهوكات بالإيموجي": "نسبة hooks التي تحتوي emoji.",
        "نسبة الهوكات بكلمات جذب": "نسبة hooks التي تحتوي كلمات جذب مثل why/how/سر/خطأ.",
        "إجمالي الظهور اليومي": "مجموع impressions من البيانات اليومية.",
        "إجمالي التفاعل اليومي": "مجموع engagements من البيانات اليومية.",
        "إجمالي المتابعين الجدد": "مجموع new_followers.",
        "متوسط معدل التفاعل اليومي": "متوسط (engagements ÷ impressions) يوميًا."
    }
    for kpi_name, value in kpis.items():
        if "نسبة" in kpi_name or "معدل" in kpi_name:
            value_text = fmt_pct(value)
        elif "متوسط" in kpi_name:
            value_text = fmt_float(value, 2)
        else:
            value_text = fmt_int(value)
        lines.append(f"| {kpi_name} | {value_text} | {definitions.get(kpi_name, '')} |")
    lines.append("")
    lines.append("## 2) Deep Insights")
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
    lines.append("## 5) Last 15 Raw Posts")
    lines.append("")
    lines.append(df_to_md(raw_recent_posts))
    lines.append("")
    lines.append("## 6) Full Demographics Table")
    lines.append("")
    lines.append(df_to_md(demographics_full))
    lines.append("")
    lines.append("## 7) Weekly Change Analytics (from merged_df)")
    lines.append("")
    lines.append(df_to_md(weekly_change_table))
    lines.append("")
    lines.append("## 8) LLM Advisor Prompt")
    lines.append("")
    lines.append("Use this prompt with any LLM as strategic advisor:")
    lines.append("")
    lines.append("```text")
    lines.append("You are my elite LinkedIn growth consultant and keyword researcher.")
    lines.append("Context:")
    lines.append(f"- Headline: {profile_headline}")
    lines.append(f"- About: {profile_about}")
    lines.append(f"- Publishing Goal: {posting_goal}")
    lines.append("- Use KPI table, insights, hook matrix, top posts, and demographics from this report.")
    lines.append("Tasks:")
    lines.append("1) Extract strongest content signals and diagnose growth bottlenecks.")
    lines.append("2) Build keyword strategy: short-tail, long-tail, semantic, intent-based.")
    lines.append("3) Recommend best profile keywords for headline/about based on niche and audience.")
    lines.append("4) Rewrite my Headline in 5 variants for different positioning angles.")
    lines.append("5) Rewrite my About in 3 versions: authority, storytelling, conversion.")
    lines.append("6) Propose 20 post keywords and 20 hook keywords ranked by priority.")
    lines.append("7) Create 14 post ideas mapped to funnel stages (awareness, trust, conversion).")
    lines.append("8) Build A/B tests for hook patterns: question, numbers, emoji, alert words, language mix.")
    lines.append("9) Recommend post structure templates with CTA by objective (reach, engagement, leads).")
    lines.append("10) Produce a 30-day execution plan with weekly KPI targets.")
    lines.append("Output format:")
    lines.append("- Executive summary")
    lines.append("- Priority actions table")
    lines.append("- Keyword library table")
    lines.append("- Profile optimization section")
    lines.append("- Content calendar section")
    lines.append("- Experiment roadmap")
    lines.append("```")
    lines.append("")
    return "\n".join(lines)


st.title("🚀 LinkedIn Deep Deep Analytics Dashboard")
st.caption("تحميل الملفات ثم تنظيف تلقائي وتحليل عميق لكل المؤشرات + تقرير ثابت Markdown")

with st.sidebar:
    st.subheader("رفع الملفات")
    uploaded_excel = st.file_uploader("ارفع ملف Content.xlsx", type=["xlsx"])
    uploaded_posts = st.file_uploader("ارفع ملف posts_linkedin.txt", type=["txt"])
    use_local = st.checkbox("استخدام الملفات المحلية الافتراضية إذا لم ترفع", value=True)
    st.subheader("بيانات البروفايل للسياق")
    profile_headline = st.text_input("LinkedIn Headline", value="")
    profile_about = st.text_area("LinkedIn About", value="", height=140)
    posting_goal = st.text_area("هدف النشر الحالي", value="", height=90)

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
    st.info("ارفع الملفين من الـ Sidebar أو فعّل استخدام الملفات المحلية.")
    st.stop()

posts, merged_data, demographics_data = load_data(posts_path, excel_path)
posts = posts.dropna(subset=["actual_date"]).copy()
merged_data = merged_data.dropna(subset=["date"]).copy()

if posts.empty or merged_data.empty:
    st.error("بعد التنظيف لا توجد بيانات كافية للتحليل.")
    st.stop()

min_date = min(posts["actual_date"].min().date(), merged_data["date"].min().date())
max_date = max(posts["actual_date"].max().date(), merged_data["date"].max().date())
date_range = st.slider("نطاق التاريخ", min_value=min_date, max_value=max_date, value=(min_date, max_date))
start_date = pd.to_datetime(date_range[0])
end_date = pd.to_datetime(date_range[1])

posts_filtered = posts[(posts["actual_date"] >= start_date) & (posts["actual_date"] <= end_date)].copy()
merged_filtered = merged_data[(merged_data["date"] >= start_date) & (merged_data["date"] <= end_date)].copy()
if posts_filtered.empty:
    st.warning("لا توجد منشورات داخل هذا النطاق، تم الرجوع لكل المنشورات.")
    posts_filtered = posts.copy()
if merged_filtered.empty:
    st.warning("لا توجد بيانات يومية داخل هذا النطاق، تم الرجوع لكل الأيام.")
    merged_filtered = merged_data.copy()

kpis = compute_kpis(posts_filtered, merged_filtered)

st.markdown('<div class="section-title">📌 KPIs الشاملة</div>', unsafe_allow_html=True)
kpi_items = [
    ("عدد المنشورات", fmt_int(kpis["عدد المنشورات"]), "حجم المحتوى"),
    ("إجمالي الظهور", fmt_int(kpis["إجمالي الظهور للمنشورات"]), "Reach"),
    ("إجمالي التفاعلات", fmt_int(kpis["إجمالي التفاعلات"]), "Likes + Comments + Reposts"),
    ("معدل التفاعل", fmt_pct(kpis["معدل التفاعل العام للمنشورات"]), "Engagement / Impression"),
    ("إجمالي اللايكات", fmt_int(kpis["إجمالي اللايكات"]), "إشارات التفضيل"),
    ("إجمالي التعليقات", fmt_int(kpis["إجمالي التعليقات"]), "عمق النقاش"),
    ("إجمالي إعادة النشر", fmt_int(kpis["إجمالي إعادة النشر"]), "قابلية الانتشار"),
    ("معدل التعليقات", fmt_pct(kpis["معدل التعليقات العام"]), "Comments / Impression"),
    ("كلمات عربية", fmt_int(kpis["إجمالي الكلمات العربية"]), "Arabic Word Footprint"),
    ("كلمات إنجليزية", fmt_int(kpis["إجمالي الكلمات الإنجليزية"]), "English Word Footprint"),
    ("إيموجي", fmt_int(kpis["إجمالي الإيموجي"]), "Expressive Symbols"),
    ("متوسط طول الهوك", fmt_float(kpis["متوسط طول الهوك"], 1), "Characters")
]
for i in range(0, len(kpi_items), 4):
    cols = st.columns(4)
    for col, item in zip(cols, kpi_items[i:i+4]):
        with col:
            create_kpi_card(item[0], item[1], item[2])

st.markdown('<div class="section-title">📈 Deep Visual Analytics</div>', unsafe_allow_html=True)
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
    title="السلوك اليومي: الظهور، التفاعل، المتابعون",
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
    title="أفضل المنشورات وصولًا (مع تدرج الكفاءة)",
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
    reposts=("reposts", "mean")
)
fig_type_perf = px.bar(
    type_performance.sort_values("engagement_rate", ascending=False),
    x="post_type",
    y="engagement_rate",
    color="comments",
    text=type_performance.sort_values("engagement_rate", ascending=False)["engagement_rate"].map(lambda x: f"{x*100:.2f}%"),
    title="كفاءة كل نوع محتوى",
    template="plotly_white"
)
fig_type_perf.update_traces(textposition="outside")
with col3:
    st.plotly_chart(fig_type_perf, use_container_width=True)

corr_columns = ["impressions", "likes", "comments", "reposts", "arabic_word_count", "english_word_count", "emoji_count", "hook_length", "hook_word_count", "engagement_rate"]
corr_df = posts_filtered[corr_columns].corr(numeric_only=True).round(2)
fig_corr = px.imshow(corr_df, text_auto=True, color_continuous_scale="RdBu", zmin=-1, zmax=1, title="مصفوفة الترابط بين المتغيرات")
with col4:
    st.plotly_chart(fig_corr, use_container_width=True)

st.markdown('<div class="section-title">🎯 Hook Analytics</div>', unsafe_allow_html=True)
col5, col6 = st.columns(2)

hook_features = ["hook_has_question", "hook_has_number", "hook_has_emoji", "hook_has_alert_word"]
selected_hook_feature = st.selectbox("اختر خاصية Hook للمقارنة", options=hook_features)
hook_behavior = behavior_by_hook_feature(posts_filtered, selected_hook_feature)
fig_hook = px.bar(
    hook_behavior,
    x=selected_hook_feature,
    y="avg_engagement_rate",
    color="avg_impressions",
    text=hook_behavior["avg_engagement_rate"].map(lambda x: f"{x*100:.2f}%"),
    title=f"أثر {selected_hook_feature} على التفاعل",
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
    title="أثر طول Hook على الكفاءة والوصول",
    template="plotly_white"
)
with col6:
    st.plotly_chart(fig_hook_len, use_container_width=True)

st.markdown('<div class="section-title">🔬 Text & Language Analytics</div>', unsafe_allow_html=True)
col7, col8 = st.columns(2)

lang_mix = posts_filtered.copy()
lang_mix["language_bucket"] = pd.cut(lang_mix["arabic_ratio"], bins=[-0.01, 0.2, 0.6, 1], labels=["English-led", "Mixed", "Arabic-led"])
lang_perf = lang_mix.groupby("language_bucket", as_index=False).agg(
    posts=("language_bucket", "size"),
    avg_engagement_rate=("engagement_rate", "mean"),
    avg_comments=("comments", "mean"),
    avg_reposts=("reposts", "mean")
)
fig_lang = px.bar(
    lang_perf,
    x="language_bucket",
    y="avg_engagement_rate",
    color="avg_comments",
    text=lang_perf["avg_engagement_rate"].map(lambda x: f"{x*100:.2f}%"),
    title="أداء نمط اللغة",
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
    title="تأثير كثافة الإيموجي على معدل التفاعل",
    template="plotly_white"
)
with col8:
    st.plotly_chart(fig_emoji, use_container_width=True)

insights = generate_deep_insights(posts_filtered, merged_filtered, demographics_data)
for insight in insights:
    st.markdown(f'<div class="insight-box">• {insight}</div>', unsafe_allow_html=True)

st.markdown('<div class="section-title">🧾 التقرير الثابت (Markdown)</div>', unsafe_allow_html=True)

with st.expander("سياق البروفايل المستخدم في التقرير"):
    st.write("**Headline:**", profile_headline if profile_headline.strip() else "Not provided")
    st.write("**About:**")
    st.write(profile_about if profile_about.strip() else "Not provided")
    st.write("**Goal:**", posting_goal if posting_goal.strip() else "Not provided")

top_posts_report = posts_filtered.sort_values("engagement_rate", ascending=False).head(10)[
    ["actual_date", "hook", "impressions", "likes", "comments", "reposts", "engagement_rate", "arabic_word_count", "english_word_count", "emoji_count"]
].copy()
top_posts_report["actual_date"] = top_posts_report["actual_date"].dt.strftime("%Y-%m-%d")
top_posts_report["engagement_rate"] = top_posts_report["engagement_rate"].map(lambda x: f"{x*100:.2f}%")

raw_recent_posts = posts_filtered.sort_values("actual_date", ascending=False).head(15)[
    ["actual_date", "content", "hook", "post_types", "impressions", "likes", "comments", "reposts", "arabic_word_count", "english_word_count", "emoji_count"]
].copy()
raw_recent_posts["actual_date"] = raw_recent_posts["actual_date"].dt.strftime("%Y-%m-%d")

hook_feature_table_parts = []
for feature_name in hook_features:
    tmp = behavior_by_hook_feature(posts_filtered, feature_name).rename(columns={feature_name: "has_feature"})
    tmp["feature"] = feature_name
    hook_feature_table_parts.append(tmp[["feature", "has_feature", "posts", "avg_engagement_rate", "avg_impressions", "avg_comments", "avg_reposts"]])
hook_feature_table = pd.concat(hook_feature_table_parts, ignore_index=True)
hook_feature_table["avg_engagement_rate"] = hook_feature_table["avg_engagement_rate"].map(lambda x: f"{x*100:.2f}%")
hook_feature_table["avg_impressions"] = hook_feature_table["avg_impressions"].map(lambda x: f"{x:.1f}")
hook_feature_table["avg_comments"] = hook_feature_table["avg_comments"].map(lambda x: f"{x:.2f}")
hook_feature_table["avg_reposts"] = hook_feature_table["avg_reposts"].map(lambda x: f"{x:.2f}")

demographics_full = demographics_data.copy()
demographics_full["percentage"] = demographics_full["percentage"].map(lambda x: f"{x*100:.2f}%")

weekly_change = compute_weekly_change(merged_filtered)
weekly_change_table = weekly_change.copy()
weekly_change_table["week_start"] = weekly_change_table["week_start"].dt.strftime("%Y-%m-%d")
weekly_change_table["weekly_engagement_rate"] = weekly_change_table["weekly_engagement_rate"].map(lambda x: f"{x*100:.2f}%")
for col in ["impressions_wow_change", "engagements_wow_change", "new_followers_wow_change", "weekly_engagement_rate_wow_change"]:
    weekly_change_table[col] = weekly_change_table[col].map(lambda x: f"{x*100:.2f}%")

st.markdown("**Weekly change stats (merged_df):**")
st.dataframe(weekly_change_table, use_container_width=True)

period_text = f"{start_date.date()} → {end_date.date()}"
markdown_report = build_markdown_report(
    kpis=kpis,
    insights=insights,
    top_posts=top_posts_report,
    raw_recent_posts=raw_recent_posts,
    hook_feature_table=hook_feature_table,
    demographics_full=demographics_full,
    weekly_change_table=weekly_change_table,
    period_text=period_text,
    profile_headline=profile_headline,
    profile_about=profile_about,
    posting_goal=posting_goal
)

st.text_area("معاينة التقرير Markdown", markdown_report, height=420)
st.download_button(
    "📥 تنزيل التقرير الثابت بصيغة .md",
    data=markdown_report.encode("utf-8"),
    file_name="linkedin_deep_analytics_report.md",
    mime="text/markdown"
)
