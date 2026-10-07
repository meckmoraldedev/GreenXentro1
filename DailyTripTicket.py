import datetime
import streamlit as st

# Page Configuration
st.set_page_config(
    page_title="GreenXentro - Daily Trip Ticket",
    page_icon="🚗",
    layout="centered",
)

# Initialize Session State for Authentication
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""


def login_screen():
    st.markdown(
        "<h2 style='text-align: center;'>GreenXentro Fleet Portal</h2>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<p style='text-align: center; color: gray;'>Please sign in to access the Daily Trip Ticket</p>",
        unsafe_allow_html=True,
    )

    with st.form("login_form"):
        username = st.text_input("Username / Email")
        password = st.text_input("Password", type="password")
        submit_btn = st.form_submit_button("Sign In", use_container_width=True)

        if submit_btn:
            # Simple authentication check (replace with your secure backend logic or DB lookup)
            if username and password:  # Add your specific credential validation here
                st.session_state.logged_in = True
                st.session_state.username = username
                st.rerun()
            else:
                st.error("Please enter valid credentials.")


def trip_ticket_form():
    # Header Banner or Title
    st.markdown("### 🌿 GreenXentro Daily Trip Ticket (Depot)")
    st.write(f"Logged in as: **{st.session_state.username}**")

    if st.button("Sign Out", type="secondary"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.rerun()

    st.markdown("---")

    with st.form("trip_ticket_form"):
        # Email field defaults to logged in user if applicable
        email = st.text_input("Email *", value=st.session_state.username)

        status = st.radio("Status *", ["Sign in", "Sign out"], horizontal=True)

        name = st.text_input(
            "Name (Last name, First name, Middle initial) *"
        )

        sap_id = st.text_input("SAP ID *")

        plate_no = st.text_input("Plate no. *")

        schedule_options = [
            "4am ~ 1pm",
            "5am ~ 2pm",
            "6am ~ 3pm",
            "7am ~ 4pm",
            "8am ~ 5pm",
            "9am ~ 6pm",
            "10am ~ 7pm",
            "11am ~ 8pm",
            "12am ~ 9pm",
            "1pm ~ 10pm",
            "2pm ~ 11pm",
        ]
        schedule_of_duty = st.selectbox(
            "Schedule of Duty *", schedule_options
        )

        battery_pct = st.number_input(
            "Battery % *", min_value=0, max_value=100, step=1
        )

        odometer = st.number_input(
            "Odometer *", min_value=0.0, format="%.2f", step=1.0
        )

        team = st.selectbox(
            "Team *", ["Team Benjo", "Team Ruel", "Team Bacor", "Team Hannah"]
        )

        dispatcher = st.selectbox(
            "Dispatcher (sino nagbigay ng susi / kanino sinoli) *",
            ["Joshua", "April", "Karl", "Jhun", "Colobong", "Lazo"],
        )

        submitted = st.form_submit_button("Submit", use_container_width=True)

        if submitted:
            if not name or not sap_id or not plate_no:
                st.warning("Please fill out all required fields.")
            else:
                # Here you can add code to save responses to a database, Google Sheet, or CSV file.
                submission_data = {
                    "Timestamp": datetime.datetime.now().strftime(
                        "%Y-%m-%d %H:%M:%S"
                    ),
                    "Email": email,
                    "Status": status,
                    "Name": name,
                    "SAP ID": sap_id,
                    "Plate No": plate_no,
                    "Schedule": schedule_of_duty,
                    "Battery %": battery_pct,
                    "Odometer": odometer,
                    "Team": team,
                    "Dispatcher": dispatcher,
                }

                st.success(
                    "Trip ticket submitted successfully! A copy of your response has been logged."
                )
                # You can inspect the submitted dict or log it:
                # st.json(submission_data)


# Main Flow Controller
if not st.session_state.logged_in:
    login_screen()
else:
    trip_ticket_form()