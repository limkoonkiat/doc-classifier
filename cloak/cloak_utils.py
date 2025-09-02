import streamlit as st
from logic.submit_handler import clean_text_for_markdown
from cloak.cloak_requests import cloak_it


def display_cloak_setting(name, default_toggle=True, default_technique="Replace"):

    with st.expander(name):
        st.toggle("Enable", key=f"toggle_{name.lower()}", value=default_toggle)

        techniques = ["Alias", "Mask", "Redact", "Replace"]
        st.selectbox(
            "Technique", techniques, key=f"technique_{name.lower()}", index=techniques.index(default_technique))

        if st.session_state.get(f"technique_{name.lower()}") == "Alias":
            # No additional settings for Alias for now
            pass
        elif st.session_state.get(f"technique_{name.lower()}") == "Mask":
            st.text_input("Masking Character", value="*",
                          key=f"mask_char_{name.lower()}", max_chars=1)
            st.number_input("Masking Length", min_value=1, value=1,
                            key=f"mask_length_{name.lower()}")
            st.checkbox("Prefix", value=False,
                        key=f"mask_prefix_{name.lower()}")
        elif st.session_state.get(f"technique_{name.lower()}") == "Redact":
            # No additional settings for Redact for now
            pass
        elif st.session_state.get(f"technique_{name.lower()}") == "Replace":
            st.text_input(
                "Replace with", value=f"<{name}>", key=f"replace_text_{name.lower()}")


def display_cloak_section():
    st.subheader("Cloak It!")
    st.write("You can use Govtech's Cloak to mask specific Personally Identifiable Information (PII) in the text to potentially lower the security and/or sensitivity classifications.")

    with st.expander("Cloak Settings"):
        tab1, tab2, tab3, tab4 = st.tabs(
            ["Personal", "Financial", "Technical Security", "Other"])
        with tab1:
            display_cloak_setting("Name")
            display_cloak_setting("NRIC")
            display_cloak_setting("Email Address")
            display_cloak_setting("Phone Number")
            display_cloak_setting(
                "Nationality/Race/Religion", default_toggle=False)
            display_cloak_setting("Full Address")
            display_cloak_setting("Street")
            display_cloak_setting("Postal Code")
            display_cloak_setting("Unit Number")
            display_cloak_setting("Country", default_toggle=False)
        with tab2:
            display_cloak_setting("Currency", default_toggle=False)
            display_cloak_setting("Credit Card")
            display_cloak_setting("SG Bank Account Number")
            display_cloak_setting("Intl. Bank Account Number")
        with tab3:
            display_cloak_setting("IP Address", default_toggle=False)
            display_cloak_setting("URL", default_toggle=False)
        with tab4:
            display_cloak_setting("Date and Time", default_toggle=False)
            display_cloak_setting("UEN", default_toggle=False)

    st.button("Cloak my text!", key="pressed_cloak")

    with st.container():
        if st.session_state.get("pressed_cloak"):
            with st.container(border=True):
                cloak_text = cloak_it(
                    st.session_state.get("text_input", ""))
                st.write(clean_text_for_markdown(cloak_text))
