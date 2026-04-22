import streamlit as st

st.set_page_config(page_title="My Portfolio", page_icon="BioI", layout="wide")

st.title("The BioInnovators Toolkit")

st.markdown("""
Welcome to my portfolio of Streamlit apps! This is a collection of mini-applications I've built to accelerate the biodesign process.

Navigate using the sidebar to explore different apps.
""")

st.markdown("## Available Apps")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### 🧮 Basic Calculator")
    st.write("A simple calculator for basic arithmetic operations.")
    st.page_link("pages/calculator.py", label="Open Calculator", icon="🧮")

with col2:
    st.markdown("### 🎨 Choose Favorite Color")
    st.write("Select and display your favorite color.")
    st.page_link("pages/favorite_color.py", label="Choose Color", icon="🎨")

st.markdown("---")
st.write("More apps coming soon!")
