# AI-Powered Customer Complaint Management System (Full Python Edition)

An AI-powered Quality Management System (QMS) module tailored for the pharmaceutical manufacturing industry (Active Pharmaceutical Ingredients [API] and Finished Dosage Forms [FDF]).

This application has been converted into a **100% Full-Stack Python application** using **Streamlit, SQLAlchemy, and Groq LLMs (with smart heuristic fallback)**. It eliminates all Node.js, npm, and Vite dependencies, running seamlessly from a single Python command.

---

## 🌟 Key Features

1. **System-Locked Complaint Form (No Manual Entry)**:
   - Complies with strict data-integrity rules: all form fields are locked in read-only mode.
   - An alert banner reminds operators that fields can only be populated or modified via AI Ingestion or the Chat Copilot.
2. **AI Document Ingestion**:
   - Supports uploading `.pdf`, `.docx`, `.txt`, and `.eml` files or pasting raw complaint text.
   - The AI agent extracts GMP tracing parameters (Customer, Product, Batch, Dates, Quantities, Defect Type, Initial Severity, Priority, Next Action, Risk Rationale).
3. **Interactive AI Chat Copilot**:
   - Conversational assistant with instant form mutation (e.g., *"sorry, the batch number is BMX24602 and the affected quantity is 48 capsules"*).
   - Quick action chips for common corrections.
4. **AI Copilot Quality Assessor Tools (6 Built-in Tools)**:
   - **Completeness Check**: Evaluates presence of mandatory GMP parameters.
   - **Risk Classification**: Triages severity under EU Annex 15 and FDA guidance.
   - **Root Cause Analysis**: Suggests 3 plausible technical root causes.
   - **CAPA Suggestion**: Generates structured Correction, Corrective Action, and Preventive Action plans.
   - **Duplicate Detection**: Flags matching batch records in the registry.
   - **Executive Summarization**: Synthesizes a 2-3 sentence QA review summary.
5. **QA Dashboard & GMP Registry**:
   - Database registry of all logged complaints with search and workflow status transitions (`Pending Triage` &rarr; `Under Investigation` &rarr; `Resolved`).
   - **21 CFR Part 11 Electronic Signature Stamp**: Cryptographic SHA-256 hash stamp for approved and closed complaints.
   - **Traceability Audit Trail**: Chronological event timeline recording every field change, author (`User` or `AI Copilot`), old value strike-through, and new value.
   - **Export GMP Report**: One-click download of a self-contained, printable HTML quality certificate.

---

## 🛠️ Technology Stack

- **UI & Application**: Python, Streamlit (Custom Glassmorphism Dark Theme)
- **Database & ORM**: SQLAlchemy 2.0, SQLite (default) / PostgreSQL / MySQL
- **AI Agent**: Groq client calling `gemma2-9b-it` (extraction) and `llama-3.3-70b-versatile` (chat & assessments)
- **Fallback Mock Engine**: Built-in regex and heuristic engine for full offline / no-API-key functionality
- **Document Parsers**: PyPDF, python-docx

---

## 🚀 How to Run

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment (Optional)
Copy `.env.example` to `.env` and add your Groq API key:
```env
GROQ_API_KEY=gsk_your_groq_api_key_here
```
*(If no API key is provided, the system automatically runs in fallback mode with full scenario support!)*

### 3. Launch the Application
- **Windows**: Double-click `run.bat` or run:
  ```powershell
  .\run.bat
  ```
- **Platform-Independent**:
  ```bash
  python run.py
  # OR
  streamlit run app.py
  ```
The web application will open automatically in your browser at `http://localhost:8501`.

---

## 🔬 Sample Text for Testing / Demo

Copy and paste the text below into the uploader area or click **"Load Demo Sample"** inside the app:

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
