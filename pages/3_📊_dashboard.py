import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Load data
employee_df = pd.read_csv("employee_info.csv")
criteria_df = pd.read_csv("criteria_config.csv")
eval_df = pd.read_csv("evaluation_data.csv")

# Title
st.title("📊 Criteria Dashboard report")
st.caption("Employee insights across competencies and evaluators")

# Select department and employee
departments = sorted(employee_df["department"].unique())
selected_department = st.selectbox("Select department / เลือกแผนก", departments)

filtered_employees = employee_df[employee_df["department"] == selected_department]
employee_names = filtered_employees["name"].tolist()
employee_selected = st.selectbox("Select employee", employee_names)

# Get employee info
emp_row = filtered_employees[filtered_employees["name"] == employee_selected].iloc[0]
emp_id = emp_row["employee_id"]
emp_dept = emp_row["department"]

# Filter evaluation data
emp_eval = eval_df[eval_df["employee_id"] == emp_id]

if emp_eval.empty:
    st.warning("No evaluations found for this employee.")
    st.stop()

# Merge captions
core_criteria = criteria_df[criteria_df["department"] == "Core"]
dept_criteria = criteria_df[criteria_df["department"] == emp_dept]
all_criteria_df = pd.concat([core_criteria, dept_criteria])

caption_eng = all_criteria_df.set_index("criteria")["caption_eng"].to_dict()

# --- Dashboard Components ---

# 1. Number of Evaluators
num_evaluators = emp_eval["evaluator_type"].nunique()
st.metric("👥 Number of Evaluator Types", num_evaluators)

# 2. Bar Chart of Average Scores
avg_scores = emp_eval.groupby("criteria")["score"].mean().reset_index()
avg_scores = avg_scores[avg_scores["criteria"].isin(all_criteria_df["criteria"])]
avg_scores["score"] = avg_scores["score"].round(2)
avg_scores = avg_scores.sort_values(by="score", ascending=True)


bar = px.bar(
    avg_scores,
    x="score",
    y="criteria",
    orientation="h",
    title="📊 Average Scores by Criteria",
    labels={"criteria": "Criteria", "score": "Average Score"},
    color="score",
    color_continuous_scale="blues",
    height=500
)
st.plotly_chart(bar, use_container_width=True)

# 3. Radar Chart
radar_data = avg_scores.copy()
radar_data = radar_data.set_index("criteria").reindex(all_criteria_df["criteria"])
radar = radar_data.reset_index()
radar = pd.concat([radar, radar.iloc[[0]]])  # Close loop

fig = go.Figure()
fig.add_trace(go.Scatterpolar(
    r=radar["score"],
    theta=radar["criteria"],
    fill='toself',
    name=employee_selected
))
fig.update_layout(
    polar=dict(radialaxis=dict(visible=True, range=[1, 5])),
    title="📈 Radar Chart of Evaluation",
    showlegend=False
)
st.plotly_chart(fig, use_container_width=True)

# 4. Strengths & Opportunities
st.subheader("🌟 Strengths and 🛠 Opportunities")

top_3 = avg_scores.sort_values("score", ascending=False).head(3)
bottom_3 = avg_scores.sort_values("score").head(3)

col1, col2 = st.columns(2)
with col1:
    st.markdown("**Top Strengths**")
    for _, row in top_3.iterrows():
        st.write(f"- {row['criteria']} ({row['score']:.2f})")

with col2:
    st.markdown("**Improvement Opportunities**")
    for _, row in bottom_3.iterrows():
        st.write(f"- {row['criteria']} ({row['score']:.2f})")

# 6. Evaluator Breakdown: Self vs Others
st.subheader("📊 Self vs Others Comparison")

# Separate self and others
self_scores = emp_eval[emp_eval["evaluator_type"] == "Self / ตัวเอง"]
others_scores = emp_eval[emp_eval["evaluator_type"] != "Self / ตัวเอง"]

# Compute averages per criteria
self_avg = self_scores.groupby("criteria")["score"].mean().rename("Self")
others_avg = others_scores.groupby("criteria")["score"].mean().rename("Others")

# Combine into single DataFrame
comparison_df = pd.concat([self_avg, others_avg], axis=1)
comparison_df = comparison_df.reindex(all_criteria_df["criteria"]).reset_index()
comparison_df = comparison_df.round(2)

# Ensure numeric types for plotting
comparison_df["Self"] = pd.to_numeric(comparison_df["Self"], errors="coerce")
comparison_df["Others"] = pd.to_numeric(comparison_df["Others"], errors="coerce")

# Determine bar colors: red if self < others, blue otherwise
colors = ["crimson" if self < others else "royalblue"
          for self, others in zip(comparison_df["Self"], comparison_df["Others"])]

# Create grouped bar chart
fig = go.Figure()

# Self scores with dynamic colors
fig.add_trace(go.Bar(
    x=comparison_df["criteria"],
    y=comparison_df["Self"],
    name="Self",
    marker_color=colors
))

# Others scores in gray
fig.add_trace(go.Bar(
    x=comparison_df["criteria"],
    y=comparison_df["Others"],
    name="Others",
    marker_color="lightgray"
))

# Customize layout
fig.update_layout(
    barmode='group',
    title="Comparison: Self vs Others",
    xaxis_title="Criteria",
    yaxis_title="Score",
    height=400
)

st.plotly_chart(fig, use_container_width=True)

# 5. Summary Table
st.subheader("📋 Summary Table")
summary_table = avg_scores.copy()
summary_table["Description"] = summary_table["criteria"].map(caption_eng)
summary_table = summary_table[["criteria", "score", "Description"]]
summary_table.columns = ["Criteria", "Avg Score", "Description"]
summary_table["Avg Score"] = summary_table["Avg Score"].round(2)
summary_table.index = range(1, len(summary_table) + 1)
st.dataframe(summary_table, use_container_width=True)

###

st.subheader("📊 Company-Wide Performance Summary")

# Group by criteria to get average scores
criteria_avg = eval_df.groupby('criteria')['score'].mean().reset_index()
criteria_avg["score"] = criteria_avg["score"].round(2)
criteria_avg = criteria_avg.sort_values(by="score", ascending=False)

# Find top and bottom criteria
top_row = criteria_avg.loc[criteria_avg['score'].idxmax()]
bottom_row = criteria_avg.loc[criteria_avg['score'].idxmin()]

top_criteria, top_score = top_row['criteria'], top_row['score']
bottom_criteria, bottom_score = bottom_row['criteria'], bottom_row['score']

top_score = round(top_score, 2)
bottom_score = round(bottom_score, 2)

# Create bar chart using Plotly
bar_fig = px.bar(criteria_avg,
                 x='criteria',
                 y='score',
                 title='Average Score by Criteria (Company-Wide)',
                 color='score',
                 color_continuous_scale='Viridis',
                 labels={'score': 'Average Score'},
                 height=400)

st.plotly_chart(bar_fig, use_container_width=True)

# Display insights
st.markdown(f"""
### Insights  
✅ **Top Strength:** {top_criteria} (Average Score: {top_score:.2f})  
🔍 **Area for Improvement:** {bottom_criteria} (Average Score: {bottom_score:.2f})
""")