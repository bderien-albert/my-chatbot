import streamlit as st
import time
from pathlib import Path

# =====================================
# PAGE SETUP
# =====================================

# Resolve the logo next to this file, so it works no matter which folder
# the terminal is in when you run `streamlit run app.py`
LOGO_PATH = Path(__file__).parent / "albertschool_logo.jpg"
LOGO = str(LOGO_PATH) if LOGO_PATH.exists() else None

st.set_page_config(
    page_title="Knowledge Assistant",
    page_icon=LOGO or "📚",
    layout="wide"
)

ADMIN_PASSWORD = "admin123"

# =====================================
# CANNED ANSWERS
# =====================================

CANCER_ANSWER = """
Summary:

The symptoms can include changes in bowel habits, a persistent cough, or a changing mole. These symptoms do not necessarily mean cancer, but they warrant medical advice if they persist.

* Screening: detecting certain cancers early can improve treatment options. The conference found emphasizes the importance of early diagnosis: in its example of breast cancer, it indicates a five-year survival rate close to 100% for treatment at stage 1, compared with 22% at stage 4 (00:00–00:01). However, these figures depend on the country, tumor subtype, and available treatments.
* Examinations: depending on the situation, doctors may use a clinical examination, imaging, biological tests, and often a biopsy to confirm the diagnosis and determine the type of tumor.
* Treatments: these can include surgery, radiotherapy, chemotherapy, hormone therapy, targeted therapies, immunotherapy, stem cell transplantation, or supportive care. The choice depends on the cancer, its stage, and the individual.
* Prevention: not smoking, limiting alcohol, protecting the skin from the sun, maintaining physical activity and a balanced diet, getting vaccinated when recommended (particularly HPV and hepatitis B), and participating in recommended screening programs.
* Research: the source describes research into “liquid biopsy,” which looks for biomarkers in blood, urine, or saliva, particularly exosomes. This is a promising area of research, but these tools do not necessarily replace standard screening and diagnostic methods (00:01–00:03).

A cancer diagnosis is not automatically a death sentence: prognosis varies greatly depending on the type, stage, and response to treatment. For personal concerns or symptoms, it is important to consult a healthcare professional rather than relying on general information.

Sources:

* `/joshua_smith_new_nanotech_to_catch_cancer_early_seg01.wav`
* `/joshua_smith_new_nanotech_to_catch_cancer_early_seg02.wav`
* `/joshua_smith_new_nanotech_to_catch_cancer_early_seg03.wav`

If you have any feedback, feel free to share them with me.
"""

ESCALATION_ANSWER = """
Sorry, I cannot answer this question.

However, **Clara Osborn, Chief of Finance**, may be able to assist you.

You can contact her at:

📧 [c.osborn@gmail.com](mailto:c.osborn@gmail.com)
"""

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

def pick_answer(question_number, admin):

    if admin:
        if question_number == 1:
            return CONTACT_SAVED_ANSWER
        if question_number == 2:
            return ANALYTICS_ANSWER
        return ADMIN_STATUS_ANSWER

    if question_number == 1:
        return CANCER_ANSWER
    return ESCALATION_ANSWER

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

    answer = pick_answer(question_number, st.session_state.admin_mode)

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
