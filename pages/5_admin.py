import streamlit as st
import pandas as pd
import json
import os

st.header("🛠️ Admin Panel: Customize Evaluation Form")

CONFIG_FILE = "config.json"
CUSTOM_CRITERIA_FILE = "custom_criteria.csv"

DEPARTMENTS = ["Core", "Finance/Accounting", "HR", "IT", "Marketing", "Sales", "Operations"]
QUESTION_TYPES = ["rating", "numeric", "text"]  # ✅ เพิ่ม text เข้ามา

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

# Toggle custom form usage
use_custom = st.checkbox("Use custom evaluation form", value=config.get("use_custom", False))
config["use_custom"] = use_custom
save_config(config)

st.markdown("---")

if use_custom:
    st.subheader("✏️ Customize Criteria Questions")

    if os.path.exists(CUSTOM_CRITERIA_FILE):
        custom_df = pd.read_csv(CUSTOM_CRITERIA_FILE)
    else:
        custom_df = pd.DataFrame(columns=["department", "criteria", "caption_eng", "caption_th", "type"])

    # Ensure type column exists and is filled
    if "type" not in custom_df.columns:
        custom_df["type"] = "rating"
    else:
        custom_df["type"] = custom_df["type"].fillna("rating")

    edited_df = st.data_editor(
        custom_df,
        column_config={
            "department": st.column_config.SelectboxColumn(
                "Department",
                help="Select the department this question belongs to.",
                options=DEPARTMENTS,
                required=True,
            ),
            "criteria": st.column_config.TextColumn("Criteria (Key)", required=True),
            "caption_eng": st.column_config.TextColumn("English Caption"),
            "caption_th": st.column_config.TextColumn("Thai Caption"),
            "type": st.column_config.SelectboxColumn(
                "Type",
                help="Select question type: rating (1-5), numeric (e.g. KPI), or text (open-ended response)",
                options=QUESTION_TYPES,
                required=True,
            ),
        },
        use_container_width=True,
        num_rows="dynamic",
        key="custom_criteria_editor"
    )

    if st.button("💾 Save Custom Criteria"):
        edited_df.to_csv(CUSTOM_CRITERIA_FILE, index=False)
        st.success("✅ Custom criteria saved.")
