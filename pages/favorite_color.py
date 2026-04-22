import streamlit as st

st.set_page_config(page_title="Choose Favorite Color", page_icon="🎨", layout="centered")

st.title("🎨 Choose Your Favorite Color")

st.markdown("Select your favorite color from the options below:")

color = st.selectbox("Favorite Color:", ["Blue", "Green", "Red", "Yellow", "Purple", "Orange", "Pink", "Black", "White"])

if color:
    st.success(f"Your favorite color is {color}!")
    
    # Display a colored box or something
    st.markdown(f"""
    <div style="background-color: {color.lower()}; padding: 20px; border-radius: 10px; color: white;">
        <h3>This is {color}!</h3>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")
st.write("This app lets you choose and display your favorite color.")