import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Load data
employee_df = pd.read_csv("employee_info.csv")
criteria_df = pd.read_csv("criteria_config.csv")
eval_df = pd.read_csv("evaluation_data.csv")

# Ensure 'evaluation_year' is of type int
eval_df['evaluation_year'] = eval_df['evaluation_year'].astype(int)

# Sidebar for navigation
st.sidebar.title("Navigation")
section = st.sidebar.radio("Go to", ["Criteria Dashboard", "Department Focus", "Trend Over Time"])

# Mapping for criterion captions
caption_eng = criteria_df.set_index("criteria")["caption_eng"].to_dict()

# 1️. Criteria Dashboard
if section == "Criteria Dashboard":
    st.subheader("📊 Criteria Dashboard (Company-Wide)")
    st.caption("> สรุปค่าเฉลี่ยตามเกณฑ์การประเมินทั่วทั้งบริษัท")

    # Select year and criteria group
    available_years = sorted(eval_df["evaluation_year"].dropna().unique(), reverse=True)
    selected_year = st.selectbox("Select Evaluation Year / เลือกปีที่ประเมิน", available_years)

    criteria_groups = sorted(criteria_df["department"].unique())
    selected_group = st.selectbox("Select Criteria Group / เลือกกลุ่มเกณฑ์การประเมิน", criteria_groups)

    # Filter evaluation and criteria
    filtered_eval = eval_df[eval_df["evaluation_year"] == selected_year]
    group_criteria = criteria_df[criteria_df["department"] == selected_group]["criteria"].unique()
    filtered_eval = filtered_eval[filtered_eval["criteria"].isin(group_criteria)]

    # Group and calculate average scores
    criteria_avg = filtered_eval.groupby('criteria')['score'].mean().reset_index()
    criteria_avg["score"] = criteria_avg["score"].round(2)
    criteria_avg = criteria_avg.sort_values(by="score", ascending=True)

    # Handle empty data
    if criteria_avg.empty:
        st.warning("No data available for the selected group and year. / ไม่พบข้อมูลสำหรับกลุ่มและปีที่เลือก")
    else:
        # Top and bottom
        top_row = criteria_avg.iloc[0]
        bottom_row = criteria_avg.iloc[-1]

        # Horizontal bar chart
        bar_fig = px.bar(
            criteria_avg,
            x='score',
            y='criteria',
            orientation='h',
            title=f'Average Score by Criteria – {selected_group} ({selected_year})',
            color='score',
            color_continuous_scale='bluyl',
            labels={'score': 'Average Score'},
            height=500
        )
        st.plotly_chart(bar_fig, use_container_width=True)

        # Insight
        st.markdown(f"""
        ### Insights (สรุปข้อมูลเชิงลึก)
        💪 **Top Strength / จุดแข็ง:** {top_row['criteria']} (Avg: {top_row['score']:.2f})  
        🛠️ **Area for Improvement / ควรปรับปรุง:** {bottom_row['criteria']} (Avg: {bottom_row['score']:.2f})
        """)



# 2️. Department Focus
elif section == "Department Focus":
    st.title("🏢 Department Focus")
    st.caption("> สรุปค่าเฉลี่ยผลการประเมินของแต่ละแผนกในแต่ละปีที่เลือก / เปรียบเทียบรายปี")
    departments = sorted(employee_df["department"].unique())
    selected_department = st.selectbox("Select Department / เลือกแผนก", departments)
    available_years = sorted(eval_df["evaluation_year"].unique(), reverse=True)
    selected_years = st.multiselect("Select Evaluation Year(s) / เลือกปีที่ประเมิน (สามารถเลือกได้มากกว่า 1 ปี)", available_years, default=available_years[0])
    
    if not selected_years:
        st.warning("Please select at least one year. / โปรดเลือกอย่างน้อย 1 ปี")
    else:
        dept_emp_ids = employee_df[employee_df["department"] == selected_department]["employee_id"]
        dept_data = eval_df[(eval_df["employee_id"].isin(dept_emp_ids)) & (eval_df["evaluation_year"].isin(selected_years))]
        
        if dept_data.empty:
            st.warning("No evaluation data available for the selected department and years.")
        else:
            avg_scores = dept_data.groupby(["evaluation_year", "criteria"])["score"].mean().reset_index()
            avg_scores["score"] = avg_scores["score"].round(2)
            
            fig = px.line(avg_scores, x="criteria", y="score", color="evaluation_year",
                          title=f"Average Criteria Scores for {selected_department} Over Selected Years",
                          labels={"score": "Average Score", "criteria": "Criteria", "evaluation_year": "Year"})
            st.plotly_chart(fig, use_container_width=True)


# 3. Trend Over Time
elif section == "Trend Over Time":
    st.subheader("📈 Trend Over Time by Criteria")
    st.caption("> แนวโน้มตามเกณฑ์และเวลา")

    # Available criteria in data
    available_criteria = sorted(eval_df["criteria"].unique())

    # Let user select one or more criteria
    selected_criteria = st.multiselect("Select Criteria / เลือกเกณฑ์การประเมิน", available_criteria, default=available_criteria[:3])

    if selected_criteria:
        # Filter by selected criteria
        trend_data = eval_df[eval_df["criteria"].isin(selected_criteria)]

        # Group by year and criteria, calculate average score
        trend_summary = trend_data.groupby(["evaluation_year", "criteria"])["score"].mean().reset_index()
        trend_summary["score"] = trend_summary["score"].round(2)

        # Plot line chart
        fig = px.line(
            trend_summary,
            x="evaluation_year",
            y="score",
            color="criteria",
            markers=True,
            title="Average Score Trend Over Time by Criteria",
            labels={"evaluation_year": "Year", "score": "Average Score", "criteria": "Criteria"}
        )
        fig.update_layout(xaxis=dict(dtick=1))
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Please select at least one criterion to view the trend. / โปรดเลือกอย่างน้อย 1 เกณฑ์")
