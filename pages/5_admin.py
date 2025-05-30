import streamlit as st
import pandas as pd
import os

DEFAULT_CRITERIA_FILE = "criteria_config.csv"
CUSTOM_CRITERIA_FILE = "custom_criteria.csv"
OPEN_Q_FILE = "open_questions.csv"

# Initialize files if empty
def init_file(file_path, headers):
    if not os.path.exists(file_path) or os.path.getsize(file_path) == 0:
        pd.DataFrame(columns=headers).to_csv(file_path, index=False)

init_file(CUSTOM_CRITERIA_FILE, ["department", "criteria", "caption_eng", "caption_th"])
init_file(OPEN_Q_FILE, ["question_eng", "question_th"])

# Load data
@st.cache_data
def load_default_criteria():
    return pd.read_csv(DEFAULT_CRITERIA_FILE)

@st.cache_data
def load_custom_criteria():
    return pd.read_csv(CUSTOM_CRITERIA_FILE)

@st.cache_data
def load_open_questions():
    return pd.read_csv(OPEN_Q_FILE)

# Save functions
def save_custom_criteria(df):
    df.to_csv(CUSTOM_CRITERIA_FILE, index=False)

def save_open_questions(df):
    df.to_csv(OPEN_Q_FILE, index=False)

# === Admin UI ===
st.title("🛠️ Admin: Customize Questionnaire")

option = st.radio("Choose questionnaire base:", ["Use Default", "Use Custom"])

# === Criteria Section ===
if option == "Use Default":
    st.subheader("🔹 Default Criteria (Read-only)")
    st.dataframe(load_default_criteria(), use_container_width=True)

elif option == "Use Custom":
    st.subheader("🔹 Custom Criteria (Editable)")
    custom_df = load_custom_criteria()
    edited_df = st.data_editor(
        custom_df,
        use_container_width=True,
        num_rows="dynamic",
        key="custom_criteria_editor"
    )
    if st.button("💾 Save Custom Criteria"):
        save_custom_criteria(edited_df)
        st.success("Saved custom criteria.")

# === Open-ended Questions ===
st.subheader("✍️ Open-ended Questions")
open_q_df = load_open_questions()
edited_open_q_df = st.data_editor(
    open_q_df,
    use_container_width=True,
    num_rows="dynamic",
    key="open_ended_editor"
)
if st.button("💾 Save Open-ended Questions"):
    save_open_questions(edited_open_q_df)
    st.success("Saved open-ended questions.")
