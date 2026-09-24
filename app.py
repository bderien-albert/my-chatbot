import streamlit as st
from openai import OpenAI


# python -m streamlit run app.py


API_KEY = st.secrets["API_KEY"]


BASE_URL = "https://dss-186181c0-20d9f059-dku.eu-west-3.app.dataiku.io/public/api/projects/NOUVEAU/llms/openai/v1/"


USER_MODEL = "agent:9nBHrFOO"
ADMIN_MODEL = "agent:Ab77Rma6"


ADMIN_PASSWORD = "admin123"


# =====================================
# OPENAI CLIENT
# =====================================


client = OpenAI(
    api_key=API_KEY,
    base_url=BASE_URL
)


# =====================================
# PAGE SETUP
# =====================================


st.set_page_config(
    page_title="Knowledge Assistant",
    page_icon="albertschool_logo.jpg",
    layout="wide"
)

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
    selected_model = ADMIN_MODEL


else:

    col1, col2 = st.columns([1, 6])

    with col1:
        st.image("albertschool_logo.jpg", width=100)

    with col2:
        st.title("What's on your mind today?")

    messages = st.session_state.user_messages
    selected_model = USER_MODEL


# python -m streamlit run app.py


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


            try:


                response = client.responses.create(
                    model=selected_model,
                    input=prompt
                )


                answer = response.output_text


            except Exception as e:


                answer = f"Error: {str(e)}"


            st.markdown(answer)


    messages.append(
        {
            "role": "assistant",
            "content": answer
        }
    )
