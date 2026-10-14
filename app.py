import os
import datetime
import hashlib
import streamlit as st
import pandas as pd
from typing import Dict, Any

from core.database import init_db, get_db_session
from core.models import Complaint, AuditLog
from core.document_parser import extract_text_from_upload
from core.agent import (
    extract_complaint_from_text,
    chat_with_copilot,
    run_assessment,
    get_groq_client
)
from core.reports import generate_gmp_html_report

# ----------------- PAGE CONFIG -----------------
st.set_page_config(
    page_title="AIVOA.AI - Customer Complaint Management",
    page_icon="💊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize Database
init_db()

# ----------------- CUSTOM THEME CSS -----------------
st.markdown("""
<style>
    /* Dark Theme & Typography */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }

    /* Glassmorphism Cards */
    .gmp-card {
        background: rgba(22, 29, 47, 0.65);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 16px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.25);
    }
    
    .gmp-header {
        font-size: 0.95rem;
        font-weight: 700;
        color: #14b8a6;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        border-bottom: 1px solid rgba(255, 255, 255, 0.08);
        padding-bottom: 6px;
        margin-bottom: 14px;
    }

    /* System Lock Alert Banner */
    .system-lock-banner {
        background: rgba(234, 179, 8, 0.12);
        border: 1px solid rgba(234, 179, 8, 0.35);
        color: #eab308;
        padding: 12px 16px;
        border-radius: 8px;
        font-size: 0.85rem;
        font-weight: 500;
        display: flex;
        align-items: center;
        gap: 10px;
        margin-bottom: 16px;
    }

    /* Regulatory Badges */
    .badge-pill {
        display: inline-block;
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 0.72rem;
        font-weight: 600;
        margin-right: 6px;
        margin-bottom: 4px;
    }
    .badge-fda { background: rgba(99, 102, 241, 0.15); border: 1px solid rgba(99, 102, 241, 0.35); color: #818cf8; }
    .badge-eu { background: rgba(20, 184, 166, 0.15); border: 1px solid rgba(20, 184, 166, 0.35); color: #2dd4bf; }
    .badge-ich { background: rgba(234, 179, 8, 0.15); border: 1px solid rgba(234, 179, 8, 0.35); color: #facc15; }
    .badge-alert { background: rgba(239, 68, 68, 0.15); border: 1px solid rgba(239, 68, 68, 0.35); color: #f87171; }

    /* Timeline styling */
    .timeline-log {
        border-left: 2px solid #4f46e5;
        padding-left: 14px;
        margin-bottom: 12px;
        font-size: 0.85rem;
    }
    .timeline-strike {
        text-decoration: line-through;
        color: #94a3b8;
    }
    .timeline-new {
        color: #10b981;
        font-weight: 600;
    }
    .timeline-time {
        font-size: 0.72rem;
        color: #64748b;
        margin-top: 2px;
    }

    /* 21 CFR Part 11 Stamp */
    .sig-stamp {
        border: 2px dashed #0d9488;
        padding: 14px;
        border-radius: 8px;
        background: rgba(13, 148, 136, 0.08);
        color: #2dd4bf;
        font-size: 0.85rem;
        margin-top: 14px;
    }
</style>
""", unsafe_allow_html=True)


# ----------------- SESSION STATE HELPERS -----------------
DEFAULT_FORM = {
    "complaint_source": "",
    "customer_name": "",
    "product_name": "",
    "product_strength": "",
    "batch_number": "",
    "manufacturing_date": "",
    "expiry_date": "",
    "quantity_affected": "",
    "complaint_type": "",
    "complaint_date": datetime.date.today().strftime("%Y-%m-%d"),
    "description": "",
    "initial_severity": "",
    "priority": "",
    "next_action": "",
    "risk_assessment_details": "",
    "completeness_status": "",
    "completeness_feedback": "",
    "root_cause_recommendation": "",
    "capa_recommendation": "",
    "summary": "",
    "risk_classification_reasoning": ""
}

if "form_data" not in st.session_state:
    st.session_state.form_data = dict(DEFAULT_FORM)

if "active_complaint_id" not in st.session_state:
    st.session_state.active_complaint_id = None

if "active_complaint_code" not in st.session_state:
    st.session_state.active_complaint_code = None

if "complaint_status" not in st.session_state:
    st.session_state.complaint_status = "Pending Triage"

if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
        {"role": "assistant", "content": "Hello! I am your AI Quality Assurance Assistant. Upload a complaint document or chat with me to log and triage this complaint."}
    ]

if "duplicate_alert" not in st.session_state:
    st.session_state.duplicate_alert = None

if "selected_dashboard_id" not in st.session_state:
    st.session_state.selected_dashboard_id = None


# ----------------- DATABASE OPS -----------------
def generate_complaint_code(db) -> str:
    current_year = datetime.datetime.now().year
    count = db.query(Complaint).filter(Complaint.complaint_code.like(f"CC-{current_year}-%")).count()
    return f"CC-{current_year}-{(count + 1):04d}"


def get_all_complaints():
    db = get_db_session()
    try:
        return db.query(Complaint).order_by(Complaint.created_at.desc()).all()
    finally:
        db.close()


def save_complaint_to_db():
    db = get_db_session()
    try:
        data = st.session_state.form_data
        active_id = st.session_state.active_complaint_id
        now = datetime.datetime.utcnow()

        if active_id:
            # Update existing complaint
            comp = db.query(Complaint).filter(Complaint.id == active_id).first()
            if not comp:
                st.error("Complaint record not found.")
                return

            audit_logs = []
            for field, new_val in data.items():
                old_val = getattr(comp, field, None)
                if str(old_val or "") != str(new_val or ""):
                    log = AuditLog(
                        complaint_id=comp.id,
                        action="Update Field",
                        field_name=field,
                        old_value=str(old_val or ""),
                        new_value=str(new_val or ""),
                        changed_by="User",
                        timestamp=now
                    )
                    audit_logs.append(log)
                    setattr(comp, field, new_val)

            comp.status = st.session_state.complaint_status
            comp.updated_at = now
            if audit_logs:
                db.add_all(audit_logs)
            db.commit()
            st.success(f"Complaint {comp.complaint_code} updated successfully!")
        else:
            # Create new complaint
            code = generate_complaint_code(db)
            comp = Complaint(
                complaint_code=code,
                status=st.session_state.complaint_status or "Pending Triage",
                **data
            )
            db.add(comp)
            db.commit()
            db.refresh(comp)

            # Audit log for creation
            log = AuditLog(
                complaint_id=comp.id,
                action="Create",
                changed_by="User",
                timestamp=now
            )
            db.add(log)
            db.commit()

            st.session_state.active_complaint_id = comp.id
            st.session_state.active_complaint_code = comp.complaint_code
            st.success(f"Complaint successfully logged as **{code}**!")
    except Exception as e:
        db.rollback()
        st.error(f"Error saving complaint: {e}")
    finally:
        db.close()


def reset_form_state():
    st.session_state.form_data = dict(DEFAULT_FORM)
    st.session_state.active_complaint_id = None
    st.session_state.active_complaint_code = None
    st.session_state.complaint_status = "Pending Triage"
    st.session_state.duplicate_alert = None
    st.session_state.chat_history = [
        {"role": "assistant", "content": "Form has been reset. Ready for new complaint document or details."}
    ]


# ----------------- SIDEBAR -----------------
with st.sidebar:
    st.markdown("""
    <div style="display:flex; align-items:center; gap:12px; margin-bottom:18px;">
        <div style="background:linear-gradient(135deg, #4f46e5 0%, #14b8a6 100%); width:44px; height:44px; border-radius:10px; display:flex; align-items:center; justify-content:center; font-weight:800; font-size:1.3rem; color:white;">A</div>
        <div>
            <div style="font-size:1.15rem; font-weight:800; letter-spacing:0.04em; color:#f8fafc;">AIVOA.AI</div>
            <div style="font-size:0.7rem; color:#94a3b8; font-weight:600;">QMS ASSURANCE MODULE</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    nav_selection = st.radio(
        "Navigation",
        ["📝 Log Complaint", "📊 QA Dashboard & Registry"],
        label_visibility="collapsed"
    )

    st.markdown("---")
    
    # Engine status
    groq_active = get_groq_client() is not None
    if groq_active:
        st.success("🟢 **Groq LLM Engine**: Connected", icon="✅")
    else:
        st.info("🟡 **AI Engine**: Smart Fallback Active\n*(Valid GROQ_API_KEY optional)*")

    # DB Stats
    db = get_db_session()
    try:
        total_comps = db.query(Complaint).count()
        critical_count = db.query(Complaint).filter(Complaint.initial_severity == "Critical").count()
        pending_count = db.query(Complaint).filter(Complaint.status == "Pending Triage").count()
    finally:
        db.close()

    st.markdown("### System Metrics")
    m_col1, m_col2 = st.columns(2)
    m_col1.metric("Registered", total_comps)
    m_col2.metric("Critical", critical_count)
    st.metric("Pending Triage", pending_count)

    st.markdown("---")
    st.caption("GMP Assurance &bull; 21 CFR Part 11 &bull; EU Annex 15\nVersion 1.0 Full Python Edition")


# ==============================================================================
# TAB 1: LOG CUSTOMER COMPLAINT
# ==============================================================================
if nav_selection == "📝 Log Complaint":
    header_col1, header_col2 = st.columns([2, 1])
    with header_col1:
        st.title("Log Customer Complaint")
        st.caption("Active Pharmaceutical Ingredients (API) & Finished Dosage Forms (FDF) Quality Management")
    with header_col2:
        badge_code = st.session_state.active_complaint_code or "Draft Mode"
        badge_status = st.session_state.complaint_status
        st.markdown(f"""
        <div style="text-align:right; margin-top:14px;">
            <span style="background:rgba(99,102,241,0.2); border:1px solid #4f46e5; color:#818cf8; padding:6px 14px; border-radius:8px; font-weight:700; font-size:0.85rem;">
                {badge_code}
            </span>
            <span style="background:rgba(234,179,8,0.2); border:1px solid #eab308; color:#facc15; padding:6px 14px; border-radius:8px; font-weight:700; font-size:0.85rem; margin-left:8px;">
                {badge_status}
            </span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # Two column layout: Left = System Locked Form, Right = AI Intake Assistant
    col_form, col_assistant = st.columns([1.2, 1.0], gap="large")

    # ----------------- LEFT: SYSTEM LOCKED FORM -----------------
    with col_form:
        st.markdown("""
        <div class="system-lock-banner">
            <span>⚠️</span>
            <span><strong>System Lock:</strong> Manual entry is disabled. Use the AI Intake Assistant on the right (upload, paste, or chat) to populate and update fields.</span>
        </div>
        """, unsafe_allow_html=True)

        fd = st.session_state.form_data

        # Section 1: Origin & Customer Details
        st.markdown('<div class="gmp-card">', unsafe_allow_html=True)
        st.markdown('<div class="gmp-header">1. Origin & Customer Details</div>', unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            st.text_input("Complaint Source", value=fd.get("complaint_source", ""), disabled=True, placeholder="Awaiting AI extraction...")
        with c2:
            st.text_input("Customer Name", value=fd.get("customer_name", ""), disabled=True, placeholder="Awaiting AI extraction...")
        st.markdown('</div>', unsafe_allow_html=True)

        # Section 2: Product & Batch Identification
        st.markdown('<div class="gmp-card">', unsafe_allow_html=True)
        st.markdown('<div class="gmp-header">2. Product & Batch Identification</div>', unsafe_allow_html=True)
        c3, c4 = st.columns(2)
        with c3:
            st.text_input("Product Name", value=fd.get("product_name", ""), disabled=True, placeholder="Awaiting AI extraction...")
        with c4:
            st.text_input("Product Strength / Grade", value=fd.get("product_strength", ""), disabled=True, placeholder="Awaiting AI extraction...")
        c5, c6 = st.columns(2)
        with c5:
            st.text_input("Batch / Lot Number", value=fd.get("batch_number", ""), disabled=True, placeholder="Awaiting AI extraction...")
        with c6:
            st.text_input("Quantity Affected", value=fd.get("quantity_affected", ""), disabled=True, placeholder="Awaiting AI extraction...")
        c7, c8 = st.columns(2)
        with c7:
            st.text_input("Manufacturing Date", value=fd.get("manufacturing_date", ""), disabled=True, placeholder="YYYY-MM-DD")
        with c8:
            st.text_input("Expiry Date", value=fd.get("expiry_date", ""), disabled=True, placeholder="YYYY-MM-DD")
        st.markdown('</div>', unsafe_allow_html=True)

        # Section 3: Complaint Details & Description
        st.markdown('<div class="gmp-card">', unsafe_allow_html=True)
        st.markdown('<div class="gmp-header">3. Complaint Details & Description</div>', unsafe_allow_html=True)
        c9, c10 = st.columns([1.2, 0.8])
        with c9:
            st.text_input("Complaint Type", value=fd.get("complaint_type", ""), disabled=True, placeholder="Awaiting AI extraction...")
        with c10:
            st.text_input("Complaint Date", value=fd.get("complaint_date", datetime.date.today().strftime("%Y-%m-%d")), disabled=True)
        st.text_area("Detailed Complaint Description", value=fd.get("description", ""), height=100, disabled=True, placeholder="Awaiting AI extraction...")
        st.markdown('</div>', unsafe_allow_html=True)

        # Section 4: Initial Assessment & Priority
        st.markdown('<div class="gmp-card">', unsafe_allow_html=True)
        st.markdown('<div class="gmp-header">4. Initial Assessment & Priority</div>', unsafe_allow_html=True)
        c11, c12 = st.columns(2)
        with c11:
            st.text_input("Initial Severity", value=fd.get("initial_severity", ""), disabled=True, placeholder="Awaiting AI triage...")
        with c12:
            st.text_input("Priority", value=fd.get("priority", ""), disabled=True, placeholder="Awaiting AI triage...")
        st.markdown('</div>', unsafe_allow_html=True)

        # Section 5: AI Co-Pilot Risk Assessment
        st.markdown('<div class="gmp-card">', unsafe_allow_html=True)
        st.markdown('<div class="gmp-header">5. AI Co-Pilot Risk Assessment</div>', unsafe_allow_html=True)
        st.text_input("Suggested Next Action", value=fd.get("next_action", ""), disabled=True, placeholder="Awaiting AI assessment...")
        st.text_area("Risk Assessment Details & Rationale", value=fd.get("risk_assessment_details", ""), height=80, disabled=True, placeholder="Awaiting AI assessment...")

        # Regulatory compliance badges
        severity = fd.get("initial_severity")
        if severity:
            badges_html = """
            <div style="margin-top:10px;">
                <span class="badge-pill badge-fda">21 CFR §211.198 (FDA)</span>
                <span class="badge-pill badge-eu">EU GMP Chapter 8</span>
                <span class="badge-pill badge-ich">ICH Q9 Risk Mgt</span>
            """
            if severity == "Critical":
                badges_html += '<span class="badge-pill badge-alert">⚠️ 24h Authority Alert Rule</span>'
            badges_html += "</div>"
            st.markdown(badges_html, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # AI Insights Section (If any tool ran)
        has_insights = any([
            fd.get("summary"),
            fd.get("completeness_status"),
            fd.get("root_cause_recommendation"),
            fd.get("capa_recommendation"),
            fd.get("risk_classification_reasoning")
        ])
        if has_insights:
            st.markdown('<div class="gmp-card">', unsafe_allow_html=True)
            st.markdown('<div class="gmp-header">AI Copilot Quality Analysis</div>', unsafe_allow_html=True)
            if fd.get("summary"):
                st.markdown(f"**Executive Summary:**\n{fd.get('summary')}")
            if fd.get("completeness_status"):
                status_color = "#10b981" if fd.get("completeness_status") == "Complete" else "#ef4444"
                st.markdown(f"**Completeness:** <span style='color:{status_color}; font-weight:700;'>{fd.get('completeness_status')}</span> &bull; {fd.get('completeness_feedback', '')}", unsafe_allow_html=True)
            if fd.get("root_cause_recommendation"):
                st.markdown(f"**Root Cause Recommendations:**\n{fd.get('root_cause_recommendation')}")
            if fd.get("capa_recommendation"):
                st.markdown(f"**CAPA Plan:**\n{fd.get('capa_recommendation')}")
            if fd.get("risk_classification_reasoning"):
                st.markdown(f"**Risk Rationale:**\n{fd.get('risk_classification_reasoning')}")
            st.markdown('</div>', unsafe_allow_html=True)

        # Duplicate Alert
        if st.session_state.duplicate_alert:
            st.error(st.session_state.duplicate_alert, icon="🚨")

        # Form Buttons
        btn_c1, btn_c2 = st.columns([1, 2])
        with btn_c1:
            if st.button("🔄 Reset Form", use_container_width=True):
                reset_form_state()
                st.rerun()
        with btn_c2:
            save_label = "💾 Update Complaint" if st.session_state.active_complaint_id else "💾 Save Complaint"
            if st.button(save_label, type="primary", use_container_width=True):
                save_complaint_to_db()
                st.rerun()

    # ----------------- RIGHT: AI INTAKE ASSISTANT -----------------
    with col_assistant:
        st.markdown('<div class="gmp-card">', unsafe_allow_html=True)
        st.markdown('<div class="gmp-header">📁 AI Document Ingestion</div>', unsafe_allow_html=True)
        
        uploaded_doc = st.file_uploader(
            "Upload Complaint Document (.pdf, .docx, .txt, .eml)",
            type=["pdf", "docx", "txt", "eml"],
            help="LangGraph extraction pipeline processes the text and instantly populates the form fields."
        )

        if uploaded_doc is not None:
            doc_key = f"processed_{uploaded_doc.name}_{uploaded_doc.size}"
            if doc_key not in st.session_state:
                with st.spinner("Extracting GMP parameters from document..."):
                    try:
                        text_content = extract_text_from_upload(uploaded_doc)
                        if not text_content:
                            st.warning("Uploaded file did not contain readable text.")
                        else:
                            extracted = extract_complaint_from_text(text_content)
                            st.session_state.form_data.update(extracted)
                            st.session_state[doc_key] = True
                            st.session_state.chat_history.append({
                                "role": "assistant",
                                "content": f"✅ Extracted data from **{uploaded_doc.name}** and populated the form fields. Batch: {extracted.get('batch_number')}, Severity: {extracted.get('initial_severity')}."
                            })
                            st.rerun()
                    except Exception as ex:
                        st.error(f"Error parsing document: {ex}")

        # Paste raw text toggle
        with st.expander("📋 Or Paste Complaint Text / Email"):
            sample_text = (
                "From: reporter@saintjudepharmacy.com\n"
                "To: qualityassurance@aivoa.ai\n"
                "Subject: Defect Report - Paracetamol 500mg Batch P1234\n\n"
                "Dear Quality Team,\n"
                "We are writing to report a major defect in the latest shipment of Paracetamol 500mg tablets received on July 25th, 2026.\n"
                "Upon opening the box for Batch/Lot Number P1234 (Mfg: 2025-06-15, Exp: 2027-06-15), we noticed that approximately 15 kg of material (roughly 20 bottles) had compromised sealing foil on the primary blisters. Many tablets were crushed, and there is visible black discoloration/residue on the container seals, indicating potential manufacturing contamination.\n"
                "Best regards,\nDr. Alan Vance\nSaint Jude Pharmacy Distribution"
            )
            raw_text_input = st.text_area("Paste complaint message:", height=140, placeholder="Paste email, letter, or inspection report here...")
            p_col1, p_col2 = st.columns(2)
            with p_col1:
                if st.button("Load Demo Sample", use_container_width=True):
                    raw_text_input = sample_text
                    with st.spinner("Analyzing demo complaint text..."):
                        extracted = extract_complaint_from_text(sample_text)
                        st.session_state.form_data.update(extracted)
                        st.session_state.chat_history.append({
                            "role": "assistant",
                            "content": "Loaded demo complaint from Saint Jude Pharmacy (Paracetamol 500mg, Batch P1234). All form fields populated."
                        })
                        st.rerun()
            with p_col2:
                if st.button("⚡ Extract Text", type="primary", use_container_width=True):
                    if raw_text_input.strip():
                        with st.spinner("Analyzing text with AI agent..."):
                            extracted = extract_complaint_from_text(raw_text_input)
                            st.session_state.form_data.update(extracted)
                            st.session_state.chat_history.append({
                                "role": "assistant",
                                "content": "Parsed complaint text and updated form fields."
                            })
                            st.rerun()
                    else:
                        st.warning("Please paste some text first.")
        st.markdown('</div>', unsafe_allow_html=True)

        # AI Interactive Chat Copilot
        st.markdown('<div class="gmp-card">', unsafe_allow_html=True)
        st.markdown('<div class="gmp-header">💬 AI Complaint Intake Assistant</div>', unsafe_allow_html=True)

        # Render chat messages container
        chat_container = st.container(height=320)
        with chat_container:
            for message in st.session_state.chat_history:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])

        # Quick chips
        st.caption("Quick actions & updates:")
        chip_col1, chip_col2, chip_col3, chip_col4 = st.columns(4)
        with chip_col1:
            if st.button("Strength 250mg", use_container_width=True):
                st.session_state.form_data["product_strength"] = "250mg"
                st.session_state.chat_history.append({"role": "user", "content": "Set product strength to 250mg"})
                st.session_state.chat_history.append({"role": "assistant", "content": "Product strength updated to **250mg**."})
                st.rerun()
        with chip_col2:
            if st.button("Source: Email", use_container_width=True):
                st.session_state.form_data["complaint_source"] = "Email"
                st.session_state.chat_history.append({"role": "user", "content": "Set complaint source to Email"})
                st.session_state.chat_history.append({"role": "assistant", "content": "Complaint source updated to **Email**."})
                st.rerun()
        with chip_col3:
            if st.button("Batch BMX24602", use_container_width=True):
                st.session_state.form_data["batch_number"] = "BMX24602"
                st.session_state.chat_history.append({"role": "user", "content": "Update batch to BMX24602"})
                st.session_state.chat_history.append({"role": "assistant", "content": "Batch number updated to **BMX24602**."})
                st.rerun()
        with chip_col4:
            if st.button("Qty 48 caps", use_container_width=True):
                st.session_state.form_data["quantity_affected"] = "48 capsules"
                st.session_state.chat_history.append({"role": "user", "content": "Update quantity affected to 48 capsules"})
                st.session_state.chat_history.append({"role": "assistant", "content": "Quantity affected updated to **48 capsules**."})
                st.rerun()

        # Chat Input
        user_input = st.chat_input("Instruct AI assistant to modify fields or ask questions...")
        if user_input:
            st.session_state.chat_history.append({"role": "user", "content": user_input})
            with st.spinner("AI Copilot thinking..."):
                chat_res = chat_with_copilot(
                    message=user_input,
                    chat_history=st.session_state.chat_history,
                    current_fields=st.session_state.form_data
                )
                st.session_state.form_data.update(chat_res.get("suggested_fields", {}))
                st.session_state.chat_history.append({"role": "assistant", "content": chat_res.get("response", "Updated.")})
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

        # AI Copilot Analysis Tools (6 Quick Assessment Tools)
        st.markdown('<div class="gmp-card">', unsafe_allow_html=True)
        st.markdown('<div class="gmp-header">✨ AI Copilot Quality Assessor Tools</div>', unsafe_allow_html=True)
        
        t_col1, t_col2 = st.columns(2)
        with t_col1:
            if st.button("📋 Completeness Check", use_container_width=True):
                with st.spinner("Checking completeness..."):
                    res = run_assessment("completeness", st.session_state.form_data)
                    st.session_state.form_data.update(res)
                    st.rerun()
            if st.button("🔥 Risk Classification", use_container_width=True):
                with st.spinner("Evaluating risk level..."):
                    res = run_assessment("risk", st.session_state.form_data)
                    st.session_state.form_data.update(res)
                    st.rerun()
            if st.button("🧠 Root Cause Analysis", use_container_width=True):
                with st.spinner("Analyzing potential root causes..."):
                    res = run_assessment("root_cause", st.session_state.form_data)
                    st.session_state.form_data.update(res)
                    st.rerun()
        with t_col2:
            if st.button("✅ CAPA Suggestion", use_container_width=True):
                with st.spinner("Generating CAPA recommendations..."):
                    res = run_assessment("capa", st.session_state.form_data)
                    st.session_state.form_data.update(res)
                    st.rerun()
            if st.button("📑 Duplicate Check", use_container_width=True):
                with st.spinner("Scanning registry for duplicates..."):
                    res = run_assessment("duplicate", st.session_state.form_data)
                    if res.get("is_duplicate"):
                        st.session_state.duplicate_alert = res.get("duplicate_details")
                    else:
                        st.session_state.duplicate_alert = None
                        st.toast("No duplicate complaints detected for this batch.", icon="✅")
                    st.rerun()
            if st.button("📝 Summarize Complaint", use_container_width=True):
                with st.spinner("Synthesizing executive summary..."):
                    res = run_assessment("summary", st.session_state.form_data)
                    st.session_state.form_data.update(res)
                    st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)


# ==============================================================================
# TAB 2: QA DASHBOARD & REGISTRY
# ==============================================================================
else:
    st.title("Quality Assurance Dashboard")
    st.caption("Traceability audit trails & database registry of logged GMP customer complaints")
    st.markdown("---")

    complaints_list = get_all_complaints()

    if not complaints_list:
        st.info("No complaints logged in the database registry yet. Navigate to 'Log Complaint' to register your first record!")
    else:
        # Layout: Table on left, detailed inspector on right
        dash_col1, dash_col2 = st.columns([1.1, 1.0], gap="large")

        with dash_col1:
            st.markdown('<div class="gmp-card">', unsafe_allow_html=True)
            st.markdown('<div class="gmp-header">Logged Quality Complaints Registry</div>', unsafe_allow_html=True)

            # Build display dataframe
            rows = []
            for c in complaints_list:
                rows.append({
                    "ID": c.id,
                    "Code": c.complaint_code,
                    "Product": f"{c.product_name or ''} {c.product_strength or ''}".strip(),
                    "Batch": c.batch_number or "N/A",
                    "Severity": c.initial_severity or "Major",
                    "Status": c.status,
                    "Date": c.complaint_date or c.created_at.strftime("%Y-%m-%d")
                })
            df = pd.DataFrame(rows)
            st.dataframe(df.drop(columns=["ID"]), use_container_width=True, hide_index=True)

            # Selection mechanism
            comp_options = {c.id: f"{c.complaint_code} - {c.product_name} (Batch {c.batch_number})" for c in complaints_list}
            selected_id = st.selectbox(
                "Select a complaint to inspect full audit trail & export report:",
                options=list(comp_options.keys()),
                format_func=lambda x: comp_options[x]
            )
            st.session_state.selected_dashboard_id = selected_id
            st.markdown('</div>', unsafe_allow_html=True)

        with dash_col2:
            st.markdown('<div class="gmp-card">', unsafe_allow_html=True)
            sel_comp = next((c for c in complaints_list if c.id == st.session_state.selected_dashboard_id), complaints_list[0])

            # Header info
            st.markdown(f"""
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px; border-bottom:1px solid rgba(255,255,255,0.08); padding-bottom:8px;">
                <div>
                    <h3 style="margin:0; font-size:1.2rem; color:#818cf8;">{sel_comp.complaint_code}</h3>
                    <span style="font-size:0.75rem; color:#94a3b8;">Created: {sel_comp.created_at.strftime('%Y-%m-%d %H:%M UTC')}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Status changer
            current_status = sel_comp.status
            new_status = st.selectbox(
                "Workflow Status:",
                ["Pending Triage", "Under Investigation", "Resolved"],
                index=["Pending Triage", "Under Investigation", "Resolved"].index(current_status) if current_status in ["Pending Triage", "Under Investigation", "Resolved"] else 0
            )

            if new_status != current_status:
                db = get_db_session()
                try:
                    c_db = db.query(Complaint).filter(Complaint.id == sel_comp.id).first()
                    if c_db:
                        c_db.status = new_status
                        log = AuditLog(
                            complaint_id=c_db.id,
                            action="Update Field",
                            field_name="status",
                            old_value=current_status,
                            new_value=new_status,
                            changed_by="User",
                            timestamp=datetime.datetime.utcnow()
                        )
                        db.add(log)
                        db.commit()
                        st.success(f"Status changed to {new_status}")
                        st.rerun()
                finally:
                    db.close()

            # Actions row: Load into form, Sign & Resolve, Export Report
            act_col1, act_col2, act_col3 = st.columns(3)
            with act_col1:
                if st.button("✏️ Edit in Form", use_container_width=True):
                    st.session_state.form_data = sel_comp.to_dict()
                    st.session_state.active_complaint_id = sel_comp.id
                    st.session_state.active_complaint_code = sel_comp.complaint_code
                    st.session_state.complaint_status = sel_comp.status
                    st.session_state.chat_history.append({
                        "role": "assistant",
                        "content": f"Loaded complaint {sel_comp.complaint_code} into form for review/updates."
                    })
                    st.rerun()
            with act_col2:
                # 21 CFR Part 11 Electronic Signature Stamp
                if sel_comp.status != "Resolved":
                    if st.button("🔒 Sign & Resolve", type="primary", use_container_width=True):
                        db = get_db_session()
                        try:
                            c_db = db.query(Complaint).filter(Complaint.id == sel_comp.id).first()
                            c_db.status = "Resolved"
                            log = AuditLog(
                                complaint_id=c_db.id,
                                action="Sign Record",
                                field_name="status",
                                old_value=current_status,
                                new_value="Resolved",
                                changed_by="QA-USER (FDA 21 CFR Part 11)",
                                timestamp=datetime.datetime.utcnow()
                            )
                            db.add(log)
                            db.commit()
                            st.success("Record electronically signed and resolved!")
                            st.rerun()
                        finally:
                            db.close()
                else:
                    st.button("✅ Signed & Closed", disabled=True, use_container_width=True)

            with act_col3:
                # Generate HTML Report for download
                report_html = generate_gmp_html_report(sel_comp.to_dict())
                st.download_button(
                    label="📄 Export Report",
                    data=report_html,
                    file_name=f"GMP_Report_{sel_comp.complaint_code}.html",
                    mime="text/html",
                    use_container_width=True
                )

            # Electronic Signature Stamp Banner (if Resolved)
            if sel_comp.status == "Resolved":
                hash_val = hashlib.sha256(f"{sel_comp.complaint_code}-{sel_comp.id}".encode("utf-8")).hexdigest()[:24]
                st.markdown(f"""
                <div class="sig-stamp">
                    <div style="font-weight:700; display:flex; align-items:center; gap:6px;">
                        <span>&#10004;</span> 21 CFR PART 11 ELECTRONIC SIGNATURE STAMP
                    </div>
                    <div style="font-size:0.75rem; color:#94a3b8; margin-top:4px;">
                        Status: <strong>Approved & Closed</strong><br/>
                        Signer: <strong>Quality Assurance Assessor (QA-USER)</strong><br/>
                        Verification Hash: <code style="color:#2dd4bf;">sha256-{hash_val}dfa{sel_comp.complaint_code.lower()}</code>
                    </div>
                </div>
                """, unsafe_allow_html=True)

            st.markdown("---")

            # Product & Customer Parameters
            p1, p2 = st.columns(2)
            with p1:
                st.markdown(f"**Customer:** {sel_comp.customer_name or 'N/A'}")
                st.markdown(f"**Source:** {sel_comp.complaint_source or 'N/A'}")
                st.markdown(f"**Severity:** `{sel_comp.initial_severity or 'Major'}`")
            with p2:
                st.markdown(f"**Product:** {sel_comp.product_name or 'N/A'} ({sel_comp.product_strength or 'N/A'})")
                st.markdown(f"**Batch:** `{sel_comp.batch_number or 'N/A'}`")
                st.markdown(f"**Qty Affected:** {sel_comp.quantity_affected or 'N/A'}")

            st.markdown(f"**Issue Description:**")
            st.info(sel_comp.description or "No description provided.")

            # GMP Traceability Audit Trail Timeline
            st.markdown('<div class="gmp-header" style="margin-top:16px;">GMP Traceability Audit Trail</div>', unsafe_allow_html=True)
            logs = sel_comp.logs
            if not logs:
                st.caption("No audit log events recorded.")
            else:
                for log in logs:
                    if log.action == "Create":
                        st.markdown(f"""
                        <div class="timeline-log">
                            <strong>Complaint created in database</strong>
                            <div class="timeline-time">By {log.changed_by} &bull; {log.timestamp.strftime('%Y-%m-%d %H:%M:%S UTC')}</div>
                        </div>
                        """, unsafe_allow_html=True)
                    elif log.action == "Sign Record":
                        st.markdown(f"""
                        <div class="timeline-log">
                            <strong>Electronic Record Electronically Signed & Resolved</strong>
                            <div class="timeline-time">By {log.changed_by} &bull; {log.timestamp.strftime('%Y-%m-%d %H:%M:%S UTC')}</div>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown(f"""
                        <div class="timeline-log">
                            <strong>Updated field: {str(log.field_name).replace('_', ' ').upper()}</strong>
                            <div>Change: <span class="timeline-strike">"{log.old_value or 'empty'}"</span> &rarr; <span class="timeline-new">"{log.new_value}"</span></div>
                            <div class="timeline-time">By {log.changed_by} &bull; {log.timestamp.strftime('%Y-%m-%d %H:%M:%S UTC')}</div>
                        </div>
                        """, unsafe_allow_html=True)

            # Delete button at bottom
            st.markdown("---")
            if st.button("🗑️ Delete Complaint Record", type="secondary"):
                db = get_db_session()
                try:
                    c_to_del = db.query(Complaint).filter(Complaint.id == sel_comp.id).first()
                    if c_to_del:
                        db.delete(c_to_del)
                        db.commit()
                        st.warning(f"Complaint {sel_comp.complaint_code} deleted.")
                        st.rerun()
                finally:
                    db.close()

            st.markdown('</div>', unsafe_allow_html=True)
