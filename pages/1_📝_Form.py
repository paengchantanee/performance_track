import streamlit as st
import pandas as pd
import os
import json

# --- Config ---

CONFIG_FILE = "config.json"

def load_config():
    if not os.path.exists(CONFIG_FILE):
        default_config = {"use_custom": False}
        with open(CONFIG_FILE, "w") as f:
            json.dump(default_config, f)
        return default_config
    else:
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)

config = load_config()
use_custom = config.get("use_custom", False)

# --- UI Header ---
st.header("📝 360° Evaluation Form (กรอกแบบประเมินพนักงาน)")
st.write("- This evaluation form is designed for 360-degree evaluation, " \
         "which requires gathering opinions from managers, peers, subordinates, and even oneself " \
         "to obtain a well-rounded and multi-perspective assessment for reliable results.")
st.caption("- แบบประเมินพนักงานนี้ออกแบบมาเพื่อทำการประเมินผลรอบทิศแบบ 360 องษา " \
           "ซึ่งเป็นการประเมินที่ต้องสอบถามความคิดเห็นกับการทำงานทั้งหมดแบบครบองค์รวม 360 องษา")
st.write("___")

# --- Load data ---
employee_df = pd.read_csv("employee_info.csv")
criteria_file = "custom_criteria.csv" if use_custom else "criteria_config.csv"
criteria_config = pd.read_csv(criteria_file)

# --- Select employee ---
departments = sorted(employee_df["department"].unique())
selected_department = st.selectbox("Select department / เลือกแผนก", departments)
filtered_employees = employee_df[employee_df["department"] == selected_department]
employee_names = filtered_employees["name"].tolist()
employee_selected = st.selectbox("Select employee / เลือกพนักงานที่ต้องประเมิน", employee_names)

employee_row = filtered_employees[filtered_employees["name"] == employee_selected].iloc[0]
employee_id = employee_row["employee_id"]
department = employee_row["department"]

core_criteria_df = criteria_config[criteria_config["department"] == "Core"]
dept_criteria_df = criteria_config[criteria_config["department"] == department]

core_criteria = core_criteria_df["criteria"].tolist()
department_criteria = dept_criteria_df["criteria"].tolist()
captions_eng = pd.concat([core_criteria_df, dept_criteria_df]).set_index("criteria")["caption_eng"].to_dict()
captions_th = pd.concat([core_criteria_df, dept_criteria_df]).set_index("criteria")["caption_th"].to_dict()

all_criteria = core_criteria + department_criteria

# --- Form ---
with st.form("evaluation_form"):
    evaluator_type = st.selectbox("Evaluator / ผู้ประเมิน", ["Self / ตัวเอง", "Manager / ผู้จัดการ", "Peer / เพื่อนร่วมงาน", "Subordinate / ลูกน้อง"])
    evaluator_id = st.text_input("Evaluator ID / รหัสผู้ประเมิน")
    year = st.number_input("Year of Evaluation / ปีที่ประเมิน", min_value=2000, max_value=2100, value=2025, step=1)
    st.write("___")

    st.subheader("**📋 Please rate the employee on the following competencies**")
    st.write("- Using a scale of 1 to 5, where 1 is the least and 5 is the most")
    st.write("- โปรดให้คะแนนพนักงานตามเกณฐ์ต่อไปนี้ด้วยคะแนน 1 ถึง 5")
    st.badge(f"{'Custom' if use_custom else 'Default'} Questionnaire")

    scores = {}
    for crit in all_criteria:
        st.write(f">**{crit}**")
        st.caption(captions_th.get(crit, ""))
        score = st.slider(captions_eng.get(crit, crit), 1, 5, 3)
        scores[crit] = score

    submitted = st.form_submit_button("✅ Submit / ส่งแบบประเมิน")

# --- Save data ---
if submitted:
    new_data = pd.DataFrame([{
        "employee_id": employee_id,
        "evaluator_id": evaluator_id,
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