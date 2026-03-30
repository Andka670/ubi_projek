import streamlit as st

if "login" in st.session_state and st.session_state.login:
    role = st.session_state.get("role")

    if role == "admin":
        st.switch_page("pages/admin.py")
    elif role == "kasir":
        st.switch_page("pages/kasir.py")
    else:
        st.switch_page("pages/login.py")
else:
    st.switch_page("pages/login.py")