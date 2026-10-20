import os
import uuid
import pandas as pd
from io import BytesIO
import streamlit as st

# ReportLab libraries for official certificate generation layout execution
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

# ==============================================================================
# 1. APPLICATION ENVIRONMENT PLATFORM INITIALIZATION
# ==============================================================================
st.set_page_config(page_title="Kenya School Leaving Certificate Portal", layout="wide", page_icon="🇰🇪")

if os.path.exists(".env"):
    from dotenv import load_dotenv
    load_dotenv()

# Prioritize local or production secret assignments; Fallback explicitly to your active project API domain
SUPABASE_URL = st.secrets.get("SUPABASE_URL", os.environ.get("SUPABASE_URL", "")).strip()
if not SUPABASE_URL or "supabase.com" in SUPABASE_URL.lower() and not ".supabase.co" in SUPABASE_URL.lower():
    SUPABASE_URL = "https://supabase.co"

SUPABASE_KEY = st.secrets.get("SUPABASE_KEY", os.environ.get("SUPABASE_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZhaWpzbWx6bnJ2xHN1aGxqeXp6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3OTI0MDY0NTgsImV4cCI6MjEwNzk4MjQ1OH0.nLMUPq_wVDwz1EJWpo6Udn3epmuNq-eSSZVsavm8zMY")).strip()

# Initialize Supabase client with a soft structural safety check
supabase = None
try:
    from supabase import create_client
    if SUPABASE_URL and SUPABASE_KEY:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
except Exception as e:
    pass

# Establish baseline reactive execution context values
if "auth_token" not in st.session_state:
    st.session_state.auth_token = "DEVELOPMENT_BYPASS_TOKEN"  # Bypass token set to unlock your screen immediately
if "school_id" not in st.session_state:
    st.session_state.school_id = "00000000-0000-0000-0000-000000000000"
if "school_name" not in st.session_state:
    st.session_state.school_name = "SAMPLE REPUBLIC ACADEMY"

def handle_logout():
    st.session_state.auth_token = None
    st.session_state.school_id = None
    st.session_state.school_name = ""
    st.rerun()

# ==============================================================================
# 2. APPLICATION AUTHENTICATION ROUTING GATEWAY
# ==============================================================================
if not st.session_state.auth_token:
    st.title("🇰🇪 Kenya School Leaving Certificate Portal")
    st.subheader("Official Ministry of Education Multi-Tenant Management Gateway")
    
    tab_login, tab_signup = st.tabs(["🔒 School Administrator Login", "📝 Register New Institution Account"])
    
    with tab_login:
        with st.form("login_form"):
            email = st.text_input("Official Institutional Email Address")
            password = st.text_input("Security Access Password", type="password")
            submitted = st.form_submit_button("Authenticate Session")
            
            if submitted:
                if supabase:
                    try:
                        res = supabase.auth.sign_in_with_password({"email": email, "password": password})
                        st.session_state.auth_token = res.session.access_token
                        st.session_state.school_id = res.user.id
                        profile = supabase.table("schools").select("school_name").eq("id", res.user.id).execute()
                        if profile.data:
                            st.session_state.school_name = profile.data[0]["school_name"]
                        st.success("Session verified!")
                        st.rerun()
                    except Exception as e:
                        st.error("Authentication Failed: Invalid credentials.")
                else:
                    st.session_state.auth_token = "DEV_TOKEN"
                    st.rerun()
                    
    with tab_signup:
        with st.form("signup_form"):
            new_email = st.text_input("Official School Email")
            new_password = st.text_input("Choose Strong Password", type="password")
            school_name_input = st.text_input("Complete School Name (As per MoE Registration)")
            level = st.selectbox("Institutional Type", ["Primary", "Secondary"])
            county = st.text_input("Sub-County / County Location")
            registered = st.form_submit_button("Provision School Infrastructure Account")
            
            if registered:
                if not new_email or len(new_password) < 6 or not school_name_input:
                    st.error("Validation Error: Please fill all fields.")
                elif supabase:
                    try:
                        auth_res = supabase.auth.sign_up({"email": new_email, "password": new_password})
                        if auth_res.user:
                            supabase.table("schools").insert({
                                "id": auth_res.user.id,
                                "school_name": school_name_input,
                                "school_level": level,
                                "county": county
                            }).execute()
                            st.success("Account provisioned successfully!")
                    except Exception as e:
                        st.error(f"Registration Interrupted: {str(e)}")
    st.stop()

# ==============================================================================
# 3. INTERACTIVE SECURED MANAGEMENT APPLICATION CONTROL CENTER
# ==============================================================================
st.sidebar.title("🏫 Control Center")
st.sidebar.markdown(f"**Institution:** \n{st.session_state.school_name}")
st.sidebar.button("Secure Application Terminate", on_click=handle_logout)

# Safely extract school metadata summaries or assign temporary dummy values
school_level_val = "Secondary"
school_county_val = "Nairobi"
if supabase:
    try:
        school_profile = supabase.table("schools").select("*").eq("id", st.session_state.school_id).single().execute()
        if school_profile.data:
            st.session_state.school_name = school_profile.data.get('school_name', st.session_state.school_name)
            school_level_val = school_profile.data.get('school_level', 'Secondary')
            school_county_val = school_profile.data.get('county', 'Nairobi')
    except Exception:
        pass

menu = st.sidebar.radio("Navigation Workspace Router", [
    "🎓 Issue New Leaving Certificate",
    "🏛️ Institutional Branding",
    "📊 Historic Registries & Audit Logs"
])

# ------------------------------------------------------------------------------
# MODULE A: LEAVING CERTIFICATE PIPELINE (PDF FILLING PAGE & DATA INGESTION)
# ------------------------------------------------------------------------------
if menu == "🎓 Issue New Leaving Certificate":
    st.title("🎓 Ministry of Education Certificate Compiler Engine")
    st.write("Provide structural academic performance data and behavioral marks below to dynamically compile a print-ready PDF certificate.")
    
    with st.form("cert_input_form"):
        c1, c2, c3 = st.columns(3)
        with c1:
            student_name = st.text_input("Pupil's Full Legal Name (Caps Recommended)", value="JOHN DOE OMONDI").upper()
            adm_no = st.text_input("Official School Admission Registration ID (Adm No)", value="9845")
            index_no = st.text_input("National Examination Index Number (KNEC Code Mapping)", value="20400001001")
        with c2:
            mean_grade = st.selectbox("Final Mean Grade Attained", ["A", "A-", "B+", "B", "B-", "C+", "C", "C-", "D+", "D", "D-", "E"], index=3)
            dob = st.date_input("Date of Birth")
            date_entered = st.date_input("Official Institutional Enrollment Date")
        with c3:
            class_entered = st.text_input("Class / Form upon Initial Admission Entry", value="Form 1 Blue")
            date_left = st.date_input("Official Graduation / Leaving Date")
            class_left = st.text_input("Final Class / Form level upon Departure", value="Form 4 East")
            
        conduct = st.selectbox("General Evaluation of Behavioral Conduct & Attitude", ["Excellent", "Very Good", "Good", "Fair"])
        headteacher_remarks = st.text_area("Principal / Headteacher's Final Comprehensive Report Remarks", value="An exemplary, disciplined student who consistently demonstrated outstanding leadership capabilities across all semesters.")
        co_curricular = st.text_area("Notable Extracurricular Engagements or Talents Exhibited", value="Captain of the Varsity Football Team, active participant in regional Science Congress debates.")

        issue_cert = st.form_submit_button("Compile & Generate Official Leaving Certificate PDF")

        if issue_cert:
            if not student_name or not adm_no or not index_no:
                st.error("Validation Halt: Student Name, Admission ID, and KNEC Index Number fields are mandatory.")
            else:
                with st.spinner("Compiling structural layout profiles..."):
                    try:
                        cert_uuid = str(uuid.uuid4())
                        verification_url = f"https://streamlit.app{cert_uuid}"
                        
                        # Correctly structured dictionary data packet mapping
                        cert_payload = {
                            "id": cert_uuid,
                            "school_id": st.session_state.school_id,
                            "student_name": student_name,
                            "admission_no": adm_no,
                            "index_no": index_no,
