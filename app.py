import os
import uuid
import qrcode
import requests
import pandas as pd
from io import BytesIO
import streamlit as st
from supabase import create_client, Client
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from PIL import Image as PILImage

# ==============================================================================
# 1. APPLICATION INITIALIZATION & SECURITY CONFIGURATION
# ==============================================================================
st.set_page_config(page_title="Kenya School Leaving Certificate Portal", layout="wide")

# Forcefully handle environment initialization strategies across local development and cloud production spaces
if os.path.exists(".env"):
    from dotenv import load_dotenv
    load_dotenv()

# Prioritize Streamlit production secrets manager variables; fallback to environment variables
SUPABASE_URL = st.secrets.get("SUPABASE_URL", os.environ.get("SUPABASE_URL", "https://supabase.co"))
SUPABASE_KEY = st.secrets.get("SUPABASE_KEY", os.environ.get("SUPABASE_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZhaWpzbWx6bnJ2xHN1aGxqeXp6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3OTI0MDY0NTgsImV4cCI6MjEwNzk4MjQ1OH0.nLMUPq_wVDwz1EJWpo6Udn3epmuNq-eSSZVsavm8zMY"))

if not SUPABASE_URL or not SUPABASE_KEY:
    st.error("Critical Failure: Infrastructure integration keys missing from global environmental execution space.")
    st.stop()

@st.cache_resource
def get_supabase_client() -> Client:
    return create_client(SUPABASE_URL, SUPABASE_KEY)

supabase = get_supabase_client()

# Initialize dynamic operational session state parameters
if "auth_token" not in st.session_state:
    st.session_state.auth_token = None
if "school_id" not in st.session_state:
    st.session_state.school_id = None
if "school_name" not in st.session_state:
    st.session_state.school_name = ""

# ==============================================================================
# 2. CENTRALIZED AUTHENTICATION LOGIC PIPELINE
# ==============================================================================
def handle_logout():
    st.session_state.auth_token = None
    st.session_state.school_id = None
    st.session_state.school_name = ""
    st.rerun()

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
                try:
                    res = supabase.auth.sign_in_with_password({"email": email, "password": password})
                    st.session_state.auth_token = res.session.access_token
                    st.session_state.school_id = res.user.id
                    
                    # Fetch profile meta mapping metrics from schools ledger matrix
                    profile = supabase.table("schools").select("school_name").eq("id", res.user.id).execute()
                    if profile.data:
                        st.session_state.school_name = profile.data[0]["school_name"]
                    st.success("Session verified! Accessing dashboard configuration space...")
                    st.rerun()
                except Exception as e:
                    st.error("Authentication Failed: Invalid user credentials.")
                    
    with tab_signup:
        with st.form("signup_form"):
            new_email = st.text_input("Official School Email")
            new_password = st.text_input("Choose Strong Password", type="password")
            school_name = st.text_input("Complete School Name (As per MoE Registration)")
            level = st.selectbox("Institutional Type", ["Primary", "Secondary"])
            county = st.text_input("Sub-County / County Location")
            
            # Syntax anomaly corrected: removed historical comments and structural syntax defects
            registered = st.form_submit_button("Provision School Infrastructure Account")
            
            if registered:
                try:
                    auth_res = supabase.auth.sign_up({"email": new_email, "password": new_password})
                    if auth_res.user:
                        supabase.table("schools").insert({
                            "id": auth_res.user.id,
                            "school_name": school_name,
                            "school_level": level,
                            "county": county
                        }).execute()
                        st.success("Account provisioned successfully! Check mailbox for confirmation links, then log in.")
                except Exception as e:
                    st.error("Registration Interrupted: Database processing mismatch.")
    st.stop()

# ==============================================================================
# 3. INTERACTIVE DASHBOARD SYSTEM OPERATIONS
# ==============================================================================
st.sidebar.title("🏫 Control Center")
st.sidebar.markdown(f"**Institution:** \n{st.session_state.school_name}")
st.sidebar.button("Secure Application Terminate", on_click=handle_logout)

# Pull baseline institutional metadata configurations profile
try:
    school_profile = supabase.table("schools").select("*").eq("id", st.session_state.school_id).single().execute()
except Exception as config_err:
    st.error(f"Critical Metadata Profile Read Interrupted: {str(config_err)}")
    st.stop()

menu = st.sidebar.radio("Navigation Workspace Router", [
    "🏛️ Institutional Branding",
    "🎓 Issue New Leaving Certificate",
    "📊 Historic Registries & Audit Logs"
])

# ------------------------------------------------------------------------------
# MODULE A: INSTITUTIONAL BRANDING SETUP
# ------------------------------------------------------------------------------
if menu == "🏛️ Institutional Branding":
    st.title("🏛️ Institutional Branding & Metadata Asset Hub")
    st.write("Manage your school profile and upload an official high-resolution crest to embed dynamically into generated certificate artifacts.")
    
    col1, col2 = st.columns(2)
    with col1:
        st.info(f"**Registered Name:** {school_profile.data['school_name']}\n\n**Academic Tier:** {school_profile.data['school_level']} School\n\n**Regional Jurisdiction Location:** {school_profile.data['county']} County")
    
    with col2:
        if school_profile.data.get("school_logo_url"):
            st.image(school_profile.data["school_logo_url"], width=120, caption="Active Verified School Crest Image Asset")
        else:
            st.warning("No custom institutional emblem file detected. System is running standard text-only header generation templates.")
            
    logo_file = st.file_uploader("Upload New High-Resolution Logo/Crest File Asset", type=["png", "jpg", "jpeg"])
    if logo_file:
        if st.button("Commit Logo File Asset to Secure Storage Grid"):
            with st.spinner("Processing file streaming vectors..."):
                try:
                    ext = logo_file.name.split(".")[-1].lower()
                    bucket_path = f"logos/{st.session_state.school_id}_{uuid.uuid4().hex[:6]}.{ext}"
                    
                    supabase.storage.from_("certificates").upload(
                        path=bucket_path, file=logo_file.getvalue(),
                        file_options={"content-type": f"image/{ext}", "upsert": "true"}
                    )
                    public_logo_url = supabase.storage.from_("certificates").get_public_url(bucket_path)
                    supabase.table("schools").update({"school_logo_url": public_logo_url}).eq("id", st.session_state.school_id).execute()
                    st.success("Logo catalog configuration pipeline sync completed successfully!")
                    st.rerun()
                except Exception as logo_err:
                    st.error(f"Asset Transmission Error: {str(logo_err)}")

# ------------------------------------------------------------------------------
# MODULE B: DOCUMENT GENERATOR COMPILER ENGINE
# ------------------------------------------------------------------------------
elif menu == "🎓 Issue New Leaving Certificate":
    st.title("🎓 Ministry of Education Certificate Compiler Engine")
    st.write("Provide structural academic performance data and behavioral marks below to dynamically register a unique certificate tracking hash.")
    
    with st.form("cert_input_form"):
        c1, c2, c3 = st.columns(3)
        with c1:
            student_name = st.text_input("Pupil's Full Legal Name (Caps Recommended)").upper()
            adm_no = st.text_input("Official School Admission Registration ID (Adm No)")
            mean_grade = st.selectbox("Final KCSE / National Assessment Mean Grade Attained", ["A", "A-", "B+", "B", "B-", "C+", "C", "C-", "D+", "D", "D-", "E"])
        with c2:
            dob = st.date_input("Date of Birth (As per Admission Register Record Books)")
            date_entered = st.date_input("Official Institutional Enrollment Date")
            class_entered = st.text_input("Class / Form upon Initial Admission Entry")
        with c3:
            date_left = st.date_input("Official Graduation / Leaving Date")
            class_left = st.text_input("Final Class / Form level upon Departure")
