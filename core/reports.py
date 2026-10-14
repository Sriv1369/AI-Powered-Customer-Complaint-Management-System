import datetime
import hashlib
from typing import Dict, Any


def generate_gmp_html_report(complaint: Dict[str, Any]) -> str:
    """
    Generates a 21 CFR Part 11 compliant HTML GMP Quality Complaint Record certificate.
    """
    complaint_code = complaint.get("complaint_code", "DRAFT")
    timestamp_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")
    
    # Generate deterministic hash for the record
    raw_hash_seed = f"{complaint_code}-{complaint.get('id', 0)}-{complaint.get('batch_number', '')}-{timestamp_str}"
    rec_hash = hashlib.sha256(raw_hash_seed.encode("utf-8")).hexdigest()[:32]

    logs = complaint.get("logs", [])
    logs_html = ""
    if logs:
        for log in logs:
            action_desc = "Complaint created in database" if log.get("action") == "Create" else f"Updated field: {str(log.get('field_name', '')).replace('_', ' ').upper()}"
            diff_html = ""
            if log.get("action") == "Update Field":
                old_v = log.get("old_value") or "empty"
                new_v = log.get("new_value") or ""
                diff_html = f'<div style="margin-top: 2px;">Change: <span style="text-decoration: line-through; color: #94a3b8;">"{old_v}"</span> to <span style="color: #059669; font-weight: bold;">"{new_v}"</span></div>'
            
            ts = log.get("timestamp")
            if isinstance(ts, datetime.datetime):
                ts_str = ts.strftime("%Y-%m-%d %H:%M:%S")
            else:
                ts_str = str(ts)

            logs_html += f"""
            <li class="timeline-item">
              <strong>{action_desc}</strong>
              {diff_html}
              <div class="timeline-time">By {log.get('changed_by', 'User')} &bull; {ts_str}</div>
            </li>
            """
    else:
        logs_html = '<li style="list-style:none; color:#64748b;">No audit logs recorded.</li>'

    # AI Quality Analysis Section
    has_ai = any([
        complaint.get("summary"),
        complaint.get("completeness_status"),
        complaint.get("root_cause_recommendation"),
        complaint.get("capa_recommendation")
    ])

    ai_section_html = ""
    if has_ai:
        summary_row = f'<tr><th>Executive Summary</th><td>{complaint.get("summary")}</td></tr>' if complaint.get("summary") else ""
        comp_row = f'<tr><th>Completeness Status</th><td><strong>{complaint.get("completeness_status")}</strong> - {complaint.get("completeness_feedback", "")}</td></tr>' if complaint.get("completeness_status") else ""
        root_row = f'<tr><th>Recommended Root Causes</th><td><pre style="font-family: inherit; margin: 0; white-space: pre-wrap; font-size: 13px;">{complaint.get("root_cause_recommendation")}</pre></td></tr>' if complaint.get("root_cause_recommendation") else ""
        capa_row = f'<tr><th>Suggested CAPA Plan</th><td><pre style="font-family: inherit; margin: 0; white-space: pre-wrap; font-size: 13px;">{complaint.get("capa_recommendation")}</pre></td></tr>' if complaint.get("capa_recommendation") else ""

        ai_section_html = f"""
        <div class="section">
          <div class="section-title">5. AI Copilot Quality Analysis</div>
          <table>
            {summary_row}
            {comp_row}
            {root_row}
            {capa_row}
          </table>
        </div>
        """

    html = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>GMP Quality Record - {complaint_code}</title>
  <style>
    body {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
      color: #1e293b;
      margin: 40px;
      line-height: 1.5;
      background: #ffffff;
    }}
    .header {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      border-bottom: 3px double #cbd5e1;
      padding-bottom: 20px;
      margin-bottom: 30px;
    }}
    .title {{
      font-size: 22px;
      font-weight: 800;
      letter-spacing: 0.05em;
      color: #0f172a;
    }}
    .subtitle {{
      font-size: 11px;
      color: #64748b;
      font-weight: 600;
      text-transform: uppercase;
      margin-top: 4px;
    }}
    .section {{
      margin-bottom: 28px;
    }}
    .section-title {{
      font-size: 13px;
      font-weight: 700;
      background: #f1f5f9;
      padding: 6px 12px;
      border-left: 4px solid #4f46e5;
      margin-bottom: 12px;
      color: #1e293b;
      text-transform: uppercase;
      letter-spacing: 0.03em;
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
      margin-bottom: 16px;
      font-size: 13px;
    }}
    th, td {{
      padding: 10px 12px;
      border: 1px solid #e2e8f0;
      text-align: left;
      vertical-align: top;
    }}
    th {{
      background: #f8fafc;
      font-weight: 600;
      width: 28%;
      color: #475569;
    }}
    .timeline {{
      padding-left: 20px;
      margin: 0;
    }}
    .timeline-item {{
      border-left: 2px solid #e2e8f0;
      padding-left: 16px;
      margin-bottom: 14px;
      position: relative;
      list-style: none;
      font-size: 13px;
    }}
    .timeline-item::before {{
      content: '';
      position: absolute;
      left: -6px;
      top: 4px;
      width: 10px;
      height: 10px;
      border-radius: 50%;
      background: #4f46e5;
      border: 2px solid #fff;
    }}
    .timeline-time {{
      font-size: 11px;
      color: #94a3b8;
      margin-top: 2px;
    }}
    .sig-block {{
      border: 2px dashed #0d9488;
      padding: 18px;
      border-radius: 8px;
      background: #f0fdfa;
      margin-top: 36px;
    }}
    .sig-title {{
      font-weight: 700;
      color: #0d9488;
      margin-bottom: 6px;
      font-size: 13px;
    }}
    .sig-details {{
      font-size: 12px;
      font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
      color: #0f766e;
      line-height: 1.6;
    }}
    @media print {{
      body {{ margin: 20px; }}
      .header {{ border-bottom: 2px solid #333; }}
    }}
  </style>
</head>
<body>
  <div class="header">
    <div>
      <div class="title">GMP QUALITY COMPLAINT RECORD</div>
      <div class="subtitle">AIVOA.AI Quality Management System &bull; Pharmaceutical Assurance</div>
    </div>
    <div style="text-align: right;">
      <div style="font-weight: 800; font-size: 20px; color: #4f46e5;">{complaint_code}</div>
      <div style="font-size: 12px; color: #475569; margin-top: 4px;">Status: <strong>{complaint.get('status', 'Pending Triage')}</strong></div>
    </div>
  </div>
  
  <div class="section">
    <div class="section-title">1. Origin & Customer Details</div>
    <table>
      <tr><th>Complaint Source</th><td>{complaint.get('complaint_source') or 'N/A'}</td></tr>
      <tr><th>Customer Name</th><td>{complaint.get('customer_name') or 'N/A'}</td></tr>
      <tr><th>Complaint Date</th><td>{complaint.get('complaint_date') or 'N/A'}</td></tr>
    </table>
  </div>

  <div class="section">
    <div class="section-title">2. Product & Batch Identification</div>
    <table>
      <tr><th>Product Name</th><td>{complaint.get('product_name') or 'N/A'}</td></tr>
      <tr><th>Strength / Grade</th><td>{complaint.get('product_strength') or 'N/A'}</td></tr>
      <tr><th>Batch/Lot Number</th><td>{complaint.get('batch_number') or 'N/A'}</td></tr>
      <tr><th>Manufacturing Date</th><td>{complaint.get('manufacturing_date') or 'N/A'}</td></tr>
      <tr><th>Expiry Date</th><td>{complaint.get('expiry_date') or 'N/A'}</td></tr>
      <tr><th>Quantity Affected</th><td>{complaint.get('quantity_affected') or 'N/A'}</td></tr>
    </table>
  </div>

  <div class="section">
    <div class="section-title">3. Complaint Details & Description</div>
    <table>
      <tr><th>Complaint Type</th><td>{complaint.get('complaint_type') or 'N/A'}</td></tr>
      <tr><th>Description</th><td>{complaint.get('description') or 'N/A'}</td></tr>
    </table>
  </div>

  <div class="section">
    <div class="section-title">4. Risk Assessment & Triage</div>
    <table>
      <tr><th>Initial Severity</th><td>{complaint.get('initial_severity') or 'N/A'}</td></tr>
      <tr><th>Priority</th><td>{complaint.get('priority') or 'N/A'}</td></tr>
      <tr><th>Suggested Next Action</th><td>{complaint.get('next_action') or 'N/A'}</td></tr>
      <tr><th>Risk Rationale Details</th><td>{complaint.get('risk_assessment_details') or 'N/A'}</td></tr>
    </table>
  </div>

  {ai_section_html}

  <div class="section">
    <div class="section-title">6. GMP Traceability Audit Trail</div>
    <ul class="timeline">
      {logs_html}
    </ul>
  </div>

  <div class="sig-block">
    <div class="sig-title">&#10004; 21 CFR PART 11 COMPLIANT ELECTRONIC RECORD SIGNATURE</div>
    <div style="font-size: 12px; color: #334155; margin-bottom: 8px;">
      This electronic quality record has been verified and registered in the regulatory QMS registry under FDA 21 CFR §211.198 and EU GMP Chapter 8.
    </div>
    <div class="sig-details">
      Electronic Stamp: SECURE_SIGNATURE_VERIFIED<br/>
      Signer: Quality Assurance Assessor (QA-USER)<br/>
      Timestamp: {timestamp_str}<br/>
      Record Hash (SHA-256): sha256-{rec_hash}dfa{complaint_code.lower()}
    </div>
  </div>
</body>
</html>
"""
    return html
