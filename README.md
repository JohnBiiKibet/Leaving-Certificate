 🇰🇪 Kenya School Leaving Certificate Portal

A secure, multi-tenant digital microservice designed for primary and secondary schools in Kenya to generate official School Leaving Certificates. The system embeds an automated cryptographic QR Code for real-time validation and forgery prevention, integrates with Supabase Object Storage, maintains a robust audit logging metric dashboard, and handles institutional custom branding vectors.

---

 🛠️ Technology Stack
   Backend Framework: FastAPI (Python 3.11)
   Database & Storage Layer: Supabase (PostgreSQL with Row Level Security & Cloud Storage Buckets)
   PDF Generation Core: ReportLab Engine (Configured in standard landscape framing vectors)
   Containerization: Docker (Multi-stage compilation profiles)
   Orchestration Engine: Kubernetes (Scale-out deployments with strict resource boundaries)

---

 📁 Project Directory Structure
```text
leaving-cert-portal/
│
├── .github/workflows/
│   └── deploy.yml           CI/CD pipeline script
├── app.py                   Core FastAPI application microservice
├── Dockerfile               Multi-stage production container blueprint
├── .dockerignore            Prevents copying local workspace junk
├── k8s-deployment.yaml      Kubernetes Deployment, Service, and ConfigMaps
├── requirements.txt         Exact pin-point dependency library versions
└── README.md                Documentation guide map
```

---

 🚀 Quick Start (Local Setup)

 1. Clone & Navigate to Workspace
```bash
git clone https://github.com
cd leaving-cert-portal
```

 2. Configure Environment Variables
Create a local `.env` configuration template in the root folder:
```env
SUPABASE_URL=https://supabase.co
SUPABASE_KEY=your_administrative_service_role_secret_key_here
```
> ⚠️ Security Warning: Never commit the `.env` file to your GitHub repository context.

 3. Install Requirements & Run local server
```bash
pip install -r requirements.txt
uvicorn app:app --reload --host 127.0.0.1 --port 8000
```
Your backend endpoints will become interactively testable at: `http://127.0.0`

---

 🐳 Containerization via Docker

 1. Build Production Image
```bash
docker build -t your-dockerhub-username/leaving-cert-backend:latest .
```

 2. Local Container Test Verification
```bash
docker run -d -p 8000:8000 --env-file .env your-dockerhub-username/leaving-cert-backend:latest
```

---

 ☸️ Orchestration via Kubernetes

 1. Provision Cluster Verification Secrets
Before deploying to your cluster space, securely inject your administrative Supabase secret key signature into the cluster workspace:
```bash
kubectl create secret generic supabase-secrets \
  --from-literal=service-role-key="YOUR_ACTUAL_SECRET_SERVICE_ROLE_KEY"
```

 2. Apply Declarative Configuration Manifests
```bash
kubectl apply -f k8s-deployment.yaml
```

 3. Confirm Operational Health Check Status
```bash
kubectl get pods -l app=leaving-cert
kubectl get svc leaving-cert-service
```

---

 🔌 API Documentation Interface Reference

All operational endpoints expect an `Authorization: Bearer <SUPABASE_SCHOOL_JWT_TOKEN>` header parameter for tenant authentication isolation, except the public download gateway.

 1. Upload School Branding Logo
   Endpoint: `POST /school/upload-logo`
   Payload Type: `multipart/form-data`
   Parameter: `file: UploadFile` (Accepts exclusively `.png`, `.jpg`, `.jpeg`)

 2. Programmatically Generate Leaving Certificate
   Endpoint: `POST /certificates/generate`
   Payload JSON Structure:
```json
{
  "student_name": "John Kiprop",
  "adm_no": "8432",
  "date_of_birth": "2010-05-14",
  "date_entered": "2020-01-06",
  "class_entered": "Class 4",
  "date_left": "2024-11-20",
  "class_left": "Class 8",
  "mean_grade": "A",
  "ability": "Exceptional capability in analytical mathematics",
  "industry": "Highly diligent, methodical homework preparation tracker",
  "conduct": "Excellent, highly respected prefect role model",
  "co_curricular": "Captain of the Track & Field Athletics team"
}
```

 3. School Metrics List Dashboard
   Endpoint: `GET /school/dashboard`
   Returns: Total historically registered digital certificates belonging strictly to the requesting authenticated school's jurisdiction space.

 4. Secure Download Interceptor & Audit Trail Logger
   Endpoint: `GET /download/{serial_no}`
   Behavior: Seamlessly captures client IP addresses and operational headers, commits verification events back to tracking usage metrics, and returns the final file streaming repository link.
