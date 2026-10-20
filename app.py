import os
import uuid
import pandas as pd
from io import BytesIO
import streamlit as st
from supabase import create_client, Client

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

# Prioritize Streamlit production secrets; Fallback cleanly to runtime system environment vectors
SUPABASE_URL = st.secrets.get("SUPABASE_URL", os.environ.get("SUPABASE_URL", "https://supabase.co"))
SUPABASE_KEY = st.secrets.get("SUPABASE_KEY", os.environ.get("SUPABASE_KEY", ""))

# CORRECTION: Verify the project URL is configured and isn't pointing to the root Supabase marketing page
if not SUPABASE_URL or SUPABASE_URL == "https://supabase.co" or not SUPABASE_KEY:
    st.error(
        "❌ Critical Failure: Infrastructure integration keys missing or misconfigured. "
        "Please check your `.env` file or Streamlit secrets config to ensure 'SUPABASE_URL' is set to your unique project API URL (e.g., https://your-project-id.supabase.co)."
    )
    st.stop()

@st.cache_resource
def get_supabase_client() -> Client:
    # Ensure there are no accidental trailing slashes in the initialization path
    return create_client(SUPABASE_URL.strip("/"), SUPABASE_KEY)

supabase = get_supabase_client()

# Establish baseline reactive execution context values
if "auth_token" not in st.session_state:
    st.session_state.auth_token = None
if "school_id" not in st.session_state:
    st.session_state.school_id = None
if "school_name" not in st.session_state:
    st.session_state.school_name = ""

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
                    st.error("Authentication Failed: Invalid credentials.")
                    
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
                    st.error("Validation Error: Please fill all fields. Password must be 6+ characters.")
                else:
                    try:
                        auth_res = supabase.auth.sign_up({"email": new_email, "password": new_password})
                        if auth_res.user:
                            supabase.table("schools").insert({
                                "id": auth_res.user.id,
                                "school_name": school_name_input,
                                "school_level": level,
                                "county": county
                            }).execute()
                            st.success("Account provisioned successfully! Proceed to sign in.")
                    except Exception as e:
                        st.error(f"Registration Interrupted: Database processing mismatch. Details: {str(e)}")
    st.stop()

# ==============================================================================
# 3. INTERACTIVE SECURED MANAGEMENT APPLICATION CONTROL CENTER
# ==============================================================================
st.sidebar.title("🏫 Control Center")
st.sidebar.markdown(f"**Institution:** \n{st.session_state.school_name}")
st.sidebar.button("Secure Application Terminate", on_click=handle_logout)

# Query metadata configurations profile profile
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
# MODULE A: INSTITUTIONAL CONFIGURATIONS BRAND HUB
# ------------------------------------------------------------------------------
if menu == "🏛️ Institutional Branding":
    st.title("🏛️ Institutional Branding & Metadata Asset Hub")
    col1, col2 = st.columns(2)
    with col1:
        st.info(f"**Registered Name:** {school_profile.data['school_name']}\n\n**Academic Tier:** {school_profile.data['school_level']} School\n\n**Regional Jurisdiction Location:** {school_profile.data['county']} County")
    with col2:
        if school_profile.data.get("school_logo_url"):
            st.image(school_profile.data["school_logo_url"], width=120, caption="Active Verified School Crest Image Asset")
        else:
            st.warning("No custom institutional emblem file detected.")
            
    logo_file = st.file_uploader("Upload New High-Resolution Logo/Crest File Asset", type=["png", "jpg", "jpeg"])
    if logo_file and st.button("Commit Logo File Asset to Secure Storage Grid"):
        try:
            ext = logo_file.name.split(".")[-1].lower()
            bucket_path = f"logos/{st.session_state.school_id}_{uuid.uuid4().hex[:6]}.{ext}"
            
            # Syntax fixed here: properly chained storage access loop configuration
            supabase.storage.from_("certificates").upload(
                path=bucket_path, 
                file=logo_file.getvalue(), 
                file_options={"content-type": f"image/{ext}", "upsert": "true"}
            )
            
            public_logo_url = supabase.storage.from_("certificates").get_public_url(bucket_path)
            supabase.table("schools").update({"school_logo_url": public_logo_url}).eq("id", st.session_state.school_id).execute()
            st.success("Logo catalog configuration pipeline sync completed successfully!")
        except Exception as e:
            st.error(f"Storage System Synchronization Error: {str(e)}")
