import streamlit as st
import pandas as pd
import os

st.header("👥 Employee data (ข้อมูลพนักงาน)")

# Load existing employee data
if os.path.exists("employee_info.csv"):
    employee_df = pd.read_csv("employee_info.csv")
else:
    employee_df = pd.DataFrame(columns=["employee_id", "name"]) 

# ----- Section: View employees by department -----
st.subheader("🔍 รายชื่อพนักงานตามแผนก")

if not employee_df.empty:
    # Select department
    departments = sorted(employee_df["department"].unique())
    selected_dept = st.selectbox("เลือกแผนก", departments)

    # Filter and show employees in selected department
    filtered_df = employee_df[employee_df["department"] == selected_dept]

    if not filtered_df.empty:
        st.dataframe(filtered_df.reset_index(drop=True))
    else:
        st.warning("⚠️ ไม่มีพนักงานในแผนกนี้")
else:
    st.warning("⚠️ ยังไม่มีข้อมูลพนักงาน")

# ----- Section: Add new employee -----
st.subheader("➕ เพิ่มพนักงานใหม่")
with st.form("add_employee_form"):
    new_id = st.text_input("รหัสพนักงาน (Employee ID)")
    new_name = st.text_input("ชื่อพนักงาน (Name)")
    new_dept = st.text_input("แผนก (Department)")

    submitted = st.form_submit_button("✅ เพิ่มพนักงาน")

if submitted:
    if new_id and new_name and new_dept:
        # Check for duplicate employee_id
        if new_id in employee_df["employee_id"].values:
            st.warning("⚠️ รหัสพนักงานนี้มีอยู่แล้ว!")
        else:
            new_row = pd.DataFrame([{
                "employee_id": new_id,
                "name": new_name,
                "department": new_dept
            }])
            updated_df = pd.concat([employee_df, new_row], ignore_index=True)
            updated_df.to_csv("employee_info.csv", index=False)
            st.success("✅ เพิ่มพนักงานเรียบร้อยแล้ว!")
            st.experimental_rerun()
    else:
        st.error("❌ กรุณากรอกข้อมูลให้ครบถ้วน")
