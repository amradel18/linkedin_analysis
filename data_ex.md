# مخرجات البيانات (منظّمة فقط)

## 1) استخراج المنشورات: `posts`

### أمر التشغيل
```python
posts = extract_posts(r"posts_linkedin.txt")
```

### معاينة البيانات
posts=

|  | actual_date | content | hook | likes | comments | impressions | reposts | is_text | is_image | is_link | is_pdf | post_types | arabic_word_count | english_word_count | emoji_count |
|---:|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---:|---:|---:|
| 0 | 2025-03-17 | في العصر الحالي، Data Analysis وMachine Learni... | في العصر الحالي، Data Analysis وMachine Learni... | 0 | 0 | 173 | 0 | 1 | 1 | 0 | 0 | Text, Image | 114 | 23 | 0 |
| 1 | 2025-09-18 | 🚨 When 90% Accuracy Means Nothing in the Real ... | No alternative text description for this image | 0 | 0 | 231 | 0 | 1 | 1 | 1 | 0 | Text, Image, Link | 0 | 220 | 7 |

### معلومات الـ DataFrame
```text
<class 'pandas.core.frame.DataFrame'>
RangeIndex: 48 entries, 0 to 47
Data columns (total 15 columns):
 #   Column              Non-Null Count  Dtype 
---  ------              --------------  ----- 
 0   actual_date         48 non-null     object
 1   content             48 non-null     object
 2   hook                48 non-null     object
 3   likes               48 non-null     int64 
 4   comments            48 non-null     int64 
 5   impressions         48 non-null     int64 
 6   reposts             48 non-null     int64 
 7   is_text             48 non-null     int64 
 8   is_image            48 non-null     int64 
 9   is_link             48 non-null     int64 
 10  is_pdf              48 non-null     int64 
 11  post_types          48 non-null     object
 12  arabic_word_count   48 non-null     int64 
 13  english_word_count  48 non-null     int64 
 14  emoji_count         48 non-null     int64 
dtypes: int64(11), object(4)
memory usage: 5.8+ KB
```

## 2) قراءة وتنظيف إكسل: `merged_data` و `demographics_data`

### أمر التشغيل
```python
merged_data, demographics_data = read_and_clean_excel()
```

### `merged_data` (معاينة)
merged_data=

|  | date | impressions | engagements | new_followers |
|---:|---|---:|---:|---:|
| 1 | 2025-12-18 | 32.0 | 0.0 | 0 |
| 2 | 2025-12-19 | 3.0 | 0.0 | 4 |
| 3 | 2025-12-20 | 128.0 | 6.0 | 0 |
| 4 | 2025-12-21 | 83.0 | 2.0 | 9 |
| 5 | 2025-12-22 | 87.0 | 0.0 | 11 |

### `merged_data` (معلومات الـ DataFrame)
```text
<class 'pandas.core.frame.DataFrame'>
Index: 90 entries, 1 to 90
Data columns (total 4 columns):
 #   Column         Non-Null Count  Dtype         
---  ------         --------------  -----         
 0   date           90 non-null     datetime64[ns]
 1   impressions    90 non-null     float64       
 2   engagements    90 non-null     float64       
 3   new_followers  90 non-null     int64         
dtypes: datetime64[ns](1), float64(2), int64(1)
memory usage: 3.5 KB
```

### `demographics_data` (معاينة)
demographics_data = 

|  | category | value | percentage |
|---:|---|---|---:|
| 0 | Job titles | Data Analyst | 0.063508 |
| 1 | Job titles | Human Resources Specialist | 0.011425 |
| 2 | Job titles | Software Engineer | 0.010417 |
| 3 | Job titles | Economic Researcher | 0.010000 |
| 4 | Job titles | Data Engineer | 0.010000 |
| 5 | Locations | Cairo | 0.204301 |
| 6 | Locations | Giza | 0.084677 |
| 7 | Locations | Alexandria | 0.017473 |
| 8 | Locations | Qesm El Maadi | 0.010000 |
| 9 | Locations | Qesm Heliopolis | 0.010000 |
| 10 | Industries | Economic Programs | 0.065524 |
| 11 | Industries | Data Infrastructure and Analytics | 0.063844 |
| 12 | Industries | IT Services and IT Consulting | 0.060148 |
| 13 | Industries | Accounting | 0.058132 |
| 14 | Industries | Technology, Information and Internet | 0.056452 |
| 15 | Seniority | Senior | 0.305444 |
| 16 | Seniority | Entry | 0.284946 |
| 17 | Seniority | Training | 0.053091 |
| 18 | Seniority | Manager | 0.037298 |
| 19 | Seniority | Director | 0.021841 |
| 20 | Company size | 11-50 employees | 0.114583 |
| 21 | Company size | 51-200 employees | 0.109207 |
| 22 | Company size | 10,001+ employees | 0.106855 |
| 23 | Company size | 201-500 employees | 0.103831 |
| 24 | Company size | 1001-5000 employees | 0.095094 |
| 25 | Companies | CIB Egypt | 0.017809 |
| 26 | Companies | Digital Egypt Pioneers Initiative - DEPI | 0.014113 |
| 27 | Companies | Systems Limited - Egypt | 0.013777 |
| 28 | Companies | Banque Misr | 0.011761 |
| 29 | Companies | مركز المعلومات ودعم اتخاذ القرار بمجلس الوزراء... | 0.010417 |

### `demographics_data` (معلومات الـ DataFrame)
```text
<class 'pandas.core.frame.DataFrame'>
RangeIndex: 30 entries, 0 to 29
Data columns (total 3 columns):
 #   Column      Non-Null Count  Dtype  
---  ------      --------------  -----  
 0   category    30 non-null     object 
 1   value       30 non-null     object 
 2   percentage  30 non-null     float64
dtypes: float64(1), object(2)
memory usage: 852.0+ bytes
```

