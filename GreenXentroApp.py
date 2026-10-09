import datetime
import pandas as pd
import streamlit as st

# Page Configuration
st.set_page_config(
    page_title="GreenXentro - Fleet Portal",
    page_icon="🚗",
    layout="centered",
)

# Initialize Session State
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "current_page" not in st.session_state:
    st.session_state.current_page = "login"  # "login", "initial_setup", "forgot_password", "trip_ticket"
if "failed_attempts" not in st.session_state:
    st.session_state.failed_attempts = 0
if "user_data" not in st.session_state:
    st.session_state.user_data = {}

# Employee Database / Record Store (Replace with your SQL Server backend lookup)
SHEET_ID = "10Ju2dEKjMwZwOvgFym6R9Raonom5TNWk-ampJeOIlQg"
SHEET_NAME = "Sheet1"  # Change if your tab has a different name
url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={SHEET_NAME}"

@st.cache_data(ttl=60)
def load_employee_data():
  # dtype=str forces everything to string, .fillna("") turns blank cells into empty strings
  df = pd.read_csv(url, dtype=str).fillna("")
  return df.set_index("sap_id").to_dict(orient="index")


MOCK_EMPLOYEE_DB = load_employee_data()


EMPLOYEE_DB = load_employee_data()


def login_screen():
    st.markdown("<h2 style='text-align: center;'>GSM GreenXentro</h2>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align: center;'>Fleet Portal</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: gray;'>Sign in with your SAP ID and Password</p>", unsafe_allow_html=True)

    # Check for Account Lockout (3 failed attempts threshold)
    if st.session_state.failed_attempts >= 3:
        st.error("⚠️ Account temporarily locked due to 3 consecutive failed login attempts.")
        if st.button("Reset via Forgot Password", use_container_width=True):
            st.session_state.current_page = "forgot_password"
            st.rerun()
        return

    with st.form("login_form"):
        sap_id = st.text_input("SAP ID *")
        password = st.text_input("Password *", type="password")
        submit_btn = st.form_submit_button("Sign In", use_container_width=True)

        if submit_btn:
            if not sap_id or not password:
                st.warning("Please enter both SAP ID and Password.")
            else:
                user_record = EMPLOYEE_DB.get(sap_id)

                if not user_record:
                    st.error("Invalid SAP ID. Employee record not found.")
                else:
                    # Check for First-Time Login (Password is blank/null in DB)
                    if not user_record["password_hash"]:
                        st.session_state.user_data = user_record
                        st.session_state.current_page = "initial_setup"
                        st.rerun()
                    
                    # Standard Password Verification (Hash comparison in production)
                    elif password == user_record["password_hash"]:  # Demo check
                        st.session_state.logged_in = True
                        st.session_state.user_data = user_record
                        st.session_state.failed_attempts = 0
                        st.session_state.current_page = "trip_ticket"
                        st.rerun()
                    else:
                        st.session_state.failed_attempts += 1
                        remaining = 3 - st.session_state.failed_attempts
                        st.error(f"Incorrect password. {remaining} attempt(s) remaining.")
                        if st.session_state.failed_attempts >= 3:
                            st.rerun()

    st.markdown("---")
    if st.button("Forgot Password?", use_container_width=True):
        st.session_state.current_page = "forgot_password"
        st.rerun()


def initial_setup_screen():
    st.markdown("### 🔑 Initial Password Setup")
    st.write(f"Welcome, **{st.session_state.user_data.get('name')}** (SAP ID: {st.session_state.user_data.get('sap_id')})")
    st.info("This is your first time logging in. Please set up your initial password.")

    with st.form("setup_form"):
        new_password = st.text_input("New Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")
        setup_btn = st.form_submit_button("Save Password & Continue", use_container_width=True)

        if setup_btn:
            if not new_password or not confirm_password:
                st.warning("Please fill in both password fields.")
            elif new_password != confirm_password:
                st.error("Passwords do not match.")
            else:
                sap_id = st.session_state.user_data["sap_id"]
                EMPLOYEE_DB[sap_id]["password_hash"] = "updated_secure_hash"
                st.success("Password configured successfully! Redirecting to login...")
                st.session_state.current_page = "login"
                st.rerun()


def forgot_password_screen():
    st.markdown("### 🔄 Credential Recovery (Forgot Password)")
    st.write("Please provide your employee details for verification.")

    with st.form("recovery_form"):
        sap_id = st.text_input("SAP ID *")
        cellphone = st.text_input("Registered Cellphone Number *")
        email = st.text_input("Registered Email Address *")
        verify_btn = st.form_submit_button("Verify & Dispatch OTP", use_container_width=True)

        if verify_btn:
            user_record = EMPLOYEE_DB.get(sap_id)
            if user_record and user_record["cellphone"] == cellphone and user_record["email"] == email:
                st.success("Verification successful! A secure reset OTP has been sent to your mobile number and email.")
                st.session_state.failed_attempts = 0
            else:
                st.error("Verification failed. Provided details do not match employee records.")

    if st.button("Back to Login", type="secondary"):
        st.session_state.current_page = "login"
        st.session_state.failed_attempts = 0
        st.rerun()


def trip_ticket_form():
    st.markdown("### 🌿 GreenXentro Daily Trip Ticket (Depot)")
    user = st.session_state.user_data
    st.write(f"Logged in as: **{user.get('name')}** (SAP: **{user.get('sap_id')}**)")

    if st.button("Sign Out", type="secondary"):
        st.session_state.logged_in = False
        st.session_state.current_page = "login"
        st.session_state.user_data = {}
        st.rerun()

    st.markdown("---")

    with st.form("trip_ticket_form"):
        # Pre-populated fields from the authenticated user record
        email = st.text_input("Email *", value=user.get("email", ""))
        status = st.radio("Status *", ["Sign in", "Sign out"], horizontal=True)
        name = st.text_input("Name (Last name, First name, Middle initial) *", value=user.get("name", ""))
        sap_id = st.text_input("SAP ID *", value=user.get("sap_id", ""))
        plate_no = st.text_input("Plate no. *", value=user.get("plate_no", ""))

        schedule_options = [
            "4am ~ 1pm", "5am ~ 2pm", "6am ~ 3pm", "7am ~ 4pm",
            "8am ~ 5pm", "9am ~ 6pm", "10am ~ 7pm", "11am ~ 8pm",
            "12am ~ 9pm", "1pm ~ 10pm", "2pm ~ 11pm",
        ]
        schedule_of_duty = st.selectbox("Schedule of Duty *", schedule_options)
        battery_pct = st.number_input("Battery % *", min_value=0, max_value=100, step=1)
        odometer = st.number_input("Odometer *", min_value=0.0, format="%.2f", step=1.0)
        
        # Determine index for pre-selected team
        teams = ["Team Benjo", "Team Ruel", "Team Bacor", "Team Hannah"]
        default_team_idx = teams.index(user.get("team")) if user.get("team") in teams else 0
        team = st.selectbox("Team *", teams, index=default_team_idx)
        
        dispatcher = st.selectbox(
            "Dispatcher (sino nagbigay ng susi / kanino sinoli) *",
            ["Joshua", "April", "Karl", "Jhun", "Colobong", "Lazo"],
        )

        submitted = st.form_submit_button("Submit", use_container_width=True)

        if submitted:
            if not name or not sap_id or not plate_no:
                st.warning("Please fill out all required fields.")
            else:
                submission_data = {
                    "Timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
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
                st.success("Trip ticket submitted successfully! Daily trip record populated from employee profile.")


# Main Flow Navigation Controller
if not st.session_state.logged_in:
    if st.session_state.current_page == "initial_setup":
        initial_setup_screen()
    elif st.session_state.current_page == "forgot_password":
        forgot_password_screen()
    else:
        login_screen()
else:
    trip_ticket_form()
