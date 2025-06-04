import streamlit as st 
import pandas as pd
import os
import json

# Config
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

# UI Header
st.header("📝 360° Evaluation Form (กรอกแบบประเมินพนักงาน)")
st.write("- This evaluation form is designed for 360-degree evaluation, " \
         "which requires gathering opinions from managers, peers, subordinates, and even oneself " \
         "to obtain a well-rounded and multi-perspective assessment for reliable results.")
st.caption("- แบบประเมินพนักงานนี้ออกแบบมาเพื่อทำการประเมินผลรอบทิศแบบ 360 องษา")
st.write("___")

# Load data
employee_df = pd.read_csv("employee_info.csv")
criteria_file = "custom_criteria.csv" if use_custom else "criteria_config.csv"
criteria_config = pd.read_csv(criteria_file)

# Select employee
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

all_criteria_df = pd.concat([core_criteria_df, dept_criteria_df], ignore_index=True)

# Form
with st.form("evaluation_form"):
    evaluator_type = st.selectbox("Evaluator / ผู้ประเมิน", ["Self / ตัวเอง", "Manager / ผู้จัดการ", "Peer / เพื่อนร่วมงาน", "Subordinate / ลูกน้อง"])
    evaluator_id = st.text_input("Evaluator ID / รหัสผู้ประเมิน")
    year = st.number_input("Year of Evaluation / ปีที่ประเมิน", value=2025, step=1)
    st.write("___")

    st.subheader("**📋 Please rate the employee on the following competencies**")
    st.caption("> โปรดให้คะแนนพนักงานตามความสามารถต่อไปนี้ โดยใช้มาตรวัดจาก 1 ถึง 5 (1 = น้อยที่สุด, 5 = มากที่สุด)")
    st.badge(f"{'Custom' if use_custom else 'Default'} Questionnaire")

    responses = []

    for _, row in all_criteria_df.iterrows():
        crit = row["criteria"]
        caption_eng = row.get("caption_eng", crit)
        caption_th = row.get("caption_th", "")
        q_type = row.get("type", "rating").strip().lower()

        st.markdown(f"**{caption_eng}**")
        st.caption(caption_th)

        # Default values
        score = ""
        value = ""
        text_response = ""
        typ = ""

        if q_type == "rating":
            score = st.slider(crit, 1, 5, 3, key=crit)
            typ = ""
        elif q_type in ["numeric", "kpi", "okr"]:
            value = st.number_input(crit, step=1.0, format="%f", key=crit)
            typ = q_type
        elif q_type == "text":
            text_response = st.text_area(crit, key=crit)
            typ = "text"
        else:
            score = st.slider(crit, 1, 5, 3, key=crit + "_fallback")
            typ = ""

        responses.append({
            "employee_id": employee_id,
            "evaluator_id": evaluator_id,
            "evaluator_type": evaluator_type,
            "evaluation_year": year,
            "criteria": crit,
            "type": typ,
            "score": score,
            "value": value,
            "text_response": text_response
        })

    submitted = st.form_submit_button("✅ Submit / ส่งแบบประเมิน")

# Save data
if submitted:
    new_data = pd.DataFrame(responses)

    if os.path.exists("evaluation_data.csv"):
        old_data = pd.read_csv("evaluation_data.csv")
        updated_data = pd.concat([old_data, new_data], ignore_index=True)
    else:
        updated_data = new_data

    updated_data.to_csv("evaluation_data.csv", index=False)
    st.success("✅ Data saved successfully! / บันทึกข้อมูลเสร็จสิ้น")
