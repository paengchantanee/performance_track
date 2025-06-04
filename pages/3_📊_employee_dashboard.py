import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
import json

# Load configuration to check if custom criteria is enabled
CONFIG_FILE = "config.json"
DEFAULT_CRITERIA_FILE = "criteria_config.csv"
CUSTOM_CRITERIA_FILE = "custom_criteria.csv"

# Fallback config
config = {"use_custom": False}
if os.path.exists(CONFIG_FILE):
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        config = json.load(f)

use_custom = config.get("use_custom", False)

# Load criteria file
if use_custom and os.path.exists(CUSTOM_CRITERIA_FILE):
    criteria_df = pd.read_csv(CUSTOM_CRITERIA_FILE)
    st.info("🛠 Using custom criteria set from admin.")
elif os.path.exists(DEFAULT_CRITERIA_FILE):
    criteria_df = pd.read_csv(DEFAULT_CRITERIA_FILE)
    st.info("📌 Using default criteria set.")
else:
    st.error("❌ No criteria file found. Please upload `criteria_config.csv` or `custom_criteria.csv`. / ไม่พบไฟล์ โปรดอัปโหลด `criteria_config.csv` หรือ `custom_criteria.csv`")
    st.stop()

# Load data
employee_df = pd.read_csv("employee_info.csv")
eval_df = pd.read_csv("evaluation_data.csv")

# Title
st.title("📊 Employee Evaluation Dashboard")
st.write("- Individual insights across competencies")
st.caption("- สรุปผลการประเมินเชิงลึกของแต่ละพนักงาน")

# Select year(s)
available_years = sorted(eval_df["evaluation_year"].dropna().unique(), reverse=True)

if available_years:
    selected_years = st.multiselect(
        "Select Evaluation Year(s) / เลือกปี (สามารถเลือกได้มากกว่า 1 ปี)",
        available_years,
        default=[available_years[0]]
    )
else:
    st.warning("⚠️ No evaluation data available. Please fill the form first. / ยังไม่มีข้อมูลการประเมิน โปรดทำแบบประเมินก่อน")
    st.stop()

# Filter by selected year
eval_selected = eval_df[eval_df["evaluation_year"].isin(selected_years)]

# Select department and employee
departments = sorted(employee_df["department"].unique())
selected_department = st.selectbox("Select department / เลือกแผนก", departments)

filtered_employees = employee_df[employee_df["department"] == selected_department]
employee_names = filtered_employees["name"].tolist()
employee_selected = st.selectbox("Select employee / เลือกพนักงาน", employee_names)

# Get employee info
emp_row = filtered_employees[filtered_employees["name"] == employee_selected].iloc[0]
emp_id = emp_row["employee_id"]
emp_dept = emp_row["department"]

# Filter by selected employee
emp_eval = eval_selected[eval_selected["employee_id"] == emp_id]

if emp_eval.empty:
    st.warning("No evaluations found for this employee in the selected year(s). / ไม่พบข้อมูลการประเมินของพนักงานคนนี้ในปีที่คุณเลือก")
    st.stop()

# Merge captions and define criteria by type
core_criteria = criteria_df[criteria_df["department"] == "Core"]
dept_criteria = criteria_df[criteria_df["department"] == emp_dept]
all_criteria_df = pd.concat([core_criteria, dept_criteria])

if use_custom:
    type_map = all_criteria_df.set_index("criteria")["type"].to_dict() if "type" in all_criteria_df.columns else {}
    target_map = all_criteria_df.set_index("criteria")["target_value"].to_dict() if "target_value" in all_criteria_df.columns else {}
    rating_criteria = [c for c, t in type_map.items() if t == "rating"]
    numeric_criteria = [c for c, t in type_map.items() if t == "numeric"]
    text_criteria = [c for c, t in type_map.items() if t == "text"]
else:
    # In default mode, only use available criteria
    rating_criteria = all_criteria_df["criteria"].unique().tolist()
    numeric_criteria = []
    text_criteria = []
    type_map = {}
    target_map = {}

caption_eng = all_criteria_df.set_index("criteria")["caption_eng"].to_dict()
caption_th = all_criteria_df.set_index("criteria")["caption_th"].to_dict()

st.write("___")

# 1. Number of Evaluators
num_evaluators = emp_eval["evaluator_id"].nunique()
st.metric("👥 Number of Evaluator / จำนวนคนประเมิน", num_evaluators)

# 2. Bar Chart of Average Scores
st.subheader("🔹 Average Scores by Criteria / Yearly Comparison")
st.caption("> คะแนนเฉลี่ยตามเกณฑ์ / เปรียบเทียบรายปี")

avg_scores = emp_eval.groupby(["evaluation_year", "criteria"])["score"].mean().reset_index()
avg_scores = avg_scores[avg_scores["criteria"].isin(rating_criteria)]

if len(selected_years) > 1:
    bar = px.bar(
        avg_scores,
        x="score",
        y="criteria",
        color="evaluation_year",
        barmode="group",
        orientation="h",
        title="Criteria Score Comparison Across Years",
        labels={"score": "Avg Score", "criteria": "Criteria"},
        height=500
    )
else:
    bar = px.bar(
        avg_scores.sort_values("score"),
        x="score",
        y="criteria",
        orientation="h",
        title="Average Scores by Criteria",
        labels={"score": "Avg Score", "criteria": "Criteria"},
        color="score",
        color_continuous_scale="blues",
        height=500
    )

st.plotly_chart(bar, use_container_width=True)

# 3. Radar Chart
if rating_criteria:
    st.subheader("🔹 Radar Chart")
    st.caption("> แผนภูมิเรดาร์")
    radar_avg = avg_scores.groupby("criteria")["score"].mean().reindex(rating_criteria).reset_index()
    radar_avg = pd.concat([radar_avg, radar_avg.iloc[[0]]])

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=radar_avg["score"],
        theta=radar_avg["criteria"],
        fill='toself',
        name=employee_selected
    ))
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[1, 5])),
        showlegend=False
    )
    st.plotly_chart(fig, use_container_width=True)

# 4. Strengths & Opportunities
st.subheader("✨ Strengths and Opportunities")
latest_avg = avg_scores.groupby("criteria")["score"].mean().reset_index()
latest_avg = latest_avg.sort_values("score", ascending=True)

col1, col2 = st.columns(2)
with col1:
    st.markdown("**Top Strengths / จุดแข็ง**")
    for _, row in latest_avg.sort_values("score", ascending=False).head(3).iterrows():
        st.write(f"- {row['criteria']} ({row['score']:.2f})")
with col2:
    st.markdown("**Improvement Opportunities / ควรปรับปรุง**")
    for _, row in latest_avg.head(3).iterrows():
        st.write(f"- {row['criteria']} ({row['score']:.2f})")

# 5. Evaluator Breakdown
st.subheader("🔸 Self vs Others Comparison")
st.caption("> ตนเอง vs. ผู้อื่น")

self_scores = emp_eval[emp_eval["evaluator_type"] == "Self / ตัวเอง"]
others_scores = emp_eval[emp_eval["evaluator_type"] != "Self / ตัวเอง"]

self_avg = self_scores.groupby("criteria")["score"].mean().rename("Self")
others_avg = others_scores.groupby("criteria")["score"].mean().rename("Others")

comparison_df = pd.concat([self_avg, others_avg], axis=1).reindex(rating_criteria).reset_index()
comparison_df = comparison_df.round(2)

colors = ["crimson" if row["Self"] > row["Others"] else "royalblue" for _, row in comparison_df.iterrows()]

fig = go.Figure()
fig.add_trace(go.Bar(
    x=comparison_df["criteria"],
    y=comparison_df["Self"],
    name="Self",
    marker_color="lightgray"
))
fig.add_trace(go.Bar(
    x=comparison_df["criteria"],
    y=comparison_df["Others"],
    name="Others",
    marker_color=colors
))
fig.update_layout(
    barmode='group',
    title="Self vs Others",
    xaxis_title="Criteria",
    yaxis_title="Score",
    height=400
)
st.plotly_chart(fig, use_container_width=True)

# 6. Trend Over Time
st.subheader("📈 Trend Over Time")
st.caption("> แนวโน้มรายปี")

all_emp_eval = eval_df[eval_df["employee_id"] == emp_id]
all_emp_eval = all_emp_eval[all_emp_eval["criteria"].isin(rating_criteria)]
criteria_options = all_emp_eval["criteria"].unique()

if len(criteria_options) > 0:
    selected_criterion = st.selectbox("Select a criterion to view trend / เลือกเกณฑ์ต้องการจะดู", criteria_options)

    trend = all_emp_eval[all_emp_eval["criteria"] == selected_criterion]
    trend = trend.groupby("evaluation_year")["score"].mean().reset_index()
    trend["evaluation_year"] = trend["evaluation_year"].astype(str)

    fig = px.line(
        trend,
        x="evaluation_year",
        y="score",
        markers=True,
        title=f"Trend Over Time: {selected_criterion}",
        labels={"evaluation_year": "Year", "score": "Avg Score"},
        height=400
    )
    fig.update_layout(
        yaxis_range=[1, 5],
        xaxis_type="category"
    )
    st.plotly_chart(fig, use_container_width=True)

# 7. Summary Table
st.subheader("📋 Summary Table")
st.caption("> ตารางสรุป")
table = latest_avg.copy()
table["Description"] = table["criteria"].map(caption_eng)
table["คำอธิบาย"] = table["criteria"].map(caption_th)
table.columns = ["Criteria", "Avg Score", "Description", "คำอธิบาย"]
table["Avg Score"] = table["Avg Score"].round(2)
table.index = range(1, len(table) + 1)
st.dataframe(table, use_container_width=True)

# 8. Progress Towards Goals (custom only)
if use_custom:
    numeric_criteria = [c for c, t in type_map.items() if t == "numeric"]
    numeric_data = emp_eval[emp_eval["criteria"].isin(numeric_criteria)]

    if not numeric_criteria or numeric_data.empty:
        pass
    else:
        st.subheader("🎯  Progress Towards Goals")
        st.caption("> ความคืบหน้าสู่เป้าหมาย")

        # Add toggle to switch between modes
        view_by_year = st.toggle("Display by Year/ แสดงผลแยกตามปี", value=True)

        for crit in numeric_criteria:
            st.markdown(f"**{crit}**")
            cap_eng = caption_eng.get(crit, crit)
            cap_th = caption_th.get(crit, crit)
            st.write(cap_eng)
            st.caption(cap_th)
            target = float(target_map.get(crit, 0))

            if view_by_year:
                # View by year
                for year in sorted(numeric_data["evaluation_year"].unique()):
                    year_data = numeric_data[(numeric_data["criteria"] == crit) & (numeric_data["evaluation_year"] == year)]
                    values = year_data["value"].dropna().astype(float)
                    if not values.empty:
                        avg_val = values.mean()
                        progress_ratio = min(avg_val / target, 1.0) if target > 0 else 0.0
                        percent = progress_ratio * 100
                        st.progress(progress_ratio, text=f"{year}: {avg_val:.2f} / {target:.2f} ({percent:.1f}%)")
                    else:
                        st.info(f"No data for '{crit}' in {year}. / ไม่พบข้อมูล")
            else:
                # Aggregate view (all years)
                values = numeric_data[numeric_data["criteria"] == crit]["value"].dropna().astype(float)
                if not values.empty:
                    avg_val = values.mean()
                    progress_ratio = min(avg_val / target, 1.0) if target > 0 else 0.0
                    percent = progress_ratio * 100
                    st.progress(progress_ratio, text=f"Average: {avg_val:.2f} / {target:.2f} ({percent:.1f}%)")
                else:
                    st.info(f"No overall data for '{crit}'. / ไม่พบข้อมูล")

# 9. Text Responses (custom only)
if use_custom:
    text_criteria = [c for c, t in type_map.items() if t == "text"]
    text_data = emp_eval[emp_eval["criteria"].isin(text_criteria)]

    if not text_criteria or text_data.empty:
        st.info("No text responses found for this employee in the selected year(s). / ไม่พบข้อมูลสำหรับพนักงานคนนี้ในปีที่คุณเลือก")
    else:
        st.subheader("💬 Text Responses")
        st.caption("> ความคิดเห็นจากผู้ประเมิน")

        # Get unique criteria that have text data for the selected employee and years
        criteria_with_text_data = sorted(text_data["criteria"].unique())

        if not criteria_with_text_data:
            st.info("No text responses available for the selected employee and years. / ไม่พบข้อมูลสำหรับพนักงานคนนี้ในปีที่คุณเลือก")
        else:
            # Iterate through each text criterion
            for crit in criteria_with_text_data:
                criteria_display_name = caption_eng.get(crit, crit)
                
                # Filter data for the current criterion across all selected years
                current_criteria_text_data = text_data[text_data["criteria"] == crit].sort_values(by="evaluation_year", ascending=False)
                
                # Get unique years for this specific criterion's responses
                years_for_crit = sorted(current_criteria_text_data["evaluation_year"].dropna().unique(), reverse=True)
                
                # Format years string for expander title
                years_str = ", ".join(map(str, years_for_crit)) if years_for_crit else "No years"
                
                # Get all non-null text responses for this criterion (across all selected years)
                all_responses_for_crit = current_criteria_text_data["text_response"].dropna().tolist()

                if all_responses_for_crit:
                    # Create one expander per criterion
                    with st.expander(f"**{criteria_display_name}** (Total Responses: {len(all_responses_for_crit)})"):
                        # Group and display responses by year within the expander
                        for year in years_for_crit:
                            responses_this_year = current_criteria_text_data[current_criteria_text_data["evaluation_year"] == year]["text_response"].dropna().tolist()
                            if responses_this_year:
                                st.markdown(f"**{year} Responses:**")
                                for idx, text in enumerate(responses_this_year, 1):
                                    st.markdown(f"- {text}")
                            else:
                                st.markdown(f"**{year} Responses:** *No responses provided for this year.*")
                else:
                    st.info(f"No text responses provided for '{criteria_display_name}' in the selected years.")