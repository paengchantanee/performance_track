import streamlit as st
import pandas as pd
import os

st.header("👥 Employee data (ข้อมูลพนักงาน)")
st.write("This application is designed to help you manage employee information viewing the list of employees, adding new entries, or deleting existing ones.")
st.caption("แอปพลิเคชันนี้ถูกออกแบบมาเพื่อช่วยคุณจัดการข้อมูลพนักงาน โดยสามารถดูรายชื่อพนักงาน เพิ่มพนักงานใหม่ หรือลบพนักงานออกจากระบบได้")
st.write("___")
# Load existing employee data
if os.path.exists("employee_info.csv"):
    employee_df = pd.read_csv("employee_info.csv")
else:
    employee_df = pd.DataFrame(columns=["employee_id", "name", "Department"]) 

## View employees by department
st.subheader("🔍 List of employees by department")
st.caption("> รายชื่อพนักงานตามแผนก")

if not employee_df.empty:
    # Select department
    departments = ["All"] + sorted(employee_df["department"].dropna().unique().tolist())
    selected_dept = st.selectbox("Select department / เลือกแผนก", departments)

    # Filter based on selection
    if selected_dept == "All":
        filtered_df = employee_df
    else:
        filtered_df = employee_df[employee_df["department"] == selected_dept]

    # Employee table
    if not filtered_df.empty:
        st.dataframe(filtered_df.reset_index(drop=True).rename(lambda x: x + 1))
    else:
        st.warning("⚠️ There are no employees in this department. / ไม่มีพนักงานในแผนกนี้")
else:
    st.warning("⚠️ No employee information yet / ยังไม่มีข้อมูลพนักงาน") 

st.write("___")
## Add new employee
st.subheader("➕ Add new employee")
st.caption("> เพิ่มพนักงานใหม่")

with st.form("add_employee_form"):
    new_id = st.text_input("Employee ID (รหัสพนักงาน)")
    new_name = st.text_input("Name (ชื่อพนักงาน)")
    new_dept = st.text_input("Department (แผนก)")

    submitted = st.form_submit_button("✅ Add / เพิ่ม")

if submitted:
    if new_id and new_name and new_dept:
        # Check for duplicate employee_id
        if new_id in employee_df["employee_id"].values:
            st.warning("⚠️ This employee ID is taken! / รหัสพนักงานนี้มีอยู่แล้ว!")
        else:
            new_row = pd.DataFrame([{
                "employee_id": new_id,
                "name": new_name,
                "department": new_dept
            }])
            updated_df = pd.concat([employee_df, new_row], ignore_index=True)
            updated_df.to_csv("employee_info.csv", index=False)
            st.success("✅ Employee has been added! / เพิ่มพนักงานเรียบร้อยแล้ว!")
            st.rerun()
    else:
        st.error("❌ Please fill in all information completely / กรุณากรอกข้อมูลให้ครบถ้วน")

st.write("___")
## Delete employee
st.subheader("➖ Delete employee")
st.caption("> เลือกพนักงานที่คุณต้องการลบออกจากระบบ")

if not employee_df.empty:
    # Filter by department first
    del_dept = st.selectbox("Select department / เลือกแผนก", ["All"] + sorted(employee_df["department"].dropna().unique().tolist()), key="delete_dept")
    
    if del_dept == "All":
        df_to_delete_from = employee_df
    else:
        df_to_delete_from = employee_df[employee_df["department"] == del_dept]

    if not df_to_delete_from.empty:
        employee_options = df_to_delete_from["name"] + " (" + df_to_delete_from["employee_id"] + ")"
        selected_emp = st.selectbox("Select employee / เลือกพนักงาน", employee_options)

        confirm_delete = st.checkbox("⚠️ Please confirm that you want to delete this employee. / โปรดยืนยันว่าต้องการลบพนักงานคนนี้", key="confirm_delete")

        if st.button("❌ Delete / ลบ"):
            if confirm_delete:
                emp_id = selected_emp.split("(")[-1].replace(")", "").strip()
                updated_df = employee_df[employee_df["employee_id"] != emp_id]
                updated_df.to_csv("employee_info.csv", index=False)
                st.success("✅ Employee has been deleted. / ลบพนักงานเรียบร้อยแล้ว!")
                st.rerun()
            else:
                st.warning("Check to confirm before deleting data. / กรุณายืนยันก่อนลบข้อมูล")
    else:
        st.warning("⚠️ There are no employees in this department. / ไม่มีพนักงานในแผนกนี้")
else:
    st.warning("⚠️ No employee information yet / ยังไม่มีข้อมูลพนักงาน")
