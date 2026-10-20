
# ==============================================================================
# 1. HARDENED INFRASTRUCTURE PLATFORM INITIALIZATION
# ==============================================================================
st.set_page_config(page_title="Kenya School Leaving Certificate Portal", layout="wide", page_icon="🇰🇪")

# Enforce clean string loading; completely strip spaces or default website overrides
SUPABASE_URL = st.secrets.get("SUPABASE_URL", "https://supabase.co").strip()
SUPABASE_KEY = st.secrets.get("SUPABASE_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZhaWpzbWx6bnJ2eHN1aGxqeXp6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3OTI0MDY0NTgsImV4cCI6MjEwNzk4MjQ1OH0.nLMUPq_wVDwz1EJWpo6Udn3epmuNq-eSSZVsavm8zMY").strip()

# Final safety check: if something injected a corporate marketing URL, override it instantly
if "supabase.com" in SUPABASE_URL.lower() and not ".supabase.co" in SUPABASE_URL.lower():
    SUPABASE_URL = "https://supabase.co"

# Initialize Supabase client infrastructure explicitly using verified keys
supabase = None
try:
    from supabase import create_client
    if SUPABASE_URL and SUPABASE_KEY:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
except Exception as e:
    st.sidebar.error(f"Initialization Failed: {str(e)}")

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
    SUPABASE_URL = "https://vaijsmlznrvxsuhljyzz.supabase.co"

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
                            st.session_state.school_name = profile.data["school_name"]
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
                        verification_url = f"https://leaving-certificate-cdtq3dflgykxbspyeavizj.streamlit.app/verify?id={cert_uuid}"
                        
                        # Full configuration properties dictionary mapping
                        cert_payload = {
                            "id": cert_uuid,
                            "school_id": st.session_state.school_id,
                            "student_name": student_name,
                            "admission_no": adm_no,
                            "index_no": index_no,
                            "date_of_birth": str(dob),
                            "date_entered": str(date_entered),
                            "class_entered": class_entered,
                            "date_left": str(date_left),
                            "class_left": class_left,
                            "mean_grade": mean_grade,
                            "conduct_remarks": conduct,
                            "principal_remarks": headteacher_remarks,
                            "co_curricular_activities": co_curricular,
                            "verification_url": verification_url
                        }
                        
                        if supabase:
                            try:
                                supabase.table("certificates").insert(cert_payload).execute()
                            except Exception as db_e:
                                st.sidebar.warning(f"Database sync skipped: {str(db_e)}")
                        
                        # --- COMPILING THE PDF WITH REPORTLAB ---
                        pdf_buffer = BytesIO()
                        doc = SimpleDocTemplate(pdf_buffer, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
                        styles = getSampleStyleSheet()
                        current_story = []
                        
                        title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], fontName='Helvetica-Bold', fontSize=18, alignment=TA_CENTER, spaceAfter=5)
                        sub_style = ParagraphStyle('SubStyle', parent=styles['Normal'], fontName='Helvetica', fontSize=12, alignment=TA_CENTER, spaceAfter=20)
                        body_style = ParagraphStyle('BodyStyle', parent=styles['Normal'], fontName='Helvetica', fontSize=11, leading=18, spaceAfter=10)
                        
                        current_story.append(Paragraph("REPUBLIC OF KENYA", title_style))
                        current_story.append(Paragraph(f"MINISTRY OF EDUCATION — {st.session_state.school_name.upper()}", title_style))
                        current_story.append(Paragraph("OFFICIAL SCHOOL LEAVING CERTIFICATE", sub_style))
                        current_story.append(Spacer(1, 15))
                        
                        data_matrix = [
                            [Paragraph(f"<b>Student Legal Name:</b> {student_name}", body_style), Paragraph(f"<b>KNEC Index Number:</b> {index_no}", body_style)],
                            [Paragraph(f"<b>Admission No:</b> {adm_no}", body_style), Paragraph(f"<b>Date of Birth:</b> {str(dob)}", body_style)],
                            [Paragraph(f"<b>Date Entered:</b> {str(date_entered)}", body_style), Paragraph(f"<b>Class/Form Entered:</b> {class_entered}", body_style)],
                            [Paragraph(f"<b>Date of Leaving:</b> {str(date_left)}", body_style), Paragraph(f"<b>Class/Form Left:</b> {class_left}", body_style)],
                            [Paragraph(f"<b>Mean Grade Attained:</b> {mean_grade}", body_style), Paragraph(f"<b>Conduct Assessment:</b> {conduct}", body_style)]
                        ]
                        
                        # FIXED: explicit widths assigned to layout tables
                        t = Table(data_matrix, colWidths=[260, 260])
                        t.setStyle(TableStyle([
                            ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
                            ('VALIGN', (0,0), (-1,-1), 'TOP'),
                            ('BOTTOMPADDING', (0,0), (-1,-1), 8),
                            ('TOPPADDING', (0,0), (-1,-1), 8),
                        ]))
                        current_story.append(t)
                        current_story.append(Spacer(1, 20))
                        
                        current_story.append(Paragraph(f"<b>Co-Curricular Activities & Responsibilities:</b><br/>{co_curricular}", body_style))
                        current_story.append(Spacer(1, 10))
                        current_story.append(Paragraph(f"<b>Principal / Headteacher Comprehensive Remarks:</b><br/>{headteacher_remarks}", body_style))
                        current_story.append(Spacer(1, 40))
                        
                        sig_matrix = [
                            [Paragraph("________________________________________<br/>Principal / Headteacher Signature", body_style),
                             Paragraph(f"<b>Verification Key ID:</b><br/>{cert_uuid}", body_style)]
                        ]
                        sig_table = Table(sig_matrix, colWidths=[260, 260])
                        current_story.append(sig_table)
                        
                        doc.build(current_story)
                        pdf_data = pdf_buffer.getvalue()
                        
                        st.success("🎉 PDF Certificate Compiled Successfully!")
                        st.download_button(
                            label="📥 Click Here to Download Generated Certificate PDF",
                            data=pdf_data,
                            file_name=f"Leaving_Certificate_{adm_no}.pdf",
                            mime="application/pdf"
                        )
                    except Exception as err:
                        st.error(f"Compilation Interrupted: Layout configuration error. Details: {str(err)}")

# ------------------------------------------------------------------------------
# MODULE B: INSTITUTIONAL BRAND SETUP
# ------------------------------------------------------------------------------
elif menu == "🏛️ Institutional Branding":
    st.title("🏛️ Institutional Branding Hub")
    st.info(f"**Current active school space:** {st.session_state.school_name}")
    logo_file = st.file_uploader("Upload School Crest Image", type=["png", "jpg", "jpeg"])
    if logo_file:
        st.success("Logo file asset loaded into current view buffer context.")

# ------------------------------------------------------------------------------
# MODULE C: LEDGER REGISTRIES VIEW PANEL
# ------------------------------------------------------------------------------
elif menu == "📊 Historic Registries & Audit Logs":
    st.title("📊 Historic Certificate Registries Ledger")
    st.info("Bypass Mode active: Connect Supabase endpoints via Streamlit Cloud Secrets to read persistent historical entries.")
