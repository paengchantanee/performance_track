import streamlit as st
import pandas as pd
import json
import os

st.header("🛠️ Admin Panel: Customize Evaluation Form")

CONFIG_FILE = "config.json"
CUSTOM_CRITERIA_FILE = "custom_criteria.csv"
OPEN_QUESTIONS_FILE = "open_questions.csv"

DEPARTMENTS = ["Core", "Finance", "HR", "IT", "Marketing", "Sales", "Operations"]

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
        custom_df = pd.DataFrame(columns=["department", "criteria", "caption_eng", "caption_th"])

    # Render editable table with dropdown for department
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
        },
        use_container_width=True,
        num_rows="dynamic",
        key="custom_criteria_editor"
    )

    if st.button("💾 Save Custom Criteria"):
        edited_df.to_csv(CUSTOM_CRITERIA_FILE, index=False)
        st.success("✅ Custom criteria saved.")

    st.markdown("---")

    st.subheader("📝 Customize Open-Ended Questions")

    if os.path.exists(OPEN_QUESTIONS_FILE):
        open_df = pd.read_csv(OPEN_QUESTIONS_FILE)
    else:
        open_df = pd.DataFrame(columns=["department", "question_eng", "question_th"])

    edited_open_q = st.data_editor(
        open_df,
        use_container_width=True,
        num_rows="dynamic",
        key="open_questions_editor"
    )

    if st.button("💾 Save Open-Ended Questions"):
        edited_open_q.to_csv(OPEN_QUESTIONS_FILE, index=False)
        st.success("✅ Open-ended questions saved.")
