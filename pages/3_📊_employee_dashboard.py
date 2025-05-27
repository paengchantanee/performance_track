import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Load data
employee_df = pd.read_csv("employee_info.csv")
criteria_df = pd.read_csv("criteria_config.csv")
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
    st.warning("⚠️ No evaluation years available. / ไม่มีปีที่สามารถประเมินได้")
    st.stop()

eval_selected = eval_df[eval_df["evaluation_year"].isin(selected_years)]

# Select department and employee
departments = sorted(employee_df["department"].unique())
selected_department = st.selectbox("Select department / เลือกแผนก", departments)

filtered_employees = employee_df[employee_df["department"] == selected_department]
employee_names = filtered_employees["name"].tolist()
employee_selected = st.selectbox("Select employee / เลือกพนักงาน ", employee_names)

# Get employee info
emp_row = filtered_employees[filtered_employees["name"] == employee_selected].iloc[0]
emp_id = emp_row["employee_id"]
emp_dept = emp_row["department"]

# Filter evaluation data
emp_eval = eval_selected[eval_selected["employee_id"] == emp_id]

if emp_eval.empty:
    st.warning("No evaluations found for this employee in the selected year(s). / ไม่พบผลการประเมินของพนักงานคนนี้ในปีที่ท่านเลือก")
    st.stop()

# Merge captions
core_criteria = criteria_df[criteria_df["department"] == "Core"]
dept_criteria = criteria_df[criteria_df["department"] == emp_dept]
all_criteria_df = pd.concat([core_criteria, dept_criteria])
caption_eng = all_criteria_df.set_index("criteria")["caption_eng"].to_dict()
caption_th = all_criteria_df.set_index("criteria")["caption_th"].to_dict()
st.write("___")

# 1. Number of Evaluators
num_evaluators = emp_eval["evaluator_id"].nunique()
st.metric("👥 Number of Evaluator / จำนวนคนประเมิน", num_evaluators)

# 2. Bar Chart of Average Scores (or yearly comparison if multiple years)
st.subheader("🔹 Average Scores by Criteria / Yearly Comparison")
st.caption("> คะแนนเฉลี่ยตามเกณฑ์ / เปรียบเทียบรายปี (หากมีการเลือกปีมากกว่า 1 ปี)")
avg_scores = emp_eval.groupby(["evaluation_year", "criteria"])["score"].mean().reset_index()
avg_scores = avg_scores[avg_scores["criteria"].isin(all_criteria_df["criteria"])]

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
st.subheader("🔹 Radar Chart")
st.caption("> แผนภูมิเรดาร์")
radar_avg = avg_scores.groupby("criteria")["score"].mean().reindex(all_criteria_df["criteria"]).reset_index()
radar_avg = pd.concat([radar_avg, radar_avg.iloc[[0]]])  # Close loop

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

comparison_df = pd.concat([self_avg, others_avg], axis=1).reindex(all_criteria_df["criteria"]).reset_index()
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

# 6. Summary Table
st.subheader("📋 Summary Table")
st.caption("> ตารางสรุป")
table = latest_avg.copy()
table["Description"] = table["criteria"].map(caption_eng)
table["คำอธิบาย"] = table["criteria"].map(caption_th)
table.columns = ["Criteria", "Avg Score", "Description","คำอธิบาย"]
table["Avg Score"] = table["Avg Score"].round(2)
table.index = range(1, len(table) + 1)
st.dataframe(table, use_container_width=True)

# 7. Trend Over Time of a Selected Criterion
st.subheader("📈 Trend Over Time")
st.caption("> แนวโน้มรายปี")
all_emp_eval = eval_df[eval_df["employee_id"] == emp_id]
all_emp_eval = all_emp_eval[all_emp_eval["criteria"].isin(all_criteria_df["criteria"])]

criteria_options = all_emp_eval["criteria"].unique()
selected_criterion = st.selectbox("Select a criterion to view trend / เลือกเกณฑ์ที่ต้องการจะดู", criteria_options)

trend = all_emp_eval[all_emp_eval["criteria"] == selected_criterion]
trend = trend.groupby("evaluation_year")["score"].mean().reset_index()

fig = px.line(
    trend,
    x="evaluation_year",
    y="score",
    markers=True,
    title=f"Trend Over Time: {selected_criterion}",
    labels={"evaluation_year": "Year", "score": "Avg Score"},
    height=400
)
fig.update_layout(yaxis_range=[1, 5])
st.plotly_chart(fig, use_container_width=True)
