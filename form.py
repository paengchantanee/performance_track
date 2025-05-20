import streamlit as st
import pandas as pd
import os

st.header("📝 กรอกแบบประเมินพนักงาน (360 Evaluation Form)")

# โหลดไฟล์ข้อมูลพนักงาน
employee_df = pd.read_csv("employee_info.csv")

# เลือกผู้ถูกประเมิน
employee_names = employee_df["name"].tolist()
employee_selected = st.selectbox("เลือกพนักงานที่ต้องการประเมิน", employee_names)

# ดึง employee_id
employee_id = employee_df[employee_df["name"] == employee_selected]["employee_id"].values[0]
position = employee_df[employee_df["name"] == employee_selected]["position"].values[0]

# เกณฑ์จำลองตามตำแหน่ง
criteria_by_position = {
    "Sales Executive": ["Communication", "Target Achievement", "Negotiation"],
    "Data Analyst": ["Analytical Thinking", "Accuracy", "Communication"]
}
criteria_list = criteria_by_position.get(position, [])

# ฟอร์มกรอกข้อมูล
with st.form("evaluation_form"):
    evaluator_type = st.selectbox("คุณคือใคร (ผู้ประเมิน)", ["Self", "Manager", "Peer", "Subordinate"])

    scores = {}
    for crit in criteria_list:
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

    # ตรวจว่ามีไฟล์เก่าไหม
    if os.path.exists("evaluation_data.csv"):
        old_data = pd.read_csv("evaluation_data.csv")
        updated_data = pd.concat([old_data, new_data], ignore_index=True)
    else:
        updated_data = new_data

    updated_data.to_csv("evaluation_data.csv", index=False)
    st.success("✅ บันทึกข้อมูลเรียบร้อยแล้ว!")
