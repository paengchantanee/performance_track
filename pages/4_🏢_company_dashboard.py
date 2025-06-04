import streamlit as st
import pandas as pd
import plotly.express as px
import os
import json
import numpy as np

# Configuration
CONFIG_FILE = "config.json"
DEFAULT_CRITERIA_FILE = "criteria_config.csv"
CUSTOM_CRITERIA_FILE = "custom_criteria.csv"
EMPLOYEE_INFO_FILE = "employee_info.csv"

# Load configuration
config = {"use_custom": False}
if os.path.exists(CONFIG_FILE):
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        config = json.load(f)

use_custom = config.get("use_custom", False)

# Load criteria file based on config
if use_custom and os.path.exists(CUSTOM_CRITERIA_FILE):
    criteria_df = pd.read_csv(CUSTOM_CRITERIA_FILE)
    st.info("🛠 Using custom criteria set from admin.")
elif os.path.exists(DEFAULT_CRITERIA_FILE):
    criteria_df = pd.read_csv(DEFAULT_CRITERIA_FILE)
    st.info("📌 Using default criteria set.")
else:
    st.error("❌ No criteria file found. Please upload `criteria_config.csv` or `custom_criteria.csv`. / ไม่พบไฟล์ โปรดอัปโหลด `criteria_config.csv` หรือ `custom_criteria.csv`")
    st.stop()

# Filling defaults if missing
if 'type' not in criteria_df.columns:
    criteria_df['type'] = 'rating' # Default to 'rating'
if 'target_value' not in criteria_df.columns:
    criteria_df['target_value'] = np.nan 

# Load other data files
if os.path.exists(EMPLOYEE_INFO_FILE):
    employee_df = pd.read_csv(EMPLOYEE_INFO_FILE)
else:
    st.error(f"❌ Missing {EMPLOYEE_INFO_FILE}. Please upload it. / ไม่พบไฟล์ {EMPLOYEE_INFO_FILE} โปรดอัปโหลด")
    st.stop()

if os.path.exists("evaluation_data.csv"):
    eval_df = pd.read_csv("evaluation_data.csv")
else:
    st.error("❌ Missing evaluation_data.csv. Please upload it. / ไม่พบไฟล์ evaluation_data.csv โปรดอัปโหลด")
    st.stop()

eval_df['evaluation_year'] = eval_df['evaluation_year'].astype(int)
# Clean up whitespace and lower-case
eval_df["criteria"] = eval_df["criteria"].astype(str).str.strip()
eval_df["type"] = eval_df["type"].astype(str).str.strip().str.lower()
criteria_df["criteria"] = criteria_df["criteria"].astype(str).str.strip()
criteria_df["type"] = criteria_df["type"].astype(str).str.strip().str.lower()

# Merge eval_df with employee_df to get department information
merged_eval_df = pd.merge(eval_df, employee_df[['employee_id', 'department']], on='employee_id', how='left')

# Sidebar navigation
st.sidebar.title("Navigation")
section = st.sidebar.radio("Go to", ["Criteria Dashboard", "Department Focus", "Trend Over Time", "Progress Towards Goals", "Text Responses"])

# Caption mapping
caption_eng = criteria_df.set_index("criteria")["caption_eng"].to_dict()

# Create target_map from criteria_df
target_map = criteria_df.set_index("criteria")["target_value"].to_dict()

# --- Dashboard ---
# 1. Criteria Dashboard
if section == "Criteria Dashboard":
    st.subheader("📊 Criteria Dashboard (Company-Wide)")
    st.caption("> สรุปค่าเฉลี่ยตามเกณฑ์การประเมินทั่วทั้งบริษัท")

    # Filter for 'rating' criteria
    rating_criteria_for_dashboard = criteria_df[criteria_df["type"] == "rating"]["criteria"].unique()
    eval_df_for_dashboard = eval_df[eval_df["criteria"].isin(rating_criteria_for_dashboard)]

    available_years = sorted(eval_df_for_dashboard["evaluation_year"].dropna().unique(), reverse=True)
    selected_year = st.selectbox("Select Evaluation Year / เลือกปีที่ประเมิน", available_years)

    criteria_groups = sorted(criteria_df["department"].unique())
    selected_group = st.selectbox("Select Criteria Group / เลือกกลุ่มเกณฑ์การประเมิน", criteria_groups)

    filtered_eval = eval_df_for_dashboard[(eval_df_for_dashboard["evaluation_year"] == selected_year)]
    group_criteria = criteria_df[criteria_df["department"] == selected_group]["criteria"].unique()
    filtered_eval = filtered_eval[filtered_eval["criteria"].isin(group_criteria)]

    criteria_avg = filtered_eval.groupby('criteria')['score'].mean().reset_index()
    criteria_avg["score"] = criteria_avg["score"].round(2)
    criteria_avg = criteria_avg.sort_values(by="score", ascending=True)

    if criteria_avg.empty:
        st.warning("No data available for the selected group and year. / ไม่พบข้อมูลสำหรับแผนกและปีที่เลือก")
    else:
        bar_fig = px.bar(
            criteria_avg,
            x='score',
            y='criteria',
            orientation='h',
            title=f'Average Score by Criteria – {selected_group} ({selected_year})',
            color='score',
            color_continuous_scale='bluyl',
            labels={'score': 'Average Score', 'caption': 'Criteria'},
            height=500
        )
        st.plotly_chart(bar_fig, use_container_width=True)

# 2. Department Focus
elif section == "Department Focus":
    st.title("🏢 Department Focus")
    st.caption("> สรุปค่าเฉลี่ยผลการประเมินของแต่ละแผนกในแต่ละปีที่เลือก/ เปรียบเทียบรายปี")
    departments = sorted(employee_df["department"].unique())
    selected_department = st.selectbox("Select Department/ เลือกแผนก", departments)
    available_years = sorted(eval_df["evaluation_year"].unique(), reverse=True)
    selected_years = st.multiselect("Select Evaluation Year(s)/ เลือกปีที่ประเมิน (สามารถเลือกได้มากกว่า 1 ปี)", available_years, default=available_years[:1])

    if not selected_years:
        st.warning("Please select at least one year. / โปรดเลือกอย่างน้อย 1 ปี")
    else:
        # Filter for 'rating' criteria
        rating_criteria_for_dept = criteria_df[criteria_df["type"] == "rating"]["criteria"].unique()
        dept_data = merged_eval_df[(merged_eval_df["department"] == selected_department) &
                                   (merged_eval_df["evaluation_year"].isin(selected_years)) &
                                   (merged_eval_df["criteria"].isin(rating_criteria_for_dept))]

        if dept_data.empty:
            st.warning("No evaluation data for selected department and years./ ไม่พบข้อมูลสำหรับแผนกและปีที่เลือก")
        else:
            avg_scores = dept_data.groupby(["evaluation_year", "criteria"])["score"].mean().reset_index()
            avg_scores["score"] = avg_scores["score"].round(2)

            fig = px.line(
                avg_scores, x="criteria", y="score", color="evaluation_year",
                title=f"Average Scores for {selected_department}",
                labels={"score": "Average Score", "caption": "Criteria"}
            )
            st.plotly_chart(fig, use_container_width=True)

# 3. Trend over time
elif section == "Trend Over Time":
    st.subheader("📈 Trend Over Time by Criteria")
    st.caption("> แนวโน้มตามเกณฑ์และเวลา")

    # Filter for 'rating' criteria
    rating_criteria_for_trend = criteria_df[criteria_df["type"] == "rating"]["criteria"].unique()
    available_criteria = sorted(rating_criteria_for_trend)
    selected_criteria = st.multiselect("Select Criteria/ เลือกเกณฑ์การประเมิน", available_criteria, default=available_criteria[:3])

    if selected_criteria:
        trend_data = eval_df[eval_df["criteria"].isin(selected_criteria)]
        trend_summary = trend_data.groupby(["evaluation_year", "criteria"])["score"].mean().reset_index()
        trend_summary["score"] = trend_summary["score"].round(2)
        trend_summary["caption"] = trend_summary["criteria"].map(caption_eng)

        fig = px.line(
            trend_summary,
            x="evaluation_year",
            y="score",
            color="caption",
            markers=True,
            title="Average Score Trend",
            labels={"evaluation_year": "Year", "score": "Avg Score", "caption": "Criteria"}
        )
        fig.update_layout(xaxis=dict(dtick=1))
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Please select at least one criterion. / โปรดเลือกเกณฑ์อย่างน้อย 1 ข้อ")

# 4. Progress towards goals
elif section == "Progress Towards Goals":
    st.subheader("🎯 Progress Towards Goals")
    st.caption("> ความคืบหน้าสู่เป้าหมาย")

    # Filter for 'numeric' criteria
    numeric_criteria_df = criteria_df[criteria_df["type"] == "numeric"].copy()
    numeric_criteria_list = numeric_criteria_df["criteria"].unique()

    if not numeric_criteria_list.size:
        st.warning("No criteria of type 'numeric' found in the loaded criteria configuration. / ไม่พบเกณฑ์ประเภท 'ตัวเลข'")
        st.stop()

    available_years = sorted(merged_eval_df["evaluation_year"].dropna().unique(), reverse=True)
    selected_years_num = st.multiselect("Select Evaluation Year(s)/ เลือกปีที่ประเมิน (สามารถเลือกได้มากกว่า 1 ปี)", available_years, default=available_years)

    available_departments = sorted(merged_eval_df["department"].dropna().unique())
    selected_departments_num = st.multiselect("Select Department(s)/ เลือกแผนก", available_departments, default=available_departments)

    # Filter based on selected criteria, years, and departments
    filtered_numeric_data = merged_eval_df[
        (merged_eval_df["criteria"].isin(numeric_criteria_list)) &
        (merged_eval_df["evaluation_year"].isin(selected_years_num)) &
        (merged_eval_df["department"].isin(selected_departments_num))
    ].copy()

    if filtered_numeric_data.empty:
        st.info("No numeric data available for the selected filters. / ไม่พบข้อมูล")
    else:
        view_by_year = st.toggle("Display by Year/ แสดงผลแยกตามปี", value=True)

        for crit in numeric_criteria_list:
            display_name = caption_eng.get(crit, crit)
            st.markdown(f"**{display_name}**")

            # Get the target from numeric_criteria_df
            target_series = numeric_criteria_df[numeric_criteria_df["criteria"] == crit]["target_value"]
            
            if target_series.empty or pd.isna(target_series.iloc[0]):
                st.warning(f"Target value is missing or not a number. Cannot calculate progress. / ไม่สามารถคำนวณความคืบหน้าได้ เนื่องจากค่าเป้าหมายไม่ถูกต้องหรือไม่ระบุ")
                continue
            
            target = float(target_series.iloc[0])

            if target == 0:
                st.warning(f"Target value is zero. Cannot calculate progress. ไม่สามารถคำนวณความคืบหน้าได้ เนื่องจากค่าเป้าหมายมีค่าเป็นศูนย์")
                continue

            if view_by_year:
                # View by year
                years_in_data = sorted(filtered_numeric_data[filtered_numeric_data["criteria"] == crit]["evaluation_year"].unique())
                if not years_in_data:
                    st.info(f"No data in selected years/departments. / ไม่พบข้อมูลในปีและแผนกที่คุณเลือก")
                    continue

                for year in years_in_data:
                    year_data = filtered_numeric_data[
                        (filtered_numeric_data["criteria"] == crit) &
                        (filtered_numeric_data["evaluation_year"] == year)
                    ]
                    values = year_data["value"].dropna().astype(float)
                    
                    if not values.empty:
                        avg_val = values.mean()
                        progress_ratio = min(avg_val / target, 1.0) # Cap at 100%
                        st.progress(progress_ratio, text=f"**{year}**: {avg_val:.2f} / {target:.2f} ({progress_ratio:.0%})")
                    else:
                        st.info(f"No data in {year} with selected filters. / ไม่พบข้อมูลของปี {year}")
            else:
                # Aggregate view (all selected years and departments)
                values = filtered_numeric_data[filtered_numeric_data["criteria"] == crit]["value"].dropna().astype(float)
                if not values.empty:
                    avg_val = values.mean()
                    progress_ratio = min(avg_val / target, 1.0) # Cap at 100%
                    st.progress(progress_ratio, text=f"**Overall Average**: {avg_val:.2f} / {target:.2f} ({progress_ratio:.0%})")
                else:
                    st.info(f"No overall data with selected filters. / ไม่พบข้อมูลโดยรวมสำหรับตัวกรองที่เลือก")


# 5. Text responses
elif section == "Text Responses":
    st.subheader("💬 Text Responses by Year and Criteria")
    st.caption("> ความคิดเห็นจากผู้ประเมิน")
    
    # Filter for 'text'
    text_criteria_list = criteria_df[criteria_df["type"] == "text"]["criteria"].unique()
    
    if not text_criteria_list.size:
        st.info("No criteria of type 'text' found in the loaded configuration. / ไม่พบเกณฑ์ประเภท 'ข้อความ'")
        st.stop()

    # Get all available years
    available_text_years = sorted(eval_df[eval_df["criteria"].isin(text_criteria_list)]["evaluation_year"].dropna().unique(), reverse=True)

    if not available_text_years:
        st.info("No text response data available. / ไม่พบข้อมูลการตอบกลับที่เป็นข้อความ")
    else:
        # Year selector
        selected_text_year = st.selectbox("Select Evaluation Year/ เลือกปีที่ประเมิน", available_text_years)

        # Filter by selected year
        year_text_data = eval_df[
            (eval_df["evaluation_year"] == selected_text_year) & 
            (eval_df["criteria"].isin(text_criteria_list))
        ].copy()

        if year_text_data.empty:
            st.info(f"No text responses for {selected_text_year}. / ไม่พบข้อมูลสำหรับปี {selected_text_year}")
        else:
            # Group by criteria and display responses in expanders
            for crit in sorted(text_criteria_list):
                criteria_display_name = caption_eng.get(crit, crit)
                
                # Filter data for the current criterion and selected year
                criteria_text_data = year_text_data[year_text_data["criteria"] == crit]

                if not criteria_text_data.empty and criteria_text_data['text_response'].dropna().any():
                    with st.expander(f"**{criteria_display_name}**"):
                        for _, row in criteria_text_data.iterrows():
                            # Ensure text_response is not NaN before displaying
                            if pd.notna(row['text_response']):
                                st.markdown(f"- {row['text_response']}")
                            else:
                                st.markdown("- *No response provided.* / ยังไม่มีความคิดเห็นสำหรับรายการนี้")