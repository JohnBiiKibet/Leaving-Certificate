import os
import uuid
from io import BytesIO
import streamlit as st
from supabase import create_client, Client

# ReportLab libraries for official certificate generation
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT

# ==============================================================================
# 1. DATABASE & INITIALIZATION
# ==============================================================================
st.set_page_config(page_title="Kenya School Leaving Certificate Portal", layout="centered", page_icon="🇰🇪")

# Load environment configuration variables
SUPABASE_URL = st.secrets.get("SUPABASE_URL", os.environ.get("SUPABASE_URL", "https://supabase.co"))
SUPABASE_KEY = st.secrets.get("SUPABASE_KEY", os.environ.get("SUPABASE_KEY", ""))

if not SUPABASE_URL or SUPABASE_URL == "https://supabase.co" or not SUPABASE_KEY:
    st.error("❌ Configuration Error: Please set your 'SUPABASE_URL' and 'SUPABASE_KEY' environment variables.")
    st.stop()

@st.cache_resource
def get_supabase_client() -> Client:
    return create_client(SUPABASE_URL.strip("/"), SUPABASE_KEY)

supabase = get_supabase_client()

# ==============================================================================
# 2. PDF GENERATION ENGINE
# ==============================================================================
def build_pdf_bytes(cert_data: dict) -> bytes:
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer, 
        pagesize=letter,
        rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36
    )
    
    styles = getSampleStyleSheet()
    
    # Custom Typography Styles
    title_style = ParagraphStyle(
        'CertTitle', parent=styles['Normal'], fontName='Helvetica-Bold',
        fontSize=24, leading=28, alignment=TA_CENTER, textColor=colors.HexColor('#1E3A8A')
    )
    subtitle_style = ParagraphStyle(
        'CertSub', parent=styles['Normal'], fontName='Helvetica',
        fontSize=12, leading=16, alignment=TA_CENTER, textColor=colors.HexColor('#4B5563')
    )
    section_heading = ParagraphStyle(
        'SectionHead', parent=styles['Normal'], fontName='Helvetica-Bold',
        fontSize=14, leading=18, alignment=TA_CENTER, textColor=colors.HexColor('#B91C1C'),
        spaceAfter=15
    )
    body_style = ParagraphStyle(
        'CertBody', parent=styles['Normal'], fontName='Helvetica',
        fontSize=11, leading=22, alignment=TA_LEFT, textColor=colors.HexColor('#1F2937')
    )

    story = []
    
    # Certificate Header Panel
    story.append(Paragraph("REPUBLIC OF KENYA", title_style))
    story.append(Spacer(1, 4))
    story.append(Paragraph("MINISTRY OF EDUCATION", subtitle_style))
    story.append(Spacer(1, 15))
    story.append(Paragraph("SCHOOL LEAVING CERTIFICATE", section_heading))
    story.append(Spacer(1, 10))
    
    # Structured Identity Matrix Data
    certificate_text = f"""
    <b>This is to certify that:</b> {cert_data['student_name'].upper()}<br/><br/>
    <b>Admission Number:</b> {cert_data['admission_no']} &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; 
    <b>Date of Birth:</b> {cert_data['dob']}<br/><br/>
    <b>Institution Name:</b> {cert_data['school_name'].upper()}<br/><br/>
    <b>Date of Entrance:</b> {cert_data['date_of_entrance']} &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; 
    <b>Date of Leaving:</b> {cert_data['date_of_leaving']}<br/><br/>
    <b>Headteacher's Assessment on Ability / Industry:</b><br/>
    {cert_data['headteacher_remarks']}<br/><br/>
    <b>Co-Curricular Activities & Extracurricular Responsibilities:</b><br/>
    {cert_data['co_curricular_remarks']}
    """
    
    story.append(Paragraph(certificate_text, body_style))
    story.append(Spacer(1, 50))
    
    # Signature Ledger Layout Blocks
    sig_data = [
        [
            Paragraph(f"<b>Date of Issue:</b> {cert_data['date_of_issue']}", body_style),
            Paragraph("<b>Signature:</b> _______________________<br/>Headteacher's Stamp", body_style)
        ]
    ]
    sig_table = Table(sig_data, colWidths=[250, 250])
    sig_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('ALIGN', (1,0), (1,0), 'RIGHT')
    ]))
    
    story.append(sig_table)
    
    # Build complete execution layout
    doc.build(story)
    pdf_data = buffer.getvalue()
    buffer.close()
    return pdf_data

# ==============================================================================
# 3. INTERACTIVE DATA APPLICATION INTERFACE
# ==============================================================================
st.title("🇰🇪 Kenya School Leaving Certificate System")
st.subheader("Official Form Entry & PDF Record Generation Terminal")

tab_create, tab_records = st.tabs(["🎓 Issue New Certificate", "📊 Historic Database Registry"])

# MODULE A: INPUT FORM ENTRY PIPELINE
with tab_create:
    with st.form("certificate_form", clear_on_submit=True):
        st.write("### Institutional Identity Elements")
        school_name = st.text_input("Complete School Name (As per MoE Registration)")
        
        st.write("### Scholar Demographics Profile")
        col1, col2 = st.columns(2)
        with col1:
            student_name = st.text_input("Full Pupil Name (In Block Letters)")
            admission_no = st.text_input("Unique Institutional Admission ID Reference")
        with col2:
            dob = st.date_input("Official Date of Birth Check")
            date_of_issue = st.date_input("Certificate Production Authentication Date")
            
        st.write("### Academic Enrolment Timeline")
        col3, col4 = st.columns(2)
        with col3:
            date_of_entrance = st.date_input("Date of Institutional Enrollment Admission")
        with col4:
            date_of_leaving = st.date_input("Official Date of Graduation / Leaving")
            
        st.write("### Performance Metrics & Evaluation Assessment Summaries")
        headteacher_remarks = st.text_area("Headteacher's Assessment Profile on Ability, Character and General Industry")
        co_curricular_remarks = st.text_area("Co-Curricular Accomplishments, Games Played, and Positions of Leadership Held")
        
        generate_btn = st.form_submit_button("Verify Record Metadata & Generate PDF")
        
        if generate_btn:
            if not school_name or not student_name or not admission_no:
                st.error("Validation Error: Please make sure School Name, Student Name, and Admission Number are provided.")
            else:
                # Structure payload dataset schema matching PostgreSQL types
                cert_payload = {
                    "id": str(uuid.uuid4()),
                    "school_name": school_name,
                    "student_name": student_name,
                    "admission_no": admission_no,
                    "dob": str(dob),
                    "date_of_entrance": str(date_of_entrance),
                    "date_of_leaving": str(date_of_leaving),
                    "date_of_issue": str(date_of_issue),
                    "headteacher_remarks": headteacher_remarks,
                    "co_curricular_remarks": co_curricular_remarks
                }
                
                try:
                    # Database records storage persistence grid sync loop executions
                    supabase.table("certificates").insert(cert_payload).execute()
                    st.success(f"✔️ Record for {student_name} successfully cataloged into database infrastructure matrix.")
                    
                    # Compute execution loop metrics for binary PDF stream blocks
                    pdf_bytes = build_pdf_bytes(cert_payload)
                    
                    st.download_button(
                        label="⬇️ Download Official Generated Leaving Certificate PDF",
                        data=pdf_bytes,
                        file_name=f"Leaving_Certificate_{admission_no}.pdf",
                        mime="application/pdf"
                    )
                except Exception as db_err:
                    st.error(f"Infrastructure Interruption: Error uploading dataset mapping arrays. Details: {str(db_err)}")

# MODULE B: DATAFRAME RECORDS AUDIT LOG GRID
with tab_records:
    st.write("### Registered Leaving Certificates Log Grid")
    try:
        query_response = supabase.table("certificates").select("*").order("created_at", descending=True).execute()
        
        if query_response.data:
            df = pd.DataFrame(query_response.data)
            
            # Format UI rendering components gracefully for visualization matrix display
            display_columns = {
                "admission_no": "Admission No",
                "student_name": "Student Name",
                "school_name": "Institution Name",
                "date_of_leaving": "Date Left",
                "date_of_issue": "Date Issued"
            }
            st.dataframe(df[list(display_columns.keys())].rename(columns=display_columns), use_container_width=True)
        else:
            st.info("No registered scholar leaving certificates found in the database registry matrix yet.")
            
    except Exception as read_err:
        st.error(f"Failed to query current state metrics array from PostgreSQL Database node instances: {str(read_err)}")
