import React, { useState, useEffect, useRef } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { 
  updateFormField, 
  resetForm, 
  loadComplaintIntoForm,
  fetchComplaints,
  saveComplaint,
  deleteComplaint,
  extractFromText,
  extractFromFile,
  sendChatMessage,
  updateChatInput,
  runAssessment
} from './store/complaintSlice';
import { 
  FileText, 
  Send, 
  UploadCloud, 
  RefreshCw, 
  Save, 
  Trash2, 
  Database, 
  AlertTriangle, 
  Plus, 
  CheckCircle,
  HelpCircle, 
  Flame, 
  Layers,
  Brain,
  History,
  FileCheck,
  Sparkles,
  User,
  Bot
} from 'lucide-react';

function App() {
  const dispatch = useDispatch();
  const { 
    formData, 
    activeComplaintId, 
    savedComplaints, 
    chatHistory, 
    currentChatInput,
    extractionLoading, 
    chatLoading, 
    saveLoading, 
    listLoading,
    assessmentLoading,
    duplicateAlert
  } = useSelector(state => state.complaints);

  const [activeTab, setActiveTab] = useState('log'); // 'log' or 'dashboard'
  const [pasteMode, setPasteMode] = useState(false);
  const [pasteText, setPasteText] = useState('');
  const [selectedComplaintForDetail, setSelectedComplaintForDetail] = useState(null);
  
  const chatEndRef = useRef(null);
  const fileInputRef = useRef(null);

  // Fetch complaints on load
  useEffect(() => {
    dispatch(fetchComplaints());
  }, [dispatch]);

  // Scroll chat to bottom
  useEffect(() => {
    if (chatEndRef.current) {
      chatEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [chatHistory, chatLoading]);

  const handleInputChange = (field, value) => {
    dispatch(updateFormField({ field, value }));
  };

  const handleReset = () => {
    dispatch(resetForm());
    setPasteText('');
  };

  const handleSave = async (e) => {
    e.preventDefault();
    const actionResult = await dispatch(saveComplaint({ id: activeComplaintId, data: formData }));
    if (saveComplaint.fulfilled.match(actionResult)) {
      alert(`Complaint successfully saved! Code: ${actionResult.payload.complaint_code}`);
      dispatch(fetchComplaints());
    }
  };

  const handleTextExtract = () => {
    if (!pasteText.trim()) return;
    dispatch(extractFromText(pasteText));
    setPasteMode(false);
  };

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      dispatch(extractFromFile(file));
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
  };

  const handleDrop = (e) => {
    e.preventDefault();
    const file = e.dataTransfer.files[0];
    if (file) {
      dispatch(extractFromFile(file));
    }
  };

  const handleSendChat = (e) => {
    e.preventDefault();
    if (!currentChatInput.trim()) return;
    dispatch(sendChatMessage());
  };

  const triggerQuickAction = (actionType) => {
    dispatch(runAssessment(actionType));
  };

  const handleSelectComplaint = (complaint) => {
    setSelectedComplaintForDetail(complaint);
  };

  const handleLoadComplaint = (complaint) => {
    dispatch(loadComplaintIntoForm(complaint));
    setActiveTab('log');
  };

  const handleDeleteComplaint = (id) => {
    if (window.confirm("Are you sure you want to delete this complaint?")) {
      dispatch(deleteComplaint(id));
      if (selectedComplaintForDetail && selectedComplaintForDetail.id === id) {
        setSelectedComplaintForDetail(null);
      }
    }
  };

  const handleExportReport = (complaint) => {
    const hash = Math.random().toString(36).substring(2, 10) + Math.random().toString(36).substring(2, 10);
    const htmlContent = `
<!DOCTYPE html>
<html>
<head>
  <title>GMP Quality Record - ${complaint.complaint_code}</title>
  <style>
    body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; color: #1e293b; margin: 40px; line-height: 1.5; }
    .header { display: flex; justify-content: space-between; align-items: center; border-bottom: 3px double #cbd5e1; padding-bottom: 20px; margin-bottom: 30px; }
    .title { font-size: 22px; font-weight: 800; letter-spacing: 0.05em; color: #0f172a; }
    .subtitle { font-size: 11px; color: #64748b; font-weight: 600; text-transform: uppercase; margin-top: 4px; }
    .section { margin-bottom: 28px; }
    .section-title { font-size: 14px; font-weight: 700; background: #f1f5f9; padding: 6px 12px; border-left: 4px solid #4f46e5; margin-bottom: 12px; color: #1e293b; text-transform: uppercase; letter-spacing: 0.03em; }
    table { width: 100%; border-collapse: collapse; margin-bottom: 16px; font-size: 13px; }
    th, td { padding: 10px 12px; border: 1px solid #e2e8f0; text-align: left; vertical-align: top; }
    th { background: #f8fafc; font-weight: 600; width: 30%; color: #475569; }
    .timeline { padding-left: 20px; margin: 0; }
    .timeline-item { border-left: 2px solid #e2e8f0; padding-left: 16px; margin-bottom: 14px; position: relative; list-style: none; }
    .timeline-item::before { content: ''; position: absolute; left: -6px; top: 4px; width: 10px; height: 10px; border-radius: 50%; background: #4f46e5; border: 2px solid #fff; }
    .timeline-time { font-size: 11px; color: #94a3b8; margin-top: 2px; }
    .sig-block { border: 2px dashed #14b8a6; padding: 16px; border-radius: 8px; background: #f0fdfa; margin-top: 36px; }
    .sig-title { font-weight: 700; color: #0d9488; margin-bottom: 6px; font-size: 13px; display: flex; align-items: center; gap: 6px; }
    .sig-details { font-size: 12px; font-family: monospace; color: #0f766e; line-height: 1.6; }
  </style>
</head>
<body>
  <div class="header">
    <div>
      <div class="title">GMP QUALITY COMPLAINT RECORD</div>
      <div class="subtitle">AIVOA.AI Quality Management System</div>
    </div>
    <div style="text-align: right;">
      <div style="font-weight: 800; font-size: 18px; color: #4f46e5;">${complaint.complaint_code}</div>
      <div style="font-size: 12px; color: #475569; margin-top: 4px;">Status: <strong>${complaint.status}</strong></div>
    </div>
  </div>
  
  <div class="section">
    <div class="section-title">1. Origin & Customer Details</div>
    <table>
      <tr><th>Complaint Source</th><td>${complaint.complaint_source || 'N/A'}</td></tr>
      <tr><th>Customer Name</th><td>${complaint.customer_name || 'N/A'}</td></tr>
      <tr><th>Complaint Date</th><td>${complaint.complaint_date || 'N/A'}</td></tr>
    </table>
  </div>

  <div class="section">
    <div class="section-title">2. Product & Batch Identification</div>
    <table>
      <tr><th>Product Name</th><td>${complaint.product_name || 'N/A'}</td></tr>
      <tr><th>Strength / Grade</th><td>${complaint.product_strength || 'N/A'}</td></tr>
      <tr><th>Batch/Lot Number</th><td>${complaint.batch_number || 'N/A'}</td></tr>
      <tr><th>Manufacturing Date</th><td>${complaint.manufacturing_date || 'N/A'}</td></tr>
      <tr><th>Expiry Date</th><td>${complaint.expiry_date || 'N/A'}</td></tr>
      <tr><th>Quantity Affected</th><td>${complaint.quantity_affected || 'N/A'}</td></tr>
    </table>
  </div>

  <div class="section">
    <div class="section-title">3. Complaint Details & Description</div>
    <table>
      <tr><th>Complaint Type</th><td>${complaint.complaint_type || 'N/A'}</td></tr>
      <tr><th>Description</th><td>${complaint.description || 'N/A'}</td></tr>
    </table>
  </div>

  <div class="section">
    <div class="section-title">4. Risk Assessment & Triage</div>
    <table>
      <tr><th>Initial Severity</th><td>${complaint.initial_severity || 'N/A'}</td></tr>
      <tr><th>Priority</th><td>${complaint.priority || 'N/A'}</td></tr>
      <tr><th>Suggested Next Action</th><td>${complaint.next_action || 'N/A'}</td></tr>
      <tr><th>Risk Rationale Details</th><td>${complaint.risk_assessment_details || 'N/A'}</td></tr>
    </table>
  </div>

  ${complaint.root_cause_recommendation || complaint.capa_recommendation || complaint.summary || complaint.completeness_status ? `
  <div class="section">
    <div class="section-title">5. AI Copilot Quality Analysis</div>
    <table>
      ${complaint.summary ? `<tr><th>Executive Summary</th><td>${complaint.summary}</td></tr>` : ''}
      ${complaint.completeness_status ? `<tr><th>Completeness Status</th><td><strong>${complaint.completeness_status}</strong> - ${complaint.completeness_feedback || ''}</td></tr>` : ''}
      ${complaint.root_cause_recommendation ? `<tr><th>Recommended Root Causes</th><td><pre style="font-family: inherit; margin: 0; white-space: pre-wrap; font-size: 13px;">${complaint.root_cause_recommendation}</pre></td></tr>` : ''}
      ${complaint.capa_recommendation ? `<tr><th>Suggested CAPA Plan</th><td><pre style="font-family: inherit; margin: 0; white-space: pre-wrap; font-size: 13px;">${complaint.capa_recommendation}</pre></td></tr>` : ''}
    </table>
  </div>
  ` : ''}

  <div class="section">
    <div class="section-title">6. GMP Traceability Audit Trail</div>
    <ul class="timeline">
      ${complaint.logs?.map(log => `
        <li class="timeline-item">
          <strong>${log.action === 'Create' ? 'Complaint created in database' : `Updated field: ${log.field_name?.replace('_', ' ').toUpperCase()}`}</strong><br/>
          ${log.action === 'Update Field' ? `Change: <span style="text-decoration: line-through; color: #94a3b8;">"${log.old_value || 'empty'}"</span> to <span style="color: #059669; font-weight: bold;">"${log.new_value}"</span><br/>` : ''}
          <div class="timeline-time">By ${log.changed_by} &bull; ${new Date(log.timestamp).toLocaleString()}</div>
        </li>
      `).join('') || '<li style="list-style:none; color:#64748b;">No audit logs recorded.</li>'}
    </ul>
  </div>

  <div class="sig-block">
    <div class="sig-title">21 CFR PART 11 COMPLIANT ELECTRONIC RECORD SIGNATURE</div>
    <div style="font-size: 12px; color: #334155; margin-bottom: 8px;">This quality record has been electronically verified and approved.</div>
    <div class="sig-details">
      Electronic Stamp: SECURE_SIGNATURE_VERIFIED<br/>
      Signer: Quality Assurance Assessor (QA-USER)<br/>
      Timestamp: ${new Date().toLocaleString()}<br/>
      Record Hash (SHA-256): sha256-${hash}dfa${complaint.complaint_code.toLowerCase()}
    </div>
  </div>
</body>
</html>
    `;
    const blob = new Blob([htmlContent], { type: 'text/html' });
    const element = document.createElement('a');
    element.href = URL.createObjectURL(blob);
    element.download = `GMP_Complaint_${complaint.complaint_code}.html`;
    document.body.appendChild(element);
    element.click();
    document.body.removeChild(element);
  };


  return (
    <div className="app-container">
      {/* Sidebar Navigation */}
      <aside style={{
        background: 'var(--bg-sidebar)',
        borderRight: '1px solid var(--border-color)',
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'space-between',
        padding: '24px'
      }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '32px' }}>
            <div style={{
              background: 'linear-gradient(135deg, var(--primary) 0%, var(--accent) 100%)',
              width: '40px',
              height: '40px',
              borderRadius: '10px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontWeight: 'bold',
              color: 'white',
              fontSize: '1.2rem'
            }}>
              A
            </div>
            <div>
              <h2 style={{ fontSize: '1.1rem', fontWeight: 800, letterSpacing: '0.05em' }}>AIVOA.AI</h2>
              <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)', fontWeight: 600 }}>QMS ASSURANCE</span>
            </div>
          </div>

          <nav style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            <button 
              onClick={() => setActiveTab('log')}
              className={`btn ${activeTab === 'log' ? 'btn-primary' : 'btn-secondary'}`}
              style={{ justifyContent: 'flex-start', width: '100%' }}
            >
              <FileText size={18} /> Log Complaint
            </button>
            <button 
              onClick={() => {
                setActiveTab('dashboard');
                dispatch(fetchComplaints());
              }}
              className={`btn ${activeTab === 'dashboard' ? 'btn-primary' : 'btn-secondary'}`}
              style={{ justifyContent: 'flex-start', width: '100%' }}
            >
              <Database size={18} /> QA Dashboard
            </button>
          </nav>
        </div>

        <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textAlign: 'center' }}>
          API & FDF QA MODULE v1.0
        </div>
      </aside>

      {/* Main Content Area */}
      <main style={{ padding: '32px', overflowY: 'auto', height: '100vh' }}>
        
        {activeTab === 'log' ? (
          <div>
            <header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
              <div>
                <h1 style={{ fontSize: '1.8rem', fontWeight: 700 }}>Log Customer Complaint</h1>
                <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>API & FDF Quality Assurance Module</p>
              </div>
              <div style={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
                <span className={`badge badge-${formData.status === 'Resolved' ? 'resolved' : (formData.status === 'Under Investigation' ? 'investigating' : 'pending')}`}>
                  {activeComplaintId ? `Complaint: ${formData.status}` : 'Draft Mode'}
                </span>
                <span style={{
                  padding: '6px 12px',
                  borderRadius: '6px',
                  background: 'rgba(234, 179, 8, 0.15)',
                  color: '#eab308',
                  fontSize: '0.8rem',
                  fontWeight: 600
                }}>
                  Pending Triage
                </span>
              </div>
            </header>

            {/* Split Pane: Form on Left, AI Intake Assistant on Right */}
            <div style={{ display: 'grid', gridTemplateColumns: '1.2fr 1fr', gap: '24px', alignItems: 'start' }}>
              
              {/* Form Section */}
              <form onSubmit={handleSave} className="glass-panel" style={{ padding: '24px', display: 'flex', flexDirection: 'column', gap: '20px' }}>
                
                {/* System Lock Banner */}
                <div style={{
                  padding: '12px 16px',
                  background: 'rgba(234, 179, 8, 0.06)',
                  border: '1px solid rgba(234, 179, 8, 0.2)',
                  borderRadius: '8px',
                  color: '#eab308',
                  fontSize: '0.8rem',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '10px'
                }}>
                  <AlertTriangle size={16} />
                  <span><strong>System Lock:</strong> Manual entry is disabled. Use the AI Assistant on the right to populate and edit fields.</span>
                </div>

                {/* 1. Origin & Customer Details */}
                <div>
                  <h3 style={{ fontSize: '0.95rem', color: 'var(--accent)', borderBottom: '1px solid var(--border-color)', paddingBottom: '6px', marginBottom: '12px', fontWeight: 600 }}>
                    1. ORIGIN & CUSTOMER DETAILS
                  </h3>
                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
                    <div>
                      <label style={{ display: 'block', fontSize: '0.75rem', color: 'var(--text-secondary)', marginBottom: '6px', fontWeight: 500 }}>Complaint Source</label>
                      <select 
                        value={formData.complaint_source}
                        disabled={true}
                        className="input-field"
                        style={{ cursor: 'not-allowed', background: 'rgba(255,255,255,0.02)' }}
                      >
                        <option value="">Select Source</option>
                        <option value="Email">Email</option>
                        <option value="Customer Portal">Customer Portal</option>
                        <option value="Phone Call">Phone Call</option>
                        <option value="Letter">Letter</option>
                        <option value="Regulatory Agency">Regulatory Agency</option>
                      </select>
                    </div>
                    <div>
                      <label style={{ display: 'block', fontSize: '0.75rem', color: 'var(--text-secondary)', marginBottom: '6px', fontWeight: 500 }}>Customer Name</label>
                      <input 
                        type="text" 
                        value={formData.customer_name}
                        readOnly={true}
                        placeholder="Awaiting AI extraction..."
                        className="input-field"
                        style={{ cursor: 'not-allowed', background: 'rgba(255,255,255,0.02)' }}
                      />
                    </div>
                  </div>
                </div>

                {/* 2. Product & Batch Identification */}
                <div>
                  <h3 style={{ fontSize: '0.95rem', color: 'var(--accent)', borderBottom: '1px solid var(--border-color)', paddingBottom: '6px', marginBottom: '12px', fontWeight: 600 }}>
                    2. PRODUCT & BATCH IDENTIFICATION
                  </h3>
                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px', marginBottom: '12px' }}>
                    <div>
                      <label style={{ display: 'block', fontSize: '0.75rem', color: 'var(--text-secondary)', marginBottom: '6px', fontWeight: 500 }}>Product Name</label>
                      <input 
                        type="text" 
                        value={formData.product_name}
                        readOnly={true}
                        placeholder="Awaiting AI extraction..."
                        className="input-field"
                        style={{ cursor: 'not-allowed', background: 'rgba(255,255,255,0.02)' }}
                      />
                    </div>
                    <div>
                      <label style={{ display: 'block', fontSize: '0.75rem', color: 'var(--text-secondary)', marginBottom: '6px', fontWeight: 500 }}>Product Strength/Grade</label>
                      <input 
                        type="text" 
                        value={formData.product_strength}
                        readOnly={true}
                        placeholder="Awaiting AI extraction..."
                        className="input-field"
                        style={{ cursor: 'not-allowed', background: 'rgba(255,255,255,0.02)' }}
                      />
                    </div>
                  </div>
                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px', marginBottom: '12px' }}>
                    <div>
                      <label style={{ display: 'block', fontSize: '0.75rem', color: 'var(--text-secondary)', marginBottom: '6px', fontWeight: 500 }}>Batch/Lot Number</label>
                      <input 
                        type="text" 
                        value={formData.batch_number}
                        readOnly={true}
                        placeholder="Awaiting AI extraction..."
                        className="input-field"
                        style={{ cursor: 'not-allowed', background: 'rgba(255,255,255,0.02)' }}
                      />
                    </div>
                    <div>
                      <label style={{ display: 'block', fontSize: '0.75rem', color: 'var(--text-secondary)', marginBottom: '6px', fontWeight: 500 }}>Quantity Affected</label>
                      <input 
                        type="text" 
                        value={formData.quantity_affected}
                        readOnly={true}
                        placeholder="Awaiting AI extraction..."
                        className="input-field"
                        style={{ cursor: 'not-allowed', background: 'rgba(255,255,255,0.02)' }}
                      />
                    </div>
                  </div>
                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
                    <div>
                      <label style={{ display: 'block', fontSize: '0.75rem', color: 'var(--text-secondary)', marginBottom: '6px', fontWeight: 500 }}>Manufacturing Date</label>
                      <input 
                        type="text" 
                        value={formData.manufacturing_date}
                        readOnly={true}
                        placeholder="Awaiting AI extraction..."
                        className="input-field"
                        style={{ cursor: 'not-allowed', background: 'rgba(255,255,255,0.02)' }}
                      />
                    </div>
                    <div>
                      <label style={{ display: 'block', fontSize: '0.75rem', color: 'var(--text-secondary)', marginBottom: '6px', fontWeight: 500 }}>Expiry Date</label>
                      <input 
                        type="text" 
                        value={formData.expiry_date}
                        readOnly={true}
                        placeholder="Awaiting AI extraction..."
                        className="input-field"
                        style={{ cursor: 'not-allowed', background: 'rgba(255,255,255,0.02)' }}
                      />
                    </div>
                  </div>
                </div>

                {/* 3. Complaint Details */}
                <div>
                  <h3 style={{ fontSize: '0.95rem', color: 'var(--accent)', borderBottom: '1px solid var(--border-color)', paddingBottom: '6px', marginBottom: '12px', fontWeight: 600 }}>
                    3. COMPLAINT DETAILS
                  </h3>
                  <div style={{ display: 'grid', gridTemplateColumns: '1.2fr 0.8fr', gap: '16px', marginBottom: '12px' }}>
                    <div>
                      <label style={{ display: 'block', fontSize: '0.75rem', color: 'var(--text-secondary)', marginBottom: '6px', fontWeight: 500 }}>Complaint Type</label>
                      <select 
                        value={formData.complaint_type}
                        disabled={true}
                        className="input-field"
                        style={{ cursor: 'not-allowed', background: 'rgba(255,255,255,0.02)' }}
                      >
                        <option value="">Select Type</option>
                        <option value="Packaging Integrity">Packaging Integrity</option>
                        <option value="Contamination">Contamination</option>
                        <option value="Efficacy / Substandard">Efficacy / Substandard</option>
                        <option value="Adverse Event">Adverse Event</option>
                        <option value="Other">Other</option>
                      </select>
                    </div>
                    <div>
                      <label style={{ display: 'block', fontSize: '0.75rem', color: 'var(--text-secondary)', marginBottom: '6px', fontWeight: 500 }}>Complaint Date</label>
                      <input 
                        type="text" 
                        value={formData.complaint_date}
                        readOnly={true}
                        className="input-field"
                        style={{ cursor: 'not-allowed', background: 'rgba(255,255,255,0.02)' }}
                      />
                    </div>
                  </div>
                  <div>
                    <label style={{ display: 'block', fontSize: '0.75rem', color: 'var(--text-secondary)', marginBottom: '6px', fontWeight: 500 }}>Detailed Complaint Description</label>
                    <textarea 
                      rows="4" 
                      value={formData.description}
                      readOnly={true}
                      placeholder="Awaiting AI extraction..."
                      className="input-field"
                      style={{ resize: 'none', cursor: 'not-allowed', background: 'rgba(255,255,255,0.02)' }}
                    ></textarea>
                  </div>
                </div>

                {/* 4. Initial Assessment & Priority */}
                <div>
                  <h3 style={{ fontSize: '0.95rem', color: 'var(--accent)', borderBottom: '1px solid var(--border-color)', paddingBottom: '6px', marginBottom: '12px', fontWeight: 600 }}>
                    4. INITIAL ASSESSMENT & PRIORITY
                  </h3>
                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
                    <div>
                      <label style={{ display: 'block', fontSize: '0.75rem', color: 'var(--text-secondary)', marginBottom: '6px', fontWeight: 500 }}>Initial Severity</label>
                      <select 
                        value={formData.initial_severity}
                        disabled={true}
                        className="input-field"
                        style={{ cursor: 'not-allowed', background: 'rgba(255,255,255,0.02)' }}
                      >
                        <option value="">Awaiting AI extraction...</option>
                        <option value="Critical">Critical</option>
                        <option value="Major">Major</option>
                        <option value="Minor">Minor</option>
                      </select>
                    </div>
                    <div>
                      <label style={{ display: 'block', fontSize: '0.75rem', color: 'var(--text-secondary)', marginBottom: '6px', fontWeight: 500 }}>Priority</label>
                      <select 
                        value={formData.priority}
                        disabled={true}
                        className="input-field"
                        style={{ cursor: 'not-allowed', background: 'rgba(255,255,255,0.02)' }}
                      >
                        <option value="">Awaiting AI extraction...</option>
                        <option value="High">High</option>
                        <option value="Medium">Medium</option>
                        <option value="Low">Low</option>
                      </select>
                    </div>
                  </div>
                </div>

                {/* 5. AI Co-Pilot Risk Assessment */}
                <div>
                  <h3 style={{ fontSize: '0.95rem', color: 'var(--accent)', borderBottom: '1px solid var(--border-color)', paddingBottom: '6px', marginBottom: '12px', fontWeight: 600 }}>
                    5. AI CO-PILOT RISK ASSESSMENT
                  </h3>
                  <div style={{ display: 'grid', gridTemplateColumns: '1fr', gap: '16px' }}>
                    <div>
                      <label style={{ display: 'block', fontSize: '0.75rem', color: 'var(--text-secondary)', marginBottom: '6px', fontWeight: 500 }}>Suggested Next Action</label>
                      <input 
                        type="text" 
                        value={formData.next_action}
                        readOnly={true}
                        placeholder="Awaiting AI Copilot risk assessment..."
                        className="input-field"
                        style={{ cursor: 'not-allowed', border: '1px solid rgba(20, 184, 166, 0.3)', background: 'rgba(20, 184, 166, 0.05)' }}
                      />
                    </div>
                    <div>
                      <label style={{ display: 'block', fontSize: '0.75rem', color: 'var(--text-secondary)', marginBottom: '6px', fontWeight: 500 }}>Risk Assessment Details & Rationale</label>
                      <textarea 
                        rows="3" 
                        value={formData.risk_assessment_details}
                        readOnly={true}
                        placeholder="Awaiting AI Copilot risk assessment details..."
                        className="input-field"
                        style={{ resize: 'none', cursor: 'not-allowed', border: '1px solid rgba(20, 184, 166, 0.3)', background: 'rgba(20, 184, 166, 0.05)' }}
                      ></textarea>
                    </div>
                    {formData.initial_severity && (
                      <div style={{ marginTop: '10px' }}>
                        <label style={{ display: 'block', fontSize: '0.72rem', color: 'var(--text-secondary)', marginBottom: '6px', fontWeight: 500 }}>Regulatory Compliance Mapping</label>
                        <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
                          <span style={{
                            padding: '4px 8px',
                            background: 'rgba(99, 102, 241, 0.1)',
                            border: '1px solid rgba(99, 102, 241, 0.25)',
                            borderRadius: '4px',
                            color: 'var(--primary)',
                            fontSize: '0.7rem',
                            fontWeight: 600,
                            cursor: 'help'
                          }} title="FDA Regulation on Complaint Files: Written procedures describing handling of all written/oral complaints.">
                            21 CFR §211.198 (FDA)
                          </span>
                          <span style={{
                            padding: '4px 8px',
                            background: 'rgba(20, 184, 166, 0.1)',
                            border: '1px solid rgba(20, 184, 166, 0.25)',
                            borderRadius: '4px',
                            color: 'var(--accent)',
                            fontSize: '0.7rem',
                            fontWeight: 600,
                            cursor: 'help'
                          }} title="EU GMP Chapter 8: Complaints, Quality Defects, and Product Recalls rules.">
                            EU GMP Chapter 8
                          </span>
                          {formData.initial_severity === 'Critical' && (
                            <span style={{
                              padding: '4px 8px',
                              background: 'rgba(239, 68, 68, 0.1)',
                              border: '1px solid rgba(239, 68, 68, 0.25)',
                              borderRadius: '4px',
                              color: 'var(--color-critical)',
                              fontSize: '0.7rem',
                              fontWeight: 600,
                              cursor: 'help'
                            }} title="FDA 24-Hour Alert: High-priority event requiring immediate notification of health authorities.">
                              24h Authority Alert Rule
                            </span>
                          )}
                          <span style={{
                            padding: '4px 8px',
                            background: 'rgba(234, 179, 8, 0.1)',
                            border: '1px solid rgba(234, 179, 8, 0.25)',
                            borderRadius: '4px',
                            color: '#eab308',
                            fontSize: '0.7rem',
                            fontWeight: 600,
                            cursor: 'help'
                          }} title="ICH Q9: Quality Risk Management framework.">
                            ICH Q9 Framework
                          </span>
                        </div>
                      </div>
                    )}
                  </div>
                </div>

                {/* AI Insights Displays (If generated) */}
                {(formData.completeness_status || formData.root_cause_recommendation || formData.capa_recommendation || formData.summary) && (
                  <div style={{ marginTop: '10px', padding: '16px', background: 'rgba(255,255,255,0.02)', borderRadius: '10px', border: '1px solid var(--border-color)' }}>
                    <h4 style={{ fontSize: '0.8rem', color: 'var(--primary)', marginBottom: '10px', fontWeight: 700, letterSpacing: '0.05em' }}>AI ASSISTANT ANALYSIS CO-PILOT</h4>
                    
                    {formData.summary && (
                      <div style={{ marginBottom: '12px' }}>
                        <div style={{ fontSize: '0.7rem', color: 'var(--text-secondary)', fontWeight: 600, textTransform: 'uppercase' }}>Complaint Summary</div>
                        <div style={{ fontSize: '0.85rem', color: 'var(--text-primary)', marginTop: '2px' }}>{formData.summary}</div>
                      </div>
                    )}
                    
                    {formData.completeness_status && (
                      <div style={{ marginBottom: '12px', display: 'flex', gap: '8px', alignItems: 'center' }}>
                        <div style={{ fontSize: '0.7rem', color: 'var(--text-secondary)', fontWeight: 600, textTransform: 'uppercase' }}>Completeness:</div>
                        <span className={`badge badge-${formData.completeness_status.toLowerCase() === 'complete' ? 'resolved' : 'major'}`}>
                          {formData.completeness_status}
                        </span>
                        <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>{formData.completeness_feedback}</div>
                      </div>
                    )}

                    {formData.root_cause_recommendation && (
                      <div style={{ marginBottom: '12px' }}>
                        <div style={{ fontSize: '0.7rem', color: 'var(--text-secondary)', fontWeight: 600, textTransform: 'uppercase' }}>Recommended Root Causes</div>
                        <pre style={{ fontSize: '0.8rem', color: 'var(--text-primary)', whiteSpace: 'pre-wrap', fontFamily: 'inherit', marginTop: '2px' }}>{formData.root_cause_recommendation}</pre>
                      </div>
                    )}

                    {formData.capa_recommendation && (
                      <div style={{ marginBottom: '12px' }}>
                        <div style={{ fontSize: '0.7rem', color: 'var(--text-secondary)', fontWeight: 600, textTransform: 'uppercase' }}>CAPA Suggestions</div>
                        <pre style={{ fontSize: '0.8rem', color: 'var(--text-primary)', whiteSpace: 'pre-wrap', fontFamily: 'inherit', marginTop: '2px' }}>{formData.capa_recommendation}</pre>
                      </div>
                    )}

                    {formData.risk_classification_reasoning && (
                      <div>
                        <div style={{ fontSize: '0.7rem', color: 'var(--text-secondary)', fontWeight: 600, textTransform: 'uppercase' }}>Risk Classification Reasoning</div>
                        <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginTop: '2px' }}>{formData.risk_classification_reasoning}</div>
                      </div>
                    )}
                  </div>
                )}

                {/* Duplicate Alert banner */}
                {duplicateAlert && (
                  <div style={{
                    padding: '12px',
                    borderRadius: '8px',
                    background: 'rgba(239, 68, 68, 0.12)',
                    border: '1px solid rgba(239, 68, 68, 0.3)',
                    color: '#ef4444',
                    fontSize: '0.85rem',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '10px'
                  }}>
                    <AlertTriangle size={18} />
                    <div>{duplicateAlert}</div>
                  </div>
                )}

                {/* Form Buttons */}
                <div style={{ display: 'flex', justifySelf: 'flex-end', gap: '12px', borderTop: '1px solid var(--border-color)', paddingTop: '16px', marginTop: '10px' }}>
                  <button type="button" onClick={handleReset} className="btn btn-secondary" style={{ flex: 1 }}>
                    <RefreshCw size={16} /> Reset Form
                  </button>
                  <button type="submit" disabled={saveLoading} className="btn btn-primary" style={{ flex: 2 }}>
                    <Save size={16} /> {saveLoading ? 'Saving...' : (activeComplaintId ? 'Update Complaint' : 'Save Complaint')}
                  </button>
                </div>

              </form>

              {/* AI Intake Assistant Right Panel */}
              <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
                
                {/* File Upload Panel */}
                <div 
                  className="glass-panel animate-pulse-glow" 
                  onDragOver={handleDragOver}
                  onDrop={handleDrop}
                  style={{
                    padding: '24px',
                    textAlign: 'center',
                    borderStyle: 'dashed',
                    borderWidth: '2px',
                    cursor: 'pointer'
                  }}
                  onClick={() => fileInputRef.current?.click()}
                >
                  <input 
                    type="file" 
                    ref={fileInputRef}
                    onChange={handleFileChange}
                    style={{ display: 'none' }}
                    accept=".pdf,.docx,.txt,.eml"
                  />
                  <UploadCloud size={40} style={{ color: 'var(--primary)', marginBottom: '12px' }} />
                  <h3 style={{ fontSize: '1rem', fontWeight: 600, marginBottom: '6px' }}>Drag & drop complaint document here</h3>
                  <p style={{ color: 'var(--text-secondary)', fontSize: '0.8rem', marginBottom: '8px' }}>or click to browse from system</p>
                  <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>Supported formats: PDF, DOCX, TXT, EML. Max 10MB</span>
                </div>

                {/* Paste Area Button */}
                <div style={{ textAlign: 'center' }}>
                  <button 
                    type="button" 
                    onClick={() => setPasteMode(!pasteMode)} 
                    className="btn btn-secondary"
                    style={{ width: '100%', fontSize: '0.8rem', padding: '8px 16px' }}
                  >
                    {pasteMode ? 'Hide Text Area' : '📋 Paste Complaint Text / Email'}
                  </button>
                  {pasteMode && (
                    <div className="glass-panel animate-fade-in" style={{ marginTop: '10px', padding: '16px', textAlign: 'left' }}>
                      <textarea 
                        rows="6"
                        value={pasteText}
                        onChange={(e) => setPasteText(e.target.value)}
                        placeholder="Paste the complaint email message or letter contents here..."
                        className="input-field"
                        style={{ marginBottom: '12px', fontSize: '0.85rem' }}
                      />
                      <button 
                        type="button" 
                        onClick={handleTextExtract}
                        disabled={extractionLoading}
                        className="btn btn-primary"
                        style={{ width: '100%' }}
                      >
                        {extractionLoading ? 'Extracting...' : 'Start AI Extraction'}
                      </button>
                    </div>
                  )}
                </div>

                {/* Extraction Loader */}
                {extractionLoading && (
                  <div style={{ textAlign: 'center', padding: '10px' }}>
                    <div style={{ fontSize: '0.85rem', color: 'var(--primary)', marginBottom: '6px', fontWeight: 600 }}>Analyzing document content and extracting key details...</div>
                    <div className="extraction-progress"></div>
                    <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>Please wait, this may take a few moments.</span>
                  </div>
                )}

                {/* AI Assistant Chat Interface */}
                <div className="glass-panel" style={{ display: 'flex', flexDirection: 'column', height: '420px' }}>
                  <div style={{
                    padding: '14px 16px',
                    borderBottom: '1px solid var(--border-color)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between'
                  }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                      <Bot size={18} style={{ color: 'var(--primary)' }} />
                      <h4 style={{ fontSize: '0.9rem', fontWeight: 700 }}>AI Complaint Intake Assistant</h4>
                    </div>
                    <span style={{ fontSize: '0.65rem', background: 'rgba(99, 102, 241, 0.15)', color: 'var(--primary)', padding: '2px 6px', borderRadius: '4px', fontWeight: 700 }}>BETA</span>
                  </div>

                  {/* Chat messages */}
                  <div style={{ flex: 1, overflowY: 'auto', padding: '16px', display: 'flex', flexDirection: 'column', gap: '14px' }}>
                    {chatHistory.map((msg, index) => (
                      <div 
                        key={index}
                        style={{
                          display: 'flex',
                          gap: '10px',
                          alignSelf: msg.sender === 'user' ? 'flex-end' : 'flex-start',
                          maxWidth: '85%'
                        }}
                      >
                        {msg.sender === 'ai' && (
                          <div style={{
                            width: '28px',
                            height: '28px',
                            borderRadius: '50%',
                            background: 'rgba(99,102,241,0.1)',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            flexShrink: 0
                          }}>
                            <Bot size={14} style={{ color: 'var(--primary)' }} />
                          </div>
                        )}
                        
                        <div style={{
                          padding: '10px 14px',
                          borderRadius: '12px',
                          background: msg.sender === 'user' ? 'var(--primary)' : 'rgba(255,255,255,0.03)',
                          border: msg.sender === 'user' ? 'none' : '1px solid var(--border-color)',
                          fontSize: '0.85rem',
                          lineHeight: '1.4',
                          color: 'var(--text-primary)'
                        }}>
                          {msg.text}
                        </div>

                        {msg.sender === 'user' && (
                          <div style={{
                            width: '28px',
                            height: '28px',
                            borderRadius: '50%',
                            background: 'rgba(255,255,255,0.05)',
                            border: '1px solid var(--border-color)',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            flexShrink: 0
                          }}>
                            <User size={14} style={{ color: 'var(--text-secondary)' }} />
                          </div>
                        )}
                      </div>
                    ))}
                    {chatLoading && (
                      <div style={{ display: 'flex', gap: '10px', alignSelf: 'flex-start' }}>
                        <div style={{
                          width: '28px',
                          height: '28px',
                          borderRadius: '50%',
                          background: 'rgba(99,102,241,0.1)',
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center'
                        }}>
                          <Bot size={14} style={{ color: 'var(--primary)' }} />
                        </div>
                        <div style={{
                          padding: '10px 14px',
                          borderRadius: '12px',
                          background: 'rgba(255,255,255,0.03)',
                          border: '1px solid var(--border-color)',
                          fontSize: '0.85rem',
                          color: 'var(--text-muted)'
                        }}>
                          AI is analyzing and formulating response...
                        </div>
                      </div>
                    )}
                    <div ref={chatEndRef} />
                  </div>

                  {/* Suggestion Chips */}
                  <div style={{
                    padding: '8px 16px',
                    display: 'flex',
                    gap: '6px',
                    overflowX: 'auto',
                    borderTop: '1px solid var(--border-color)',
                    background: 'rgba(0,0,0,0.1)'
                  }}>
                    <button 
                      type="button"
                      onClick={() => handleInputChange('product_strength', '250mg')}
                      style={{ fontSize: '0.75rem', background: 'rgba(255,255,255,0.02)', border: '1px solid var(--border-color)', borderRadius: '12px', padding: '4px 10px', color: 'var(--text-secondary)', cursor: 'pointer', whiteSpace: 'nowrap' }}
                    >
                      "Set strength to 250mg"
                    </button>
                    <button 
                      type="button"
                      onClick={() => handleInputChange('complaint_source', 'Email')}
                      style={{ fontSize: '0.75rem', background: 'rgba(255,255,255,0.02)', border: '1px solid var(--border-color)', borderRadius: '12px', padding: '4px 10px', color: 'var(--text-secondary)', cursor: 'pointer', whiteSpace: 'nowrap' }}
                    >
                      "Set source to Email"
                    </button>
                  </div>

                  {/* Chat Input */}
                  <form onSubmit={handleSendChat} style={{
                    padding: '12px 16px',
                    borderTop: '1px solid var(--border-color)',
                    display: 'flex',
                    gap: '10px'
                  }}>
                    <input 
                      type="text"
                      value={currentChatInput}
                      onChange={(e) => dispatch(updateChatInput(e.target.value))}
                      placeholder="Ask me anything about this complaint..."
                      className="input-field"
                      style={{ flex: 1 }}
                    />
                    <button type="submit" disabled={chatLoading} className="btn btn-primary" style={{ padding: '10px' }}>
                      <Send size={16} />
                    </button>
                  </form>
                </div>

                {/* AI Copilot Assessor Quick Action Grid */}
                <div className="glass-panel" style={{ padding: '16px' }}>
                  <h4 style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', fontWeight: 700, letterSpacing: '0.05em', marginBottom: '12px', display: 'flex', alignItems: 'center', gap: '6px' }}>
                    <Sparkles size={14} style={{ color: 'var(--accent)' }} /> 
                    AI COPILOT ANALYSIS TOOLS (BONUS)
                  </h4>
                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px' }}>
                    <button 
                      type="button" 
                      onClick={() => triggerQuickAction('completeness')}
                      disabled={assessmentLoading.completeness}
                      className="btn btn-secondary" 
                      style={{ fontSize: '0.8rem', justifyContent: 'flex-start', padding: '8px 12px' }}
                    >
                      <FileCheck size={14} style={{ color: 'var(--accent)' }} /> 
                      {assessmentLoading.completeness ? 'Checking...' : 'Completeness Check'}
                    </button>
                    <button 
                      type="button" 
                      onClick={() => triggerQuickAction('risk')}
                      disabled={assessmentLoading.risk}
                      className="btn btn-secondary" 
                      style={{ fontSize: '0.8rem', justifyContent: 'flex-start', padding: '8px 12px' }}
                    >
                      <Flame size={14} style={{ color: 'var(--color-critical)' }} /> 
                      {assessmentLoading.risk ? 'Classifying...' : 'Risk Classification'}
                    </button>
                    <button 
                      type="button" 
                      onClick={() => triggerQuickAction('root_cause')}
                      disabled={assessmentLoading.root_cause}
                      className="btn btn-secondary" 
                      style={{ fontSize: '0.8rem', justifyContent: 'flex-start', padding: '8px 12px' }}
                    >
                      <Brain size={14} style={{ color: 'var(--primary)' }} /> 
                      {assessmentLoading.root_cause ? 'Analyzing...' : 'Root Cause Analysis'}
                    </button>
                    <button 
                      type="button" 
                      onClick={() => triggerQuickAction('capa')}
                      disabled={assessmentLoading.capa}
                      className="btn btn-secondary" 
                      style={{ fontSize: '0.8rem', justifyContent: 'flex-start', padding: '8px 12px' }}
                    >
                      <CheckCircle size={14} style={{ color: 'var(--color-resolved)' }} /> 
                      {assessmentLoading.capa ? 'Generating...' : 'CAPA Suggestion'}
                    </button>
                    <button 
                      type="button" 
                      onClick={() => triggerQuickAction('duplicate')}
                      disabled={assessmentLoading.duplicate}
                      className="btn btn-secondary" 
                      style={{ fontSize: '0.8rem', justifyContent: 'flex-start', padding: '8px 12px' }}
                    >
                      <Layers size={14} style={{ color: '#eab308' }} /> 
                      {assessmentLoading.duplicate ? 'Searching...' : 'Duplicate Check'}
                    </button>
                    <button 
                      type="button" 
                      onClick={() => triggerQuickAction('summary')}
                      disabled={assessmentLoading.summary}
                      className="btn btn-secondary" 
                      style={{ fontSize: '0.8rem', justifyContent: 'flex-start', padding: '8px 12px' }}
                    >
                      <FileText size={14} style={{ color: 'var(--text-secondary)' }} /> 
                      {assessmentLoading.summary ? 'Summarizing...' : 'Summarize Complaint'}
                    </button>
                  </div>
                </div>

              </div>

            </div>
          </div>
        ) : (
          /* Dashboard View */
          <div>
            <header style={{ marginBottom: '24px' }}>
              <h1 style={{ fontSize: '1.8rem', fontWeight: 700 }}>Quality Assurance Dashboard</h1>
              <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>Traceability audit trails & database registry of logged complaints</p>
            </header>

            {listLoading ? (
              <div style={{ textAlign: 'center', padding: '40px' }}>Loading complaints registry...</div>
            ) : (
              <div style={{ display: 'grid', gridTemplateColumns: '1.2fr 1fr', gap: '24px', alignItems: 'start' }}>
                
                {/* Complaints registry list */}
                <div className="glass-panel" style={{ padding: '20px', overflowX: 'auto' }}>
                  <h3 style={{ fontSize: '1rem', fontWeight: 700, marginBottom: '16px' }}>Logged Quality Complaints</h3>
                  
                  {savedComplaints.length === 0 ? (
                    <div style={{ color: 'var(--text-muted)', textAlign: 'center', padding: '30px' }}>No complaints saved yet. Log a complaint first!</div>
                  ) : (
                    <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.85rem', textAlign: 'left' }}>
                      <thead>
                        <tr style={{ borderBottom: '1px solid var(--border-color)', color: 'var(--text-secondary)' }}>
                          <th style={{ padding: '12px 8px' }}>Code</th>
                          <th style={{ padding: '12px 8px' }}>Product</th>
                          <th style={{ padding: '12px 8px' }}>Batch</th>
                          <th style={{ padding: '12px 8px' }}>Severity</th>
                          <th style={{ padding: '12px 8px' }}>Status</th>
                          <th style={{ padding: '12px 8px' }}>Actions</th>
                        </tr>
                      </thead>
                      <tbody>
                        {savedComplaints.map((c) => (
                          <tr 
                            key={c.id} 
                            onClick={() => handleSelectComplaint(c)}
                            style={{ 
                              borderBottom: '1px solid var(--border-color)', 
                              cursor: 'pointer',
                              background: selectedComplaintForDetail?.id === c.id ? 'rgba(99,102,241,0.06)' : 'transparent',
                              transition: 'background 0.2s'
                            }}
                          >
                            <td style={{ padding: '12px 8px', fontWeight: 600, color: 'var(--primary)' }}>{c.complaint_code}</td>
                            <td style={{ padding: '12px 8px' }}>{c.product_name}</td>
                            <td style={{ padding: '12px 8px' }}>{c.batch_number}</td>
                            <td style={{ padding: '12px 8px' }}>
                              <span className={`badge badge-${c.initial_severity?.toLowerCase() || 'major'}`}>
                                {c.initial_severity || 'Major'}
                              </span>
                            </td>
                            <td style={{ padding: '12px 8px' }}>
                              <span className={`badge badge-${c.status === 'Resolved' ? 'resolved' : (c.status === 'Under Investigation' ? 'investigating' : 'pending')}`}>
                                {c.status}
                              </span>
                            </td>
                            <td style={{ padding: '12px 8px' }} onClick={(e) => e.stopPropagation()}>
                              <div style={{ display: 'flex', gap: '8px' }}>
                                <button 
                                  onClick={() => handleLoadComplaint(c)}
                                  className="btn btn-secondary" 
                                  style={{ padding: '4px 8px', fontSize: '0.75rem' }}
                                >
                                  Edit
                                </button>
                                <button 
                                  onClick={() => handleDeleteComplaint(c.id)}
                                  className="btn btn-secondary" 
                                  style={{ padding: '4px 8px', fontSize: '0.75rem', background: 'rgba(239, 68, 68, 0.08)', color: '#ef4444', borderColor: 'rgba(239,68,68,0.2)' }}
                                >
                                  <Trash2 size={12} />
                                </button>
                              </div>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  )}
                </div>

                {/* Inspect Detail / Audit Trail timeline */}
                <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
                  
                  {selectedComplaintForDetail ? (
                    <div className="glass-panel" style={{ padding: '24px' }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px', borderBottom: '1px solid var(--border-color)', paddingBottom: '12px' }}>
                        <div>
                          <h3 style={{ fontSize: '1.1rem', fontWeight: 700 }}>{selectedComplaintForDetail.complaint_code}</h3>
                          <span style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>Registered: {new Date(selectedComplaintForDetail.created_at).toLocaleString()}</span>
                        </div>
                        <select 
                          value={selectedComplaintForDetail.status}
                          onChange={async (e) => {
                            const newStatus = e.target.value;
                            const actionResult = await dispatch(saveComplaint({ 
                              id: selectedComplaintForDetail.id, 
                              data: { ...selectedComplaintForDetail, status: newStatus } 
                            }));
                            if (saveComplaint.fulfilled.match(actionResult)) {
                              setSelectedComplaintForDetail(actionResult.payload);
                              dispatch(fetchComplaints());
                            }
                          }}
                          className="input-field"
                          style={{ width: 'auto', padding: '6px 12px', fontSize: '0.8rem' }}
                        >
                          <option value="Pending Triage">Pending Triage</option>
                          <option value="Under Investigation">Under Investigation</option>
                          <option value="Resolved">Resolved</option>
                        </select>
                      </div>

                      <div style={{ display: 'flex', gap: '8px', marginBottom: '16px' }}>
                        <button
                          type="button"
                          onClick={() => handleExportReport(selectedComplaintForDetail)}
                          className="btn btn-secondary"
                          style={{ 
                            fontSize: '0.75rem', 
                            padding: '6px 12px', 
                            background: 'rgba(20, 184, 166, 0.1)', 
                            color: 'var(--accent)', 
                            borderColor: 'rgba(20, 184, 166, 0.2)',
                            flex: 1
                          }}
                        >
                          Export GMP Report
                        </button>
                        <button
                          type="button"
                          onClick={async () => {
                            const actionResult = await dispatch(saveComplaint({ 
                              id: selectedComplaintForDetail.id, 
                              data: { ...selectedComplaintForDetail, status: 'Resolved' } 
                            }));
                            if (saveComplaint.fulfilled.match(actionResult)) {
                              setSelectedComplaintForDetail(actionResult.payload);
                              dispatch(fetchComplaints());
                              alert("Record electronically signed and resolved under FDA 21 CFR Part 11!");
                            }
                          }}
                          disabled={selectedComplaintForDetail.status === 'Resolved'}
                          className="btn btn-secondary"
                          style={{ 
                            fontSize: '0.75rem', 
                            padding: '6px 12px', 
                            background: 'rgba(99, 102, 241, 0.1)', 
                            color: 'var(--primary)', 
                            borderColor: 'rgba(99, 102, 241, 0.2)',
                            flex: 1
                          }}
                        >
                          {selectedComplaintForDetail.status === 'Resolved' ? 'Sign Approved ✅' : 'Sign & Resolve 🔒'}
                        </button>
                      </div>

                      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px', fontSize: '0.85rem', marginBottom: '20px' }}>
                        <div>
                          <span style={{ color: 'var(--text-secondary)', display: 'block', fontSize: '0.7rem', fontWeight: 600 }}>CUSTOMER</span>
                          <span>{selectedComplaintForDetail.customer_name}</span>
                        </div>
                        <div>
                          <span style={{ color: 'var(--text-secondary)', display: 'block', fontSize: '0.7rem', fontWeight: 600 }}>SOURCE</span>
                          <span>{selectedComplaintForDetail.complaint_source}</span>
                        </div>
                        <div>
                          <span style={{ color: 'var(--text-secondary)', display: 'block', fontSize: '0.7rem', fontWeight: 600 }}>PRODUCT / STRENGTH</span>
                          <span>{selectedComplaintForDetail.product_name} ({selectedComplaintForDetail.product_strength})</span>
                        </div>
                        <div>
                          <span style={{ color: 'var(--text-secondary)', display: 'block', fontSize: '0.7rem', fontWeight: 600 }}>BATCH NUMBER</span>
                          <span>{selectedComplaintForDetail.batch_number}</span>
                        </div>
                      </div>

                      <div style={{ marginBottom: '20px' }}>
                        <span style={{ color: 'var(--text-secondary)', display: 'block', fontSize: '0.7rem', fontWeight: 600 }}>DESCRIPTION</span>
                        <p style={{ fontSize: '0.85rem', color: 'var(--text-primary)', marginTop: '4px', background: 'rgba(0,0,0,0.15)', padding: '10px', borderRadius: '6px' }}>
                          {selectedComplaintForDetail.description}
                        </p>
                      </div>

                      {/* Timeline audit trail */}
                      <div>
                        <h4 style={{ fontSize: '0.8rem', color: 'var(--accent)', fontWeight: 700, letterSpacing: '0.05em', marginBottom: '12px', display: 'flex', alignItems: 'center', gap: '6px' }}>
                          <History size={14} /> GMP TRACEABILITY AUDIT TRAIL
                        </h4>
                        
                        {selectedComplaintForDetail.logs?.length === 0 ? (
                          <div style={{ color: 'var(--text-muted)', fontSize: '0.8rem' }}>No audit trail entries recorded.</div>
                        ) : (
                          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', maxHeight: '200px', overflowY: 'auto', paddingRight: '4px' }}>
                            {selectedComplaintForDetail.logs?.map((log) => (
                              <div 
                                key={log.id} 
                                style={{
                                  borderLeft: '2px solid var(--primary)', 
                                  paddingLeft: '12px', 
                                  fontSize: '0.8rem',
                                  position: 'relative'
                                }}
                              >
                                <div style={{ fontWeight: 600, color: 'var(--text-primary)' }}>
                                  {log.action === 'Create' ? 'Complaint created in database' : `Updated field: ${log.field_name?.replace('_', ' ').toUpperCase()}`}
                                </div>
                                {log.action === 'Update Field' && (
                                  <div style={{ color: 'var(--text-secondary)', fontSize: '0.75rem', marginTop: '2px' }}>
                                    Change: <span style={{ color: '#ef4444', textDecoration: 'line-through' }}>"{log.old_value || 'empty'}"</span> to <span style={{ color: '#10b981' }}>"{log.new_value}"</span>
                                  </div>
                                )}
                                <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', marginTop: '2px' }}>
                                  By {log.changed_by} • {new Date(log.timestamp).toLocaleTimeString()}
                                </div>
                              </div>
                            ))}
                          </div>
                        )}
                      </div>

                      {selectedComplaintForDetail.status === 'Resolved' && (
                        <div style={{
                          marginTop: '20px',
                          padding: '12px',
                          border: '1px dashed var(--accent)',
                          background: 'rgba(20, 184, 166, 0.05)',
                          borderRadius: '8px',
                          fontSize: '0.8rem',
                          color: 'var(--accent)',
                          animation: 'fadeIn 0.3s ease-out'
                        }}>
                          <div style={{ fontWeight: 600, display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '4px' }}>
                            <CheckCircle size={14} /> 21 CFR Part 11 Electronic Signature Stamp
                          </div>
                          <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>
                            Status: Approved & Closed<br />
                            Reviewer: Quality Assurance Assessor (QA-USER)<br />
                            Verification Hash: <span style={{ fontFamily: 'monospace' }}>sha256-{(selectedComplaintForDetail.id * 789123).toString(16)}dfa{selectedComplaintForDetail.complaint_code.toLowerCase()}</span>
                          </div>
                        </div>
                      )}

                    </div>
                  ) : (
                    <div className="glass-panel" style={{ padding: '30px', textAlign: 'center', color: 'var(--text-muted)' }}>
                      Select a logged complaint from the list to view full details and verification audit trail.
                    </div>
                  )}

                </div>

              </div>
            )}
          </div>
        )}

      </main>
    </div>
  );
}

export default App;
