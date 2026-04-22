import streamlit as st

st.set_page_config(page_title="Basic Streamlit App", page_icon="✨", layout="centered")

st.title("Basic Streamlit App")
st.write("Welcome! This is a simple Streamlit application.")

st.markdown("## Inputs")
name = st.text_input("What is your name?", value="")
age = st.slider("How old are you?", min_value=0, max_value=120, value=25)

st.markdown("## Preferences")
color = st.selectbox("Choose your favorite color:", ["Blue", "Green", "Red", "Yellow", "Purple"])
likes_streamlit = st.checkbox("I like Streamlit", value=True)

if st.button("Submit"):
    st.success(f"Hi {name or 'there'}! You are {age} years old and like {color}.")
    if likes_streamlit:
        st.info("Great! Streamlit makes building apps fast.")
    else:
        st.warning("No worries — Streamlit can still be fun to explore.")

st.markdown("---")
st.write("This app demonstrates basic Streamlit widgets: text input, slider, selectbox, checkbox, and button.")
