import streamlit as st

st.set_page_config(page_title="Basic Calculator", page_icon="F", layout="centered")

st.title("🧮 Basic Calculator")

# Initialize session state for the calculator
if 'expression' not in st.session_state:
    st.session_state.expression = ""

# Function to update expression
def update_expression(value):
    st.session_state.expression += str(value)

def clear_expression():
    st.session_state.expression = ""

def calculate():
    try:
        result = eval(st.session_state.expression)
        st.session_state.expression = str(result)
    except:
        st.session_state.expression = "Error"

# Display the current expression
st.text_input("Expression", value=st.session_state.expression, key="display", disabled=True)

# Create buttons
col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("7"):
        update_expression("7")
    if st.button("4"):
        update_expression("4")
    if st.button("1"):
        update_expression("1")
    if st.button("0"):
        update_expression("0")

with col2:
    if st.button("8"):
        update_expression("8")
    if st.button("5"):
        update_expression("5")
    if st.button("2"):
        update_expression("2")
    if st.button("."):
        update_expression(".")

with col3:
    if st.button("9"):
        update_expression("9")
    if st.button("6"):
        update_expression("6")
    if st.button("3"):
        update_expression("3")
    if st.button("="):
        calculate()

with col4:
    if st.button("+"):
        update_expression("+")
    if st.button("-"):
        update_expression("-")
    if st.button("*"):
        update_expression("*")
    if st.button("/"):
        update_expression("/")
    if st.button("C"):
        clear_expression()

st.markdown("---")
st.write("This is a basic calculator. Enter numbers and operators, then press = to calculate.")