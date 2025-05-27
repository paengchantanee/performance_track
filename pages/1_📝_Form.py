import streamlit as st
import pandas as pd
import os

st.header("📝 360° Evaluation Form (กรอกแบบประเมินพนักงาน)")
st.write("- This evaluation form is designed for 360-degree evaluation, " \
"which requires gathering opinions from managers, peers, subordinates, and even oneself " \
"to obtain a well-rounded and multi-perspective assessment for reliable results.")
st.caption("- แบบประเมินพนักงานนี้ออกแบบมาเพื่อทำการประเมินผลรอบทิศแบบ 360 องศา " \
"ซึ่งเป็นการประเมินที่ต้องสอบถามความคิดเห็นจากบุคคลรอบข้างที่เกี่ยวข้องกับการทำงานทั้งหมดแบบครบองค์รวม 360 องศา" \
"ตั้งแต่ ผู้บังคับบัญชา, ผู้ใต้บังคับบัญชา, เพื่อนร่วมงาน หรือแม้แต่ตัวเอง เพื่อให้ได้ผลประเมินที่รอบด้าน หลายมุมมอง หลายฝ่าย ทำให้ข้อมูลมีความน่าเชื่อถือมากขึ้น")
st.write("___")
 
# Read file 
employee_df = pd.read_csv("employee_info.csv")
criteria_config = pd.read_csv("criteria_config.csv")

# Select department 
departments = sorted(employee_df["department"].unique())
selected_department = st.selectbox("Select department / เลือกแผนก", departments)

# Select employee
filtered_employees = employee_df[employee_df["department"] == selected_department]
employee_names = filtered_employees["name"].tolist()
employee_selected = st.selectbox("Select employee / เลือกพนักงานที่ต้องการประเมิน", employee_names)

# Retrieve employee_id and department
employee_row = filtered_employees[filtered_employees["name"] == employee_selected].iloc[0]
employee_id = employee_row["employee_id"]
department = employee_row["department"]

# Retrieve core and department criteria
core_criteria_df = criteria_config[criteria_config["department"] == "Core"]
dept_criteria_df = criteria_config[criteria_config["department"] == department]

core_criteria = core_criteria_df["criteria"].tolist()
department_criteria = dept_criteria_df["criteria"].tolist()
captions_eng = pd.concat([core_criteria_df, dept_criteria_df]).set_index("criteria")["caption_eng"].to_dict()
captions_th = pd.concat([core_criteria_df, dept_criteria_df]).set_index("criteria")["caption_th"].to_dict()

all_criteria = core_criteria + department_criteria

# Form
with st.form("evaluation_form"):

    evaluator_type = st.selectbox("Evaluator / ผู้ประเมิน", ["Self / ตัวเอง", "Manager / ผู้จัดการ", "Peer / เพื่อนร่วมงาน", "Subordinate / ลูกน้อง"])
    evaluator_id = st.text_input("Evaluator ID / รหัสผู้ประเมิน")
    year = st.number_input("Year of Evaluation / ปีที่ประเมิน", min_value=2000, max_value=2100, value=2025, step=1)
    st.write("___")

    st.subheader("**📋 Please rate the employee on the following competencies**")
    st.write("- Using a scale of 1 to 5, where 1 is the least and 5 is the most")
    st.write("- โปรดให้คะแนนพนักงานตามเกณฑ์ต่อไปนี้ด้วยคะแนน 1 ถึง 5 โดยที่ 1 คือน้อยที่สุดและ 5 คือมากที่สุด")
    st.badge("15 questions / ข้อ")

    scores = {}
    for crit in all_criteria:
        if crit in captions_eng:
            st.write(f">**{crit}**")

        st.caption(captions_th[crit])
        score = st.slider(captions_eng[crit], min_value=1, max_value=5, value=3)
        scores[crit] = score

    submitted = st.form_submit_button("✅ Submit / ส่งแบบประเมิน")

# Record the data
if submitted:
    new_data = pd.DataFrame([{
    "employee_id": employee_id,
    "evaluator_id": evaluator_id,  # Add this
    "evaluator_type": evaluator_type,
    "evaluation_year": year, 
    "criteria": crit,
    "score": score
    } for crit, score in scores.items()])

    if os.path.exists("evaluation_data.csv"):
        old_data = pd.read_csv("evaluation_data.csv")
        updated_data = pd.concat([old_data, new_data], ignore_index=True)
    else:
        updated_data = new_data

    updated_data.to_csv("evaluation_data.csv", index=False)
    st.success("✅ Data saved successfully!")
    st.success("บันทึกข้อมูลเรียบร้อยแล้ว")
