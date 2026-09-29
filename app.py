import streamlit as st
import pandas as pd
import csv
import time
from datetime import datetime
from pathlib import Path

# =====================================
# PAGE SETUP
# =====================================

BASE_DIR = Path(__file__).parent

# Resolve the logo next to this file, so it works no matter which folder
# the terminal is in when you run `streamlit run app.py`
LOGO_PATH = BASE_DIR / "albertschool_logo.jpg"
LOGO = str(LOGO_PATH) if LOGO_PATH.exists() else None

st.set_page_config(
    page_title="Knowledge Assistant",
    page_icon=LOGO or "📚",
    layout="wide"
)

ADMIN_PASSWORD = "admin123"

# =====================================
# DATASETS (CSV files in the "data" folder)
# =====================================

DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

QUESTIONS_CSV = DATA_DIR / "questions.csv"
FEEDBACK_CSV = DATA_DIR / "feedback.csv"

QUESTION_FIELDS = [
    "question_id", "question", "topic", "answered",
    "times_asked", "first_asked", "last_asked", "intent"
]
FEEDBACK_FIELDS = ["feedback_id", "timestamp", "feedback", "category"]


def load_rows(path):
    if not path.exists():
        return []
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def save_rows(path, rows, fields):
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def now():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def log_question(question, intent, topic, answered):
    """Add a question to the dataset, or bump the counter if the same
    question (same intent) was already asked, so it is never duplicated."""

    rows = load_rows(QUESTIONS_CSV)

    for row in rows:
        if row["intent"] == intent:
            row["times_asked"] = str(int(row["times_asked"]) + 1)
            row["last_asked"] = now()
            save_rows(QUESTIONS_CSV, rows, QUESTION_FIELDS)
            return

    rows.append({
        "question_id": f"Q-{len(rows) + 1:03d}",
        "question": question,
        "topic": topic,
        "answered": answered,
        "times_asked": "1",
        "first_asked": now(),
        "last_asked": now(),
        "intent": intent,
    })
    save_rows(QUESTIONS_CSV, rows, QUESTION_FIELDS)


PRAISE_WORDS = ["great", "thanks", "thank you", "love", "helpful", "perfect", "good job"]
SUGGESTION_WORDS = ["could you", "would be nice", "suggest", "please add", "maybe", "it would"]


def classify_feedback(text):
    lowered = text.lower()
    if any(w in lowered for w in PRAISE_WORDS):
        return "praise"
    if any(w in lowered for w in SUGGESTION_WORDS):
        return "suggestion"
    return "complaint"


def log_feedback(text):
    rows = load_rows(FEEDBACK_CSV)
    category = classify_feedback(text)
    rows.append({
        "feedback_id": f"FB-{len(rows) + 1:03d}",
        "timestamp": now(),
        "feedback": text,
        "category": category,
    })
    save_rows(FEEDBACK_CSV, rows, FEEDBACK_FIELDS)
    return category


# =====================================
# RECORDINGS & CONTACT
# =====================================

# Recording A (Joshua Smith, part 1)
REC_A = "joshua_smith_new_nanotech_to_catch_cancer_early_seg01.wav"
REC_A_TIME = "00:00"

# Recording B (Joshua Smith, part 2)
REC_B = "joshua_smith_new_nanotech_to_catch_cancer_early_seg02.wav"
REC_B_TIME = "00:01"

# Answer #1 cites both parts of Joshua's talk
REC_A2 = REC_B
REC_A2_TIME = REC_B_TIME

# Contact for questions the recordings can't answer
CONTACT_NAME = "Clara Osborn, Chief of Finance"
CONTACT_EMAIL = "c.osborn@gmail.com"

# =====================================
# CHAT ASSISTANT ANSWERS (normal user)
# =====================================

CONTACT_LINE = f"You can reach **{CONTACT_NAME}** at 📧 [{CONTACT_EMAIL}](mailto:{CONTACT_EMAIL})."

# 1, 4, 7: summary of Joshua's points, only what is in the recording
JOSHUA_SUMMARY = f"""
Here is a short summary of Joshua Smith's points on cancer:

* **Early diagnosis matters.** Using breast cancer as an example, he explains that the five-year survival rate is close to 100% when it is treated at stage 1, compared with 22% at stage 4.
* **Liquid biopsy research.** He describes research into "liquid biopsy", which looks for biomarkers, particularly exosomes, in blood, urine, or saliva to catch cancer earlier.

**Sources:**

* `{REC_A}` at {REC_A_TIME}
* `{REC_A2}` at {REC_A2_TIME}
"""

# 2: no information + contact
NO_INFO_ANSWER = f"""
I don't have information about this in the recordings.

{CONTACT_LINE}
"""

# 3: combines both recordings
COMBINED_ANSWER = f"""
Here is what the two recordings say together:

* **The problem (recording A):** catching cancer early changes outcomes. For breast cancer, the five-year survival rate is close to 100% when treated at stage 1, versus 22% at stage 4 (`{REC_A}` at {REC_A_TIME}).
* **The proposed solution (recording B):** "liquid biopsy" research looks for biomarkers, particularly exosomes, in blood, urine, or saliva, which could help detect cancer at those earlier stages (`{REC_B}` at {REC_B_TIME}).

Together, the recordings explain why early detection matters and how new research aims to make it easier.

**Sources:**

* `{REC_A}` at {REC_A_TIME}
* `{REC_B}` at {REC_B_TIME}
"""

# 5: refusal about revenue + contact
REVENUE_REFUSAL = f"""
I can only answer from the company's recordings, and they don't contain revenue figures.

{CONTACT_LINE}
"""

# 6: feedback
FEEDBACK_THANKS = """
Thanks for your feedback, it has been recorded.
"""

# The scripted order of answers. "kind" decides which dataset gets the row.
JOSHUA_STEP = {
    "kind": "question",
    "answer": JOSHUA_SUMMARY,
    "intent": "cancer_early_detection",
    "topic": "Cancer – early detection (Joshua Smith)",
    "answered": "yes",
}

USER_SCRIPT = [
    JOSHUA_STEP,                                            # 1
    {                                                       # 2
        "kind": "question",
        "answer": NO_INFO_ANSWER,
        "intent": "not_in_recordings",
        "topic": "Not covered by recordings (escalated)",
        "answered": "no",
    },
    {                                                       # 3
        "kind": "question",
        "answer": COMBINED_ANSWER,
        "intent": "combined_recordings",
        "topic": "Cross-recording question",
        "answered": "yes",
    },
    JOSHUA_STEP,                                            # 4 (vague wording)
    {                                                       # 5
        "kind": "question",
        "answer": REVENUE_REFUSAL,
        "intent": "revenue",
        "topic": "Revenue (out of scope, escalated)",
        "answered": "no",
    },
    {                                                       # 6
        "kind": "feedback",
        "answer": FEEDBACK_THANKS,
    },
    JOSHUA_STEP,                                            # 7 (same as #1)
]

# After the scripted steps, anything else gets the "no information" answer
FALLBACK_STEP = USER_SCRIPT[1]

# =====================================
# ADMIN ANSWERS
# =====================================

CONTACT_SAVED_ANSWER = """
✅ **Contact has been saved to the database.**

**Reference ID:** `CNT-28471`

The contact information has been successfully indexed and is now available in the internal knowledge base.
"""

ANALYTICS_ANSWER = """
### 📊 Usage Analytics — Last 30 days

**Most common topic:** Cancer Awareness & Early Detection

| Rank | Topic | Share of queries |
|---|---|---|
| 1 | Cancer Awareness & Early Detection | 42% |
| 2 | Finance & Budget requests (escalated) | 23% |
| 3 | Company & HR information | 18% |
| 4 | Other | 17% |

**Most referenced sources:**

* `/joshua_smith_new_nanotech_to_catch_cancer_early_seg01.wav` — 128 citations
* `/joshua_smith_new_nanotech_to_catch_cancer_early_seg02.wav` — 97 citations
* `/joshua_smith_new_nanotech_to_catch_cancer_early_seg03.wav` — 64 citations

**Insights:**

* Questions about early symptoms and screening are the main driver of usage.
* Finance-related questions are consistently escalated to Clara Osborn.
* Consider adding more documents on prevention to improve coverage.

**System status:**

* ✅ Database operational
* ✅ KB synchronization successful
"""

ADMIN_STATUS_ANSWER = """
### 🛠️ Administrator Dashboard

* ✅ Database: **operational**
* ✅ Knowledge base: **synchronized** (last sync: 2 minutes ago)
* ✅ Indexed documents: **1,284**
* ✅ Active users today: **57**
* ✅ Average response time: **1.4 s**

No issues detected. All systems are running normally.
"""

# =====================================
# SESSION VARIABLES
# =====================================

if "admin_mode" not in st.session_state:
    st.session_state.admin_mode = False

if "show_login" not in st.session_state:
    st.session_state.show_login = False

if "user_messages" not in st.session_state:
    st.session_state.user_messages = []

if "admin_messages" not in st.session_state:
    st.session_state.admin_messages = []

# =====================================
# SIDEBAR
# =====================================

with st.sidebar:

    st.title("Navigation")

    if not st.session_state.admin_mode:

        if st.button("⚙️ Administration"):
            st.session_state.show_login = True

    else:

        st.success("Admin Mode Active")

        if st.button("🚪 Logout Admin"):
            st.session_state.admin_mode = False
            st.session_state.show_login = False
            st.rerun()

    # Start the demo over: clears both chats and both datasets
    if st.button("🔄 Reset demo"):
        st.session_state.user_messages = []
        st.session_state.admin_messages = []
        QUESTIONS_CSV.unlink(missing_ok=True)
        FEEDBACK_CSV.unlink(missing_ok=True)
        st.rerun()

# =====================================
# ADMIN LOGIN
# =====================================

if st.session_state.show_login and not st.session_state.admin_mode:

    st.subheader("Administrator Login")

    password = st.text_input(
        "Password",
        type="password"
    )

    col_login, col_cancel = st.columns([1, 8])

    with col_login:
        login_clicked = st.button("Login")

    with col_cancel:
        if st.button("Cancel"):
            st.session_state.show_login = False
            st.rerun()

    if login_clicked:

        if password == ADMIN_PASSWORD:

            st.session_state.admin_mode = True
            st.session_state.show_login = False
            st.rerun()

        else:

            st.error("Incorrect Password")

    # Hide the chat while the login screen is shown
    st.stop()

# =====================================
# SELECT CHAT MODE
# =====================================

if st.session_state.admin_mode:

    st.title("Administrator Assistant")
    messages = st.session_state.admin_messages

else:

    col1, col2 = st.columns([1, 6])

    with col1:
        if LOGO:
            st.image(LOGO, width=100)

    with col2:
        st.title("What's on your mind today?")

    messages = st.session_state.user_messages

# =====================================
# DISPLAY CHAT HISTORY
# =====================================

for msg in messages:

    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# =====================================
# PICK THE ANSWER
# =====================================

def pick_admin_answer(question_number):

    if question_number == 1:
        return CONTACT_SAVED_ANSWER
    if question_number == 2:
        return ANALYTICS_ANSWER
    return ADMIN_STATUS_ANSWER


def pick_user_step(question_number):

    if question_number <= len(USER_SCRIPT):
        return USER_SCRIPT[question_number - 1]
    return FALLBACK_STEP

# =====================================
# USER INPUT
# =====================================

prompt = st.chat_input("Type your message...")

if prompt:

    messages.append(
        {
            "role": "user",
            "content": prompt
        }
    )

    with st.chat_message("user"):
        st.markdown(prompt)

    question_number = len(
        [m for m in messages if m["role"] == "user"]
    )

    step = None

    if st.session_state.admin_mode:
        answer = pick_admin_answer(question_number)
    else:
        step = pick_user_step(question_number)
        answer = step["answer"]

    with st.chat_message("assistant"):

        # 1. Pause with the spinner
        with st.spinner("Searching knowledge base..."):
            time.sleep(1.5)

        # 2. Type the answer out (outside the spinner, word by word)
        placeholder = st.empty()
        displayed_text = ""

        for word in answer.split(" "):
            displayed_text += word + " "
            placeholder.markdown(displayed_text + "▌")
            time.sleep(0.02)

        placeholder.markdown(answer)

    messages.append(
        {
            "role": "assistant",
            "content": answer
        }
    )

    # 3. Write to the datasets (normal user only)
    if step is not None:

        if step["kind"] == "feedback":
            category = log_feedback(prompt)
            st.toast(f"New row added to the feedback dataset ({category})", icon="📝")

        else:
            log_question(prompt, step["intent"], step["topic"], step["answered"])

# =====================================
# DATASETS VIEW (bottom of the sidebar)
# =====================================

with st.sidebar:

    st.divider()
    st.subheader("📁 Datasets")

    st.caption("Questions dataset")
    question_rows = load_rows(QUESTIONS_CSV)
    if question_rows:
        st.dataframe(
            pd.DataFrame(question_rows)[
                ["question_id", "question", "topic", "answered", "times_asked"]
            ],
            hide_index=True,
        )
    else:
        st.write("No questions yet.")

    st.caption("Feedback dataset")
    feedback_rows = load_rows(FEEDBACK_CSV)
    if feedback_rows:
        st.dataframe(
            pd.DataFrame(feedback_rows)[
                ["feedback_id", "feedback", "category"]
            ],
            hide_index=True,
        )
    else:
        st.write("No feedback yet.")
