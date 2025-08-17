import streamlit as st
import hmac

def check_password():
    def password_entered():
        if hmac.compare_digest(st.session_state["password"], st.secrets["password"]):
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False
    if st.session_state.get("password_correct", False):
        return True
    st.text_input("Password", type="password", key="password", on_change=password_entered)
    if "password_correct" in st.session_state:
        st.error("Password incorrect")
    return False
