import pandas as pd
import re
from datetime import datetime, timedelta

def parse_time_posted(time_str: str):
    """Convert LinkedIn relative time string into a date object."""
    try:
        now = datetime.now().date()
        if "yr" in time_str:
            years = int(re.search(r"(\d+)yr", time_str).group(1))
            return now - timedelta(days=years*365)
        elif "mo" in time_str:
            months = int(re.search(r"(\d+)mo", time_str).group(1))
            return now - timedelta(days=months*30)
        elif "w" in time_str:
            weeks = int(re.search(r"(\d+)w", time_str).group(1))
            return now - timedelta(weeks=weeks)
        elif "d" in time_str:
            days = int(re.search(r"(\d+)d", time_str).group(1))
            return now - timedelta(days=days)
        elif "h" in time_str:
            hours = int(re.search(r"(\d+)h", time_str).group(1))
            return (datetime.now() - timedelta(hours=hours)).date()
        else:
            return pd.NaT
    except Exception as e:
        print(f"[Warning] Failed to parse time string '{time_str}': {e}")
        return pd.NaT

def count_words_and_emojis(content: str):
    """Count Arabic words, English words, and emojis in text."""
    if not content:
        return 0, 0, 0
    arabic_words = re.findall(r'[\u0600-\u06FF]+', content)
    english_words = re.findall(r'[A-Za-z]+', content)
    emojis = re.findall(
        r'[\U0001F600-\U0001F64F]|[\U0001F300-\U0001F5FF]|[\U0001F680-\U0001F6FF]|[\U0001F900-\U0001F9FF]',
        content
    )
    return len(arabic_words), len(english_words), len(emojis)

def extract_posts(file_path: str) -> pd.DataFrame:
    """Extract LinkedIn posts from a text file into a clean DataFrame."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read()
    except Exception as e:
        raise RuntimeError(f"Error reading file: {e}")

    posts = re.findall(r"(posted this.*?View analytics)", text, re.DOTALL)
    data = []

    for idx, post in enumerate(posts, start=1):
        try:
            time_match = re.search(r"posted this • (.*?)\n", post)
            time_posted = time_match.group(1).strip() if time_match else None
            actual_date = parse_time_posted(time_posted) if time_posted else pd.NaT

            # ✅ content = السطر المكتوب مباشرة بعد posted this •
            lines = post.splitlines()
            content = None
            hook = None
            for i, line in enumerate(lines):
                if "posted this •" in line:
                    if i+1 < len(lines):
                        content = lines[i+1].strip()
                    # hook = السطر التالي بعد الـ content (لو فاضي ناخد اللي بعده)
                    if i+2 < len(lines):
                        hook = lines[i+2].strip()
                        if not hook and i+3 < len(lines):
                            hook = lines[i+3].strip()
                    break

            likes_match = re.search(r"(?:like|celebrate|love|lovelike|likecelebrate)\s+(\d+)", post)
            likes = int(likes_match.group(1)) if likes_match else 0

            comments_match = re.search(r"(\d+)\s+comment", post)
            comments = int(comments_match.group(1)) if comments_match else 0

            impressions_match = re.search(r"([\d,]+)\s+Impressions", post)
            impressions = int(impressions_match.group(1).replace(",", "")) if impressions_match else 0

            # ✅ استخراج عدد الـ reposts
            reposts_match = re.search(r"(\d+)\s+repost", post, re.IGNORECASE)
            reposts = int(reposts_match.group(1)) if reposts_match else 0

            # Detect types
            is_text = 1 if content else 0
            is_pdf = 1 if re.search(r"\d+\s+pages", post, re.IGNORECASE) else 0
            is_link = 1 if re.search(r"http[s]?://", post) else 0
            is_image = 1 if not is_pdf else 0  # assume image if not PDF

            types_list = []
            if is_text: types_list.append("Text")
            if is_image: types_list.append("Image")
            if is_link: types_list.append("Link")
            if is_pdf: types_list.append("PDF")
            post_types = ", ".join(types_list) if types_list else "Unknown"

            # Count Arabic, English words, and emojis
            arabic_count, english_count, emoji_count = count_words_and_emojis(content)

            data.append({
                "actual_date": actual_date,
                "content": content,
                "hook": hook,
                "likes": likes,
                "comments": comments,
                "impressions": impressions,
                "reposts": reposts,
                "is_text": is_text,
                "is_image": is_image,
                "is_link": is_link,
                "is_pdf": is_pdf,
                "post_types": post_types,
                "arabic_word_count": arabic_count,
                "english_word_count": english_count,
                "emoji_count": emoji_count
            })

        except Exception as e:
            print(f"[Error] Skipped post {idx} due to parsing issue: {e}")
            continue

    df = pd.DataFrame(data)
    df = df.drop_duplicates(subset=["content"]).reset_index(drop=True)
    posts = df.sort_values("actual_date", ascending=True,ignore_index=True)
    return posts

def read_and_clean_excel(file_path=r"Content_2025-12-18_2026-03-17_AmrAdel.xlsx"):
    # قراءة الشيتات
    DISCOVERY = pd.read_excel(file_path, sheet_name="DISCOVERY").dropna(how="all").dropna(axis=1, how="all")
    ENGAGEMENT = pd.read_excel(file_path, sheet_name="ENGAGEMENT").dropna(how="all").dropna(axis=1, how="all")
    FOLLOWERS = pd.read_excel(file_path, sheet_name="FOLLOWERS").dropna(how="all").dropna(axis=1, how="all")
    DEMOGRAPHICS = pd.read_excel(file_path, sheet_name="DEMOGRAPHICS").dropna(how="all").dropna(axis=1, how="all")

    # تنظيف الأعمدة
    ENGAGEMENT.columns = ENGAGEMENT.columns.str.strip().str.lower()
    FOLLOWERS.columns = FOLLOWERS.columns.astype(str).str.strip().str.lower()
    DEMOGRAPHICS.columns = DEMOGRAPHICS.columns.str.strip().str.lower()

    # تجهيز جدول المتابعين (تجاهل الصف الأول اللي فيه الإجمالي)
    followers_clean = FOLLOWERS[FOLLOWERS.columns[:2]].copy()
    followers_clean.columns = ["date","new_followers"]
    followers_clean["date"] = pd.to_datetime(followers_clean["date"], errors="coerce")

    # تجهيز جدول التفاعل
    engagement_clean = ENGAGEMENT.rename(columns={"date":"date","impressions":"impressions","engagements":"engagements"})
    engagement_clean["date"] = pd.to_datetime(engagement_clean["date"], errors="coerce")

    # دمج الاتنين على أساس التاريخ
    merged = pd.merge(engagement_clean, followers_clean, on="date", how="outer")
    merged.dropna(inplace=True)

    # تحويل الأعمدة الرقمية
    merged["impressions"] = pd.to_numeric(merged["impressions"], errors="coerce")
    merged["engagements"] = pd.to_numeric(merged["engagements"], errors="coerce")
    merged["new_followers"] = pd.to_numeric(merged["new_followers"], errors="coerce")

    # تنظيف الديموجرافيكس
    demographics_clean = DEMOGRAPHICS.rename(columns={"top demographics":"category","value":"value","percentage":"percentage"})
    demographics_clean.dropna(inplace=True)

    # تحويل percentage إلى أرقام (مع معالجة < 1%)
    def convert_percentage(x):
        if isinstance(x, str):
            x = x.strip()
            if x.startswith("<"):
                return 0.01   # أقل من 1% نحولها إلى 0.01
            try:
                return float(x)
            except:
                return None
        return x

    demographics_clean["percentage"] = demographics_clean["percentage"].apply(convert_percentage)
    demographics_clean["percentage"] = pd.to_numeric(demographics_clean["percentage"], errors="coerce")

    # تنظيف النصوص
    demographics_clean["category"] = demographics_clean["category"].str.strip()
    demographics_clean["value"] = demographics_clean["value"].str.strip()

    return merged, demographics_clean

