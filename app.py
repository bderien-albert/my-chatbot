import streamlit as st

# =====================================
# PAGE SETUP
# =====================================

st.set_page_config(
    page_title="Knowledge Assistant",
    page_icon="albertschool_logo.jpg",
    layout="wide"
)

ADMIN_PASSWORD = "admin123"

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
            st.rerun()

# =====================================
# ADMIN LOGIN
# =====================================

if st.session_state.show_login:

    st.subheader("Administrator Login")

    password = st.text_input(
        "Password",
        type="password"
    )

    if st.button("Login"):

        if password == ADMIN_PASSWORD:

            st.session_state.admin_mode = True
            st.session_state.show_login = False

            st.success("Access Granted")
            st.rerun()

        else:

            st.error("Incorrect Password")

# =====================================
# SELECT CHAT MODE
# =====================================

if st.session_state.admin_mode:

    st.title("Administrator Assistant")
    messages = st.session_state.admin_messages

else:

    col1, col2 = st.columns([1, 6])

    with col1:
        st.image("albertschool_logo.jpg", width=100)

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

    with st.chat_message("assistant"):

        with st.spinner("Thinking..."):

            user_question_count = len(
                [m for m in messages if m["role"] == "user"]
            )

            if user_question_count == 1:

                answer = """
### Summary

- **Symptoms:** warning signs can include a persistent cough, unusual fatigue, unexplained weight loss, or symptoms that persist over time.

- **Screening:** early detection can significantly improve treatment outcomes and increase treatment options.

- **Examinations:** diagnosis may involve clinical assessment, imaging, laboratory testing, and biopsies depending on the situation.

- **Treatments:** common approaches include surgery, radiotherapy, chemotherapy, immunotherapy, and targeted therapies.

- **Prevention:** maintaining a healthy lifestyle and participating in recommended screenings are important preventive measures.

### Sources

- /joshua_smith_new_nanotech_to_catch_cancer_early_seg01.wav

- /joshua_smith_new_nanotech_to_catch_cancer_early_seg02.wav

- /joshua_smith_new_nanotech_to_catch_cancer_early_seg03.wav

If you have any feedback, feel free to share it with me.
"""

            else:

                answer = """
Sorry, I cannot answer this question.

However, **Clara Osborn, Chief of Finance**, may be able to assist you.

You can contact her at:

📧 c.osborn@gmail.com
"""

            st.markdown(answer)

    messages.append(
        {
            "role": "assistant",
            "content": answer
        }
    )