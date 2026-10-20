import os
import uuid
import qrcode
import requests
from io import BytesIO
from fastapi import FastAPI, Depends, HTTPException, Header, Request, UploadFile, File
from supabase import create_client, Client
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from PIL import Image as PILImage

# Dynamic environment injector initialization
if os.path.exists(".env"):
    from dotenv import load_dotenv
    load_dotenv()

app = FastAPI(title="Kenya School Leaving Certificate Microservice Portal")

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("System lacks critical database integration keys in environmental memory.")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Dependency Verification Guard
async def get_current_school(authorization: str = Header(...)):
    token = authorization.replace("Bearer ", "")
    try:
        user = supabase.auth.get_user(token)
        return user.user.id
    except Exception:
        raise HTTPException(status_code=401, detail="Session authentication failed or token expired.")

# 1. LOGO SYNC PIPELINE
@app.post("/school/upload-logo")
async def upload_school_logo(file: UploadFile = File(...), school_id: str = Depends(get_current_school)):
    extension = file.filename.split(".")[-1].lower()
    if extension not in ["jpg", "jpeg", "png"]:
        raise HTTPException(status_code=400, detail="Unsupported image variant. Provide PNG or JPG.")
    
    file_bytes = await file.read()
    bucket_path = f"logos/{school_id}_{uuid.uuid4().hex[:6]}.{extension}"
    
    supabase.storage.from_("certificates").upload(
        path=bucket_path,
        file=file_bytes,
        file_options={"content-type": f"image/{extension}", "upsert": "true"}
    )
    
    logo_public_url = supabase.storage.from_("certificates").get_public_url(bucket_path)
    supabase.table("schools").update({"school_logo_url": logo_public_url}).eq("id", school_id).execute()
    
    return {"status": "success", "logo_url": logo_public_url}

# 2. DOCUMENT COMPILER ENGINE
@app.post("/certificates/generate")
async def generate_certificate(payload: dict, school_id: str = Depends(get_current_school)):
    serial_no = f"KE-MOE-{uuid.uuid4().hex[:8].upper()}"
    verification_url = f"https://elimu.go.ke{serial_no}"
    
    school_profile = supabase.table("schools").select("school_name, school_logo_url").eq("id", school_id).single().execute()
    if not school_profile.data:
        raise HTTPException(status_code=404, detail="School profile context not established.")
    
    # Render cryptographic QR code
    qr = qrcode.QRCode(version=1, box_size=5, border=1)
    qr.add_data(verification_url)
    qr.make(fit=True)
    os.makedirs("/tmp/assets", exist_ok=True)
    qr_path = f"/tmp/assets/qr_{serial_no}.png"
    qr.make_image(fill_color="black", back_color="white").save(qr_path)
    
    # Process custom branding assets if present
    logo_path = None
    if school_profile.data.get("school_logo_url"):
        try:
            response = requests.get(school_profile.data["school_logo_url"], timeout=10)
            if response.status_code == 200:
                logo_path = f"/tmp/assets/logo_{school_id}.png"
                img = PILImage.open(BytesIO(response.content))
                img.thumbnail((70, 70))
                img.save(logo_path)
        except Exception:
            logo_path = None

    pdf_path = f"/tmp/{serial_no}.pdf"
    doc = SimpleDocTemplate(pdf_path, pagesize=landscape(letter),
                            rightMargin=40, leftMargin=40, topMargin=30, bottomMargin=30)
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('T', fontName='Helvetica-Bold', fontSize=15, leading=18, textColor=colors.HexColor('#1A365D'), alignment=TA_CENTER)
    school_title_style = ParagraphStyle('ST', fontName='Helvetica-Bold', fontSize=13, leading=16, textColor=colors.HexColor('#2C5282'), alignment=TA_CENTER)
    body_style = ParagraphStyle('B', fontName='Helvetica', fontSize=11, leading=18, textColor=colors.HexColor('#2D3748'))
    
    story = []
    header_text_flow = [
        Paragraph("REPUBLIC OF KENYA", title_style),
        Paragraph("MINISTRY OF EDUCATION, SCIENCE AND TECHNOLOGY", title_style),
        Spacer(1, 4),
        Paragraph(f"{school_profile.data['school_name'].upper()} LEAVING CERTIFICATE", school_title_style)
    ]
    
    if logo_path:
        logo_element = RLImage(logo_path, width=65, height=65)
        header_table = Table([[logo_element, header_text_flow, ""]], colWidths=[80, 560, 80])
        header_table.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'MIDDLE'), ('ALIGN', (1,0), (1,0), 'CENTER')]))
        story.append(header_table)
    else:
        story.extend(header_text_flow)
        
    story.append(Spacer(1, 20))
    
    cert_text = (f"<b>THIS IS TO CERTIFY THAT:</b> &nbsp;&nbsp;<u>{payload['student_name'].upper()}</u>&nbsp;&nbsp;&nbsp;&nbsp;"
                 f"<b>ADM NO:</b> &nbsp;&nbsp;<u>{payload['adm_no']}</u><br/><br/>"
                 f"<b>DATE OF BIRTH:</b> &nbsp;&nbsp;<u>{payload['date_of_birth']}</u> &nbsp;&nbsp;entered this school on &nbsp;&nbsp;<u>{payload['date_entered']}</u><br/><br/>"
                 f"was enrolled in Class/Form &nbsp;&nbsp;<u>{payload['class_entered']}</u>&nbsp;&nbsp; and left on &nbsp;&nbsp;<u>{payload['date_left']}</u><br/><br/>"
                 f"from Class/Form &nbsp;&nbsp;<u>{payload['class_left']}</u>&nbsp;&nbsp; having satisfactorily completed courses with a <b>MEAN GRADE OF: {payload['mean_grade']}</b>.")
    
    story.append(Paragraph(cert_text, body_style))
    story.append(Spacer(1, 15))
    
    matrix = [
        [Paragraph("<b>Performance / Behavioral Assessment Report:</b>", body_style), ""],
        [Paragraph("<b>Ability:</b>", body_style), Paragraph(payload.get('ability', 'Good'), body_style)],
        [Paragraph("<b>Industry:</b>", body_style), Paragraph(payload.get('industry', 'Consistent'), body_style)],
        [Paragraph("<b>Conduct:</b>", body_style), Paragraph(payload.get('conduct', 'Exemplary'), body_style)],
        [Paragraph("<b>Co-Curricular:</b>", body_style), Paragraph(payload.get('co_curricular', 'N/A'), body_style)]
    ]
    t_matrix = Table(matrix, colWidths=[180, 540])
    t_matrix.setStyle(TableStyle([('SPAN', (0,0), (1,0)), ('LINEBELOW', (0,1), (1,-1), 0.5, colors.HexColor('#CBD5E0')), ('VALIGN', (0,0), (-1,-1), 'TOP')]))
    story.append(t_matrix)
    story.append(Spacer(1, 20))
    
    qr_element = RLImage(qr_path, width=55, height=55)
    footer_table = Table([
        [Paragraph(".........................................<br/><b>Pupil Signature</b>", body_style), qr_element, Paragraph(".........................................<br/><b>Headteacher Sign & Stamp</b>", body_style)],
        [Paragraph(f"<b>Serial No:</b> {serial_no}", body_style), "", Paragraph(f"<b>Verification Security Code Protected</b>", body_style)]
    ], colWidths=[260, 200, 260])
    footer_table.setStyle(TableStyle([('ALIGN', (1,0), (1,0), 'CENTER'), ('VALIGN', (0,0), (-1,-1), 'MIDDLE')]))
    story.append(footer_table)
    
    def add_border(canvas, doc):
        canvas.setStrokeColor(colors.HexColor('#1A365D'))
        canvas.setLineWidth(3)
        canvas.rect(20, 20, 752, 572)
        
    doc.build(story, onFirstPage=add_border)
    
    bucket_path = f"issued/{serial_no}.pdf"
    with open(pdf_path, "rb") as f:
        supabase.storage.from_("certificates").upload(bucket_path, f, {"content-type": "application/pdf"})
    
    public_url = supabase.storage.from_("certificates").get_public_url(bucket_path)
    
    supabase.table("certificates").insert({
        "school_id": school_id, "adm_no": payload['adm_no'], "student_name": payload['student_name'],
        "date_of_birth": payload['date_of_birth'], "date_entered": payload['date_entered'],
        "class_entered": payload['class_entered'], "date_left": payload['date_left'],
        "class_left": payload['class_left'], "mean_grade": payload['mean_grade'],
        "serial_no": serial_no, "pdf_storage_url": public_url,
        "ability": payload.get('ability'), "industry": payload.get('industry'), "conduct": payload.get('conduct'),
        "co_curricular": payload.get('co_curricular')
    }).execute()
    
    return {"status": "success", "serial_no": serial_no, "download_url": public_url}

# 3. METRIC METADATA EXTRACTION PIPELINE
@app.get("/school/dashboard")
async def get_school_dashboard(school_id: str = Depends(get_current_school)):
    certs = supabase.table("certificates").select("id, student_name, adm_no, mean_grade, serial_no, created_at").eq("school_id", school_id).execute()
    return {"generated_certificates": certs.data}

# 4. DOWNLOAD LOG INTERCEPTOR HOOK
@app.get("/download/{serial_no}")
async def log_and_download_pdf(serial_no: str, request: Request):
    cert = supabase.table("certificates").select("id, pdf_storage_url").eq("serial_no", serial_no).single().execute()
    if not cert.data:
        raise HTTPException(status_code=404, detail="Certificate payload matching tracking signature not found.")
        
    supabase.table("certificate_usage_logs").insert({
        "certificate_id": cert.data['id'],
        "access_type": "PDF Download",
        "ip_address": request.client.host,
        "user_agent": request.headers.get("user-agent")
    }).execute()
    
    return {"target_secure_download_link": cert.data['pdf_storage_url']}

# 5. AUDIT DATA LOG FEED
@app.get("/school/analytics/usage")
async def get_certificate_usage_dashboard(school_id: str = Depends(get_current_school)):
    logs = supabase.table("certificate_usage_logs").select(
