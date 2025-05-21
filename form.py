import streamlit as st
import pandas as pd
import os

st.header("📝 กรอกแบบประเมินพนักงาน (360 Evaluation Form)")

# โหลดไฟล์ข้อมูลพนักงาน
employee_df = pd.read_csv("employee_info.csv")

# เลือกแผนกก่อน 
departments = sorted(employee_df["department"].unique())
selected_department = st.selectbox("เลือกแผนก", departments)

# เลือกผู้ถูกประเมิน (กรองตามแผนก)
filtered_employees = employee_df[employee_df["department"] == selected_department]
employee_names = filtered_employees["name"].tolist()
employee_selected = st.selectbox("เลือกพนักงานที่ต้องการประเมิน", employee_names)

# ดึง employee_id และแผนกของพนักงาน
employee_row = filtered_employees[filtered_employees["name"] == employee_selected].iloc[0]
employee_id = employee_row["employee_id"]
department = employee_row["department"]

# 🔹 เกณฑ์หลัก (Core criteria)
core_criteria = ["Teamwork", "Punctuality", "Professionalism"]
core_captions = {
    "Teamwork": "ความสามารถในการทำงานร่วมกับผู้อื่น",
    "Punctuality": "การตรงต่อเวลาและรักษาวินัย",
    "Professionalism": "การแสดงออกอย่างมืออาชีพ"
}

# 🔸 เกณฑ์เฉพาะตามแผนก
criteria_by_department = {
    "Sales": ["Communication", "Target Achievement", "Negotiation"],
    "IT": ["Analytical Thinking", "Accuracy", "Communication"]
}
department_captions = {
    "Communication": "ทักษะการสื่อสารที่มีประสิทธิภาพ",
    "Target Achievement": "การบรรลุเป้าหมายที่ตั้งไว้",
    "Negotiation": "ความสามารถในการเจรจาต่อรอง",
    "Analytical Thinking": "ความสามารถในการวิเคราะห์ปัญหา",
    "Accuracy": "ความถูกต้องในการทำงาน"
}

# รวมเกณฑ์และคำอธิบาย
department_criteria = criteria_by_department.get(department, [])
all_criteria = core_criteria + department_criteria

# ฟอร์มกรอกข้อมูล
with st.form("evaluation_form"):
    st.write("📋 โปรดให้คะแนนตามเกณฑ์")

    evaluator_type = st.selectbox("คุณคือใคร (ผู้ประเมิน)", ["Self", "Manager", "Peer", "Subordinate"])
    st.write("___")

    scores = {}
    for crit in all_criteria:
        # แสดงคำอธิบายใต้หัวข้อก่อนแสดง slider
        if crit in core_captions:
            st.caption(core_captions[crit])
        elif crit in department_captions:
            st.caption(department_captions[crit])

        score = st.slider(f"{crit}", min_value=1, max_value=5, value=3)
        scores[crit] = score

    submitted = st.form_submit_button("✅ บันทึกผลการประเมิน")


# บันทึกข้อมูลเมื่อกด Submit
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
