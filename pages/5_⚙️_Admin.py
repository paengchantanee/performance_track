import streamlit as st
import pandas as pd
import json
import os

st.header("🛠️ Admin Panel: Customize Evaluation Form")
st.caption("> ระบบแอดมิน: ปรับแต่งแบบประเมิน")

CONFIG_FILE = "config.json"
CUSTOM_CRITERIA_FILE = "custom_criteria.csv"

DEPARTMENTS = ["Core", "Finance/Accounting", "HR", "IT", "Marketing", "Sales", "Operations"]
QUESTION_TYPES = ["rating", "numeric", "text"]

# Load or initialize config
def load_config():
    if not os.path.exists(CONFIG_FILE):
        default_config = {"use_custom": False}
        with open(CONFIG_FILE, "w") as f:
            json.dump(default_config, f)
    with open(CONFIG_FILE, "r") as f:
        return json.load(f)

def save_config(config):
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f)

config = load_config()

# Toggle custom
use_custom = st.checkbox("Click if you want to custom evaluation form/ คลิกเมื่อต้องการใช้แบบประเมินที่ปรับแต่งเอง", value=config.get("use_custom", False))
config["use_custom"] = use_custom
save_config(config)

st.markdown("---")

# Show default criteria
with st.expander("📋 View Default Evaluation Criteria / ดูเกณฑ์ประเมินเริ่มต้น"):
    if os.path.exists("criteria_config.csv"):
        default_df = pd.read_csv("criteria_config.csv")
        
        # Dropdown for department selection
        selected_dept = st.selectbox("Select department to view / เลือกแผนก", ["All"] + DEPARTMENTS)

        # Filter by selected department
        if selected_dept != "All":
            filtered_df = default_df[default_df["department"] == selected_dept]
            filtered_df.index = range(1, len(filtered_df) + 1)
        else:
            filtered_df = default_df

        default_df.index = range(1, len(default_df) + 1)
        st.dataframe(filtered_df, use_container_width=True)
    else:
        st.warning("⚠️ Default criteria file (criteria_config.csv) not found. / ไม่พบเจอไฟล์ criteria_config.csv")

# Customize criteria
if use_custom:
    st.subheader("✏️ Customize Criteria Questions")
    st.caption("> ปรับแต่งแบบประเมิน สามารถเพิ่มหรือลบคำถามได้")
    st.info("> หมายเหตุ: เมื่อเลือกคำถามเชิงตัวเลข (numeric) สามารถใส่ target หรือค่าเป้าหมายได้")

    if os.path.exists(CUSTOM_CRITERIA_FILE):
        custom_df = pd.read_csv(CUSTOM_CRITERIA_FILE)
    else:
        custom_df = pd.DataFrame(columns=["department", "criteria", "caption_eng", "caption_th", "type"])

    if "type" not in custom_df.columns:
        custom_df["type"] = "rating"
    else:
        custom_df["type"] = custom_df["type"].fillna("rating")

    edited_df = st.data_editor(
        custom_df,
        column_config={
            "department": st.column_config.SelectboxColumn(
                "Department",
                help="Select the department this question belongs to. / เลือกแผนก",
                options=DEPARTMENTS,
                required=True,
            ),
            "criteria": st.column_config.TextColumn("Criteria (Key)", required=True),
            "caption_eng": st.column_config.TextColumn("English Caption"),
            "caption_th": st.column_config.TextColumn("Thai Caption"),
            "type": st.column_config.SelectboxColumn(
                "Type",
                help="Select question type / เลือกประเภทของคำถาม: rating (1-5), numeric (e.g. KPI), or text (open-ended response / คำถามแบบปลายเปิด)",
                options=QUESTION_TYPES,
                required=True,
            ),
        },
        use_container_width=True,
        num_rows="dynamic",
        key="custom_criteria_editor"
    )

    if st.button("💾 Save Custom Criteria/ บันทึกแบบประเมิน"):
        edited_df.to_csv(CUSTOM_CRITERIA_FILE, index=False)
        st.success("✅ Custom criteria saved/ บันทึกสำเร็จ")
