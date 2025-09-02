import streamlit as st


def get_color(classification):
    classification = classification.split("(")[0].strip()
    colors = {
        "Class Light Green": "LightGreen",
        "Class Dark Green": "DarkGreen",
        "Class Blue": "Blue",
        "Class Yellow": "Yellow",
        "Class Orange": "Orange",
        "Class Red": "Red",
        "Class Black": "Black",
        "S1": "LightGray",
        "S2": "SlateGray",
        "S3": "DarkSlateGray"
    }


def set_stcode_style():
    return st.markdown(
        """
    <style>
    pre, code, .stCode, .stMarkdown pre {
        font-family: system-ui, -apple-system, BlinkMacSystemFont,
                     "Segoe UI", Roboto, Oxygen-Sans, Ubuntu, Cantarell,
                     "Helvetica Neue", sans-serif !important;
        font-size: 0.875rem
    }
    </style>
    """,
        unsafe_allow_html=True
    )


def create_custom_divider(mode):
    if mode == "both":
        return st.markdown(f"""
                <hr style="
                height:10px;
                border:none;
                margin: 0;
                background:linear-gradient(to right, {get_color(st.session_state.get("security_classification", "none"))}, {get_color(st.session_state.get("sensitivity_classification", "none"))});
                ">
                """, unsafe_allow_html=True)
    elif mode == "security":
        return st.markdown(f"""
                    <hr style="height:10px;
                    margin: 0;
                   background: {get_color(st.session_state.get("security_classification", "none"))}">
                    """, unsafe_allow_html=True)
    elif mode == "sensitivity":
        return st.markdown(f"""
                    <hr style="height:10px;
                    margin: 0;
                   background: {get_color(st.session_state.get("sensitivity_classification", "none"))}">
                    """, unsafe_allow_html=True)
