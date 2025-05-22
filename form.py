import streamlit as st
import pandas as pd
import os

st.header("📝 360 Evaluation Form (กรอกแบบประเมินพนักงาน)")

# Read file
employee_df = pd.read_csv("employee_info.csv")
criteria_config = pd.read_csv("criteria_config.csv")

# Select department 
departments = sorted(employee_df["department"].unique())
selected_department = st.selectbox("เลือกแผนก", departments)

# Select employee
filtered_employees = employee_df[employee_df["department"] == selected_department]
employee_names = filtered_employees["name"].tolist()
employee_selected = st.selectbox("เลือกพนักงานที่ต้องการประเมิน", employee_names)

# ดึง employee_id และแผนกของพนักงาน
employee_row = filtered_employees[filtered_employees["name"] == employee_selected].iloc[0]
employee_id = employee_row["employee_id"]
department = employee_row["department"]

# 🔹 ดึงเกณฑ์หลักและเฉพาะแผนกจากไฟล์ config
core_criteria_df = criteria_config[criteria_config["department"] == "Core"]
dept_criteria_df = criteria_config[criteria_config["department"] == department]

core_criteria = core_criteria_df["criteria"].tolist()
department_criteria = dept_criteria_df["criteria"].tolist()
captions_dict = pd.concat([core_criteria_df, dept_criteria_df]).set_index("criteria")["caption"].to_dict()

all_criteria = core_criteria + department_criteria

# ฟอร์มกรอกข้อมูล
with st.form("evaluation_form"):
    st.write("📋 โปรดให้คะแนนตามเกณฑ์")

    evaluator_type = st.selectbox("คุณคือใคร (ผู้ประเมิน)", ["Self", "Manager", "Peer", "Subordinate"])
    st.write("___")

    scores = {}
    for crit in all_criteria:
        if crit in captions_dict:
            st.caption(captions_dict[crit])

        score = st.slider(f"{crit}", min_value=1, max_value=5, value=3)
        scores[crit] = score

    submitted = st.form_submit_button("✅ บันทึกผลการประเมิน")

# บันทึกข้อมูล
if submitted:
    new_data = pd.DataFrame([{
        "employee_id": employee_id,
        "evaluator_type": evaluator_type,
        "criteria": crit,
        "score": score
    } for crit, score in scores.items()])

    if os.path.exists("evaluation_data.csv"):
        old_data = pd.read_csv("evaluation_data.csv")
        updated_data = pd.concat([old_data, new_data], ignore_index=True)
    else:
        updated_data = new_data

    updated_data.to_csv("evaluation_data.csv", index=False)
    st.success("✅ บันทึกข้อมูลเรียบร้อยแล้ว!")
