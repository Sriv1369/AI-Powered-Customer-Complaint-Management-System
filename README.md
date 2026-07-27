# AI-Powered Customer Complaint Management System

An AI-powered Quality Management System (QMS) module tailored for the pharmaceutical manufacturing industry (Active Pharmaceutical Ingredients [API] and Finished Dosage Forms [FDF]). 

This application leverages a **React/Redux** frontend and a **FastAPI/LangGraph** backend powered by **Groq** LLMs to ingest customer complaints (via PDF, DOCX, TXT, or Email), automatically extract structured GMP tracing data, refine fields using an interactive AI Chat Copilot, run compliance assessments, and record full audit trails in the database registry.

---

## 🌟 Key Features

1. **System Locked Form (No Manual Entry)**:
   - To strictly comply with the challenge rules, all input elements on the Left Form are set to `readOnly` and selects to `disabled`.
   - A yellow **System Lock Alert Banner** notifies the operator: *“System Lock: Manual entry is disabled. Use the AI Assistant on the right to populate and edit fields.”*
   - Field values can only be populated or modified via the AI Document Ingestion or the Chat Copilot.
2. **AI Document Extraction**:
   - Upload complaint files (`.pdf`, `.docx`, `.txt`, `.eml`) or paste raw complaint text.
   - A LangGraph extraction pipeline processes the text and instantly populates the form fields.
3. **Interactive AI Chat Copilot**:
   - Talk to the intake assistant to consult details or instruct it to update form fields dynamically (e.g. *“sorry, the batch number is BMX24602 and the affected quantity is 48 capsules”*).
4. **AI Co-Pilot Risk Assessment (Section 5)**:
   - **Initial Severity & Priority**: Evaluated using AI reasoning (Critical, Major, Minor).
   - **Suggested Next Action**: e.g., *“Route to QA investigation and issue replacement”* or *“Route to QA investigation and initiate raw material audit”*.
   - **Risk Assessment Details & Rationale**: Real-time justification of safety and GMP compliance risks based on FDA/EU regulations.
5. **GMP Compliance Registry & Audit Trail**:
   - Save logged complaints into the database registry.
   - Access a detailed **Traceability Timeline** listing every field update, previous values, new values, timestamps, and whether the modification was done by a "User" or the "AI Copilot".
6. **Additional QA Assessor Tools**:
   - Completeness Check, Root Cause recommendations, CAPA generation, Duplicate Detection, and executive Summarization.

---

## 🛠️ Technology Stack

- **Frontend**: React, Redux Toolkit (State Management), Lucide React (Icons), Vanilla CSS (Custom Glassmorphism Dark Theme, Inter font).
- **Backend**: Python, FastAPI, SQLAlchemy, SQLite (default fallback) / PostgreSQL / MySQL support.
- **AI Agent**: LangGraph (State Graphs for Extraction, Chat, and Assessments).
- **LLM APIs**: Groq client calling `gemma2-9b-it` (for data extraction) and `llama-3.3-70b-versatile` (for conversational chat and assessments).

---

## 🚀 How to Run the Project

### Prerequisite
Make sure you have the following installed on your system:
- **Node.js** (v18+)
- **Python** (v3.10+)

### 1. Environment Variable Setup (`.env`)
Make sure a `.env` file exists at the root of the project containing your Groq API key:
```env
GROQ_API_KEY=gsk_your_actual_groq_api_key_here
```
*Note: The application has a smart fallback mock engine that mimics all agent reasoning, conversational chat, and extraction logic if the API key is not supplied, starts with an invalid prefix (such as `sk_`), or encounters runtime errors. The system will alert you but remain fully functional in fallback mode.*

---

### 2. Quick Run (Windows)
Double-click the **`run.bat`** file in the root folder, or run it in your shell:
```powershell
.\run.bat
```
This script will:
1. Boot the FastAPI backend in a new command prompt window (`http://localhost:8000`).
2. Boot the React dev server in a second command prompt window (`http://localhost:5173`).

---

### 3. Manual Run (Platform-Independent)

If you prefer starting the services manually, open two terminal windows:

#### Terminal 1: Python FastAPI Backend
```bash
# Navigate to the backend directory
cd backend

# Install dependencies
pip install -r requirements.txt

# Run the backend server
python run.py
```
*The API is now running at `http://localhost:8000` with Swagger docs available at `http://localhost:8000/docs`.*

#### Terminal 2: React Frontend
```bash
# Navigate to the frontend directory
cd frontend

# Install package dependencies
npm install

# Run the Vite React client
npm run dev
```
*The frontend web application is now active at `http://localhost:5173/`.*

---

## 🔬 Sample Text for Testing / Demo
Copy and paste the text below into the uploader area to see the AI agent in action:

> **From**: reporter@saintjudepharmacy.com
> **To**: qualityassurance@aivoa.ai
> **Subject**: Defect Report - Paracetamol 500mg Batch P1234
> 
> Dear Quality Team,
> We are writing to report a major defect in the latest shipment of Paracetamol 500mg tablets that we received on July 25th, 2026. 
> 
> Upon opening the box for Batch/Lot Number P1234 (Mfg: 2025-06-15, Exp: 2027-06-15), we noticed that approximately 15 kg of material (roughly 20 bottles) had compromised sealing foil on the primary blisters. Many tablets were crushed, and there is visible black discoloration/residue on the container seals, indicating potential manufacturing contamination. 
> 
> One of our pharmacists noticed this prior to dispensing, so luckily no patients have taken this batch yet. Please log this complaint, initiate a CAPA, and let us know if we should return the defective stock.
> 
> Best regards,
> Dr. Alan Vance
> Saint Jude Pharmacy Distribution
