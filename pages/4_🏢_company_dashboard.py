import streamlit as st
import pandas as pd
import plotly.express as px
import os
import json

# === Configuration ===
CONFIG_FILE = "config.json"
DEFAULT_CRITERIA_FILE = "criteria_config.csv"
CUSTOM_CRITERIA_FILE = "custom_criteria.csv"

# Load configuration
config = {"use_custom": False}
if os.path.exists(CONFIG_FILE):
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        config = json.load(f)

# Load criteria file based on config
if config.get("use_custom") and os.path.exists(CUSTOM_CRITERIA_FILE):
    criteria_df = pd.read_csv(CUSTOM_CRITERIA_FILE)
    st.info("🛠 Using custom criteria set from admin.")
elif os.path.exists(DEFAULT_CRITERIA_FILE):
    criteria_df = pd.read_csv(DEFAULT_CRITERIA_FILE)
    st.info("📌 Using default criteria set.")
else:
    st.error("❌ No criteria file found. Please upload `criteria_config.csv` or `custom_criteria.csv`.")
    st.stop()

# Load other data files
employee_df = pd.read_csv("employee_info.csv")
eval_df = pd.read_csv("evaluation_data.csv")
eval_df['evaluation_year'] = eval_df['evaluation_year'].astype(int)

# Sidebar navigation
st.sidebar.title("Navigation")
section = st.sidebar.radio("Go to", ["Criteria Dashboard", "Department Focus", "Trend Over Time"])

# Caption mapping (fallback to criteria name if no caption available)
caption_eng = criteria_df.set_index("criteria")["caption_eng"].to_dict()

# 1. Criteria Dashboard
if section == "Criteria Dashboard":
    st.subheader("📊 Criteria Dashboard (Company-Wide)")
    st.caption("> สรุปค่าเฉลี่ยตามเกณฑ์การประเมินทั่วทั้งบริษัท")

    available_years = sorted(eval_df["evaluation_year"].dropna().unique(), reverse=True)
    selected_year = st.selectbox("Select Evaluation Year / เลือกปีที่ประเมิน", available_years)

    criteria_groups = sorted(criteria_df["department"].unique())
    selected_group = st.selectbox("Select Criteria Group / เลือกกลุ่มเกณฑ์การประเมิน", criteria_groups)

    # Filter evaluation and criteria
    filtered_eval = eval_df[eval_df["evaluation_year"] == selected_year]
    group_criteria = criteria_df[criteria_df["department"] == selected_group]["criteria"].unique()
    filtered_eval = filtered_eval[filtered_eval["criteria"].isin(group_criteria)]

    # Calculate averages
    criteria_avg = filtered_eval.groupby('criteria')['score'].mean().reset_index()
    criteria_avg["score"] = criteria_avg["score"].round(2)
    criteria_avg["caption"] = criteria_avg["criteria"].map(caption_eng)
    criteria_avg = criteria_avg.sort_values(by="score", ascending=True)

    if criteria_avg.empty:
        st.warning("No data available for the selected group and year. / ไม่พบข้อมูลสำหรับกลุ่มและปีที่เลือก")
    else:
        top_row = criteria_avg.iloc[-1]
        bottom_row = criteria_avg.iloc[0]

        bar_fig = px.bar(
            criteria_avg,
            x='score',
            y='caption',
            orientation='h',
            title=f'Average Score by Criteria – {selected_group} ({selected_year})',
            color='score',
            color_continuous_scale='bluyl',
            labels={'score': 'Average Score', 'caption': 'Criteria'},
            height=500
        )
        st.plotly_chart(bar_fig, use_container_width=True)

        st.markdown(f"""
        ### Insights (สรุปข้อมูลเชิงลึก)
        💪 **Top Strength / จุดแข็ง:** {top_row['caption']} (Avg: {top_row['score']:.2f})  
        🛠️ **Area for Improvement / ควรปรับปรุง:** {bottom_row['caption']} (Avg: {bottom_row['score']:.2f})
        """)

# 2. Department Focus
elif section == "Department Focus":
    st.title("🏢 Department Focus")
    st.caption("> สรุปค่าเฉลี่ยผลการประเมินของแต่ละแผนกในแต่ละปีที่เลือก / เปรียบเทียบรายปี")
    
    departments = sorted(employee_df["department"].unique())
    selected_department = st.selectbox("Select Department / เลือกแผนก", departments)
    available_years = sorted(eval_df["evaluation_year"].unique(), reverse=True)
    selected_years = st.multiselect("Select Evaluation Year(s) / เลือกปีที่ประเมิน", available_years, default=available_years[:1])
    
    if not selected_years:
        st.warning("Please select at least one year. / โปรดเลือกอย่างน้อย 1 ปี")
    else:
        dept_emp_ids = employee_df[employee_df["department"] == selected_department]["employee_id"]
        dept_data = eval_df[(eval_df["employee_id"].isin(dept_emp_ids)) & (eval_df["evaluation_year"].isin(selected_years))]

        if dept_data.empty:
            st.warning("No evaluation data available for the selected department and years. / ไม่พบข้อมูลการประเมินสำหรับแผนกและปีที่เลือก")
        else:
            avg_scores = dept_data.groupby(["evaluation_year", "criteria"])["score"].mean().reset_index()
            avg_scores["score"] = avg_scores["score"].round(2)
            avg_scores["caption"] = avg_scores["criteria"].map(caption_eng)

            fig = px.line(
                avg_scores, x="caption", y="score", color="evaluation_year",
                title=f"Average Criteria Scores for {selected_department} Over Selected Years",
                labels={"score": "Average Score", "caption": "Criteria", "evaluation_year": "Year"}
            )
            st.plotly_chart(fig, use_container_width=True)

# 3. Trend Over Time
elif section == "Trend Over Time":
    st.subheader("📈 Trend Over Time by Criteria")
    st.caption("> แนวโน้มตามเกณฑ์และเวลา")

    available_criteria = sorted(eval_df["criteria"].unique())
    selected_criteria = st.multiselect("Select Criteria / เลือกเกณฑ์การประเมิน", available_criteria, default=available_criteria[:3])

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
            title="Average Score Trend Over Time by Criteria",
            labels={"evaluation_year": "Year", "score": "Average Score", "caption": "Criteria"}
        )
        fig.update_layout(xaxis=dict(dtick=1))
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Please select at least one criterion to view the trend. / โปรดเลือกอย่างน้อย 1 เกณฑ์")
