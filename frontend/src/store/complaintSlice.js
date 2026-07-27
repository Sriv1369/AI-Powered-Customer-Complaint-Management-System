import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';

const API_BASE = 'http://localhost:8000/api';

const initialFormState = {
  complaint_source: '',
  customer_name: '',
  product_name: '',
  product_strength: '',
  batch_number: '',
  manufacturing_date: '',
  expiry_date: '',
  quantity_affected: '',
  complaint_type: '',
  complaint_date: new Date().toISOString().split('T')[0],
  description: '',
  initial_severity: '',
  priority: '',
  completeness_status: '',
  completeness_feedback: '',
  root_cause_recommendation: '',
  capa_recommendation: '',
  summary: '',
  risk_classification_reasoning: '',
  next_action: '',
  risk_assessment_details: ''
};

// Async Thunks
export const fetchComplaints = createAsyncThunk('complaints/fetchComplaints', async () => {
  const response = await fetch(`${API_BASE}/complaints`);
  if (!response.ok) throw new Error('Failed to fetch complaints');
  return await response.json();
});

export const saveComplaint = createAsyncThunk('complaints/saveComplaint', async ({ id, data }, { rejectWithValue }) => {
  try {
    const url = id ? `${API_BASE}/complaints/${id}` : `${API_BASE}/complaints`;
    const method = id ? 'PUT' : 'POST';
    const response = await fetch(url, {
      method,
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    if (!response.ok) throw new Error('Failed to save complaint');
    return await response.json();
  } catch (error) {
    return rejectWithValue(error.message);
  }
});

export const deleteComplaint = createAsyncThunk('complaints/deleteComplaint', async (id, { rejectWithValue }) => {
  try {
    const response = await fetch(`${API_BASE}/complaints/${id}`, { method: 'DELETE' });
    if (!response.ok) throw new Error('Failed to delete complaint');
    return id;
  } catch (error) {
    return rejectWithValue(error.message);
  }
});

export const extractFromText = createAsyncThunk('complaints/extractFromText', async (text, { rejectWithValue }) => {
  try {
    const response = await fetch(`${API_BASE}/agent/extract-text`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text })
    });
    if (!response.ok) throw new Error('Failed to extract data');
    return await response.json();
  } catch (error) {
    return rejectWithValue(error.message);
  }
});

export const extractFromFile = createAsyncThunk('complaints/extractFromFile', async (file, { rejectWithValue }) => {
  try {
    const formData = new FormData();
    formData.append('file', file);
    const response = await fetch(`${API_BASE}/agent/extract-file`, {
      method: 'POST',
      body: formData
    });
    if (!response.ok) throw new Error('Failed to extract file content');
    return await response.json();
  } catch (error) {
    return rejectWithValue(error.message);
  }
});

export const sendChatMessage = createAsyncThunk('complaints/sendChatMessage', async (_, { getState, rejectWithValue }) => {
  try {
    const state = getState().complaints;
    const history = state.chatHistory.map(msg => ({
      role: msg.sender === 'user' ? 'user' : 'assistant',
      content: msg.text
    }));
    const message = state.currentChatInput;
    const current_fields = state.formData;

    const response = await fetch(`${API_BASE}/agent/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message, chat_history: history, current_fields })
    });
    if (!response.ok) throw new Error('Failed to chat');
    return await response.json();
  } catch (error) {
    return rejectWithValue(error.message);
  }
});

export const runAssessment = createAsyncThunk('complaints/runAssessment', async (type, { getState, rejectWithValue }) => {
  try {
    const fields = getState().complaints.formData;
    const response = await fetch(`${API_BASE}/agent/assess`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ fields, assessment_type: type })
    });
    if (!response.ok) throw new Error('Assessment failed');
    const result = await response.json();
    return { type, result };
  } catch (error) {
    return rejectWithValue(error.message);
  }
});

const complaintSlice = createSlice({
  name: 'complaints',
  initialState: {
    formData: { ...initialFormState },
    activeComplaintId: null,
    savedComplaints: [],
    chatHistory: [
      { sender: 'ai', text: 'Hello! I am your AI Copilot Assistant. Drag & drop a complaint letter/PDF here, paste text, or chat with me to log the customer complaint.' }
    ],
    currentChatInput: '',
    extractionLoading: false,
    chatLoading: false,
    saveLoading: false,
    listLoading: false,
    assessmentLoading: {
      completeness: false,
      root_cause: false,
      capa: false,
      risk: false,
      duplicate: false,
      summary: false
    },
    duplicateAlert: null
  },
  reducers: {
    updateFormField: (state, action) => {
      const { field, value } = action.payload;
      state.formData[field] = value;
    },
    updateChatInput: (state, action) => {
      state.currentChatInput = action.payload;
    },
    resetForm: (state) => {
      state.formData = { ...initialFormState };
      state.activeComplaintId = null;
      state.duplicateAlert = null;
    },
    loadComplaintIntoForm: (state, action) => {
      const complaint = action.payload;
      state.formData = {
        complaint_source: complaint.complaint_source || '',
        customer_name: complaint.customer_name || '',
        product_name: complaint.product_name || '',
        product_strength: complaint.product_strength || '',
        batch_number: complaint.batch_number || '',
        manufacturing_date: complaint.manufacturing_date || '',
        expiry_date: complaint.expiry_date || '',
        quantity_affected: complaint.quantity_affected || '',
        complaint_type: complaint.complaint_type || '',
        complaint_date: complaint.complaint_date || '',
        description: complaint.description || '',
        initial_severity: complaint.initial_severity || '',
        priority: complaint.priority || '',
        completeness_status: complaint.completeness_status || '',
        completeness_feedback: complaint.completeness_feedback || '',
        root_cause_recommendation: complaint.root_cause_recommendation || '',
        capa_recommendation: complaint.capa_recommendation || '',
        summary: complaint.summary || '',
        risk_classification_reasoning: complaint.risk_classification_reasoning || '',
        next_action: complaint.next_action || '',
        risk_assessment_details: complaint.risk_assessment_details || ''
      };
      state.activeComplaintId = complaint.id;
      state.duplicateAlert = null;
    },
    addManualChatMessage: (state, action) => {
      state.chatHistory.push(action.payload);
    }
  },
  extraReducers: (builder) => {
    builder
      // Fetch list
      .addCase(fetchComplaints.pending, (state) => {
        state.listLoading = true;
      })
      .addCase(fetchComplaints.fulfilled, (state, action) => {
        state.listLoading = false;
        state.savedComplaints = action.payload;
      })
      .addCase(fetchComplaints.rejected, (state) => {
        state.listLoading = false;
      })
      
      // Save complaint
      .addCase(saveComplaint.pending, (state) => {
        state.saveLoading = true;
      })
      .addCase(saveComplaint.fulfilled, (state, action) => {
        state.saveLoading = false;
        // Update form state with saved details and active id
        state.activeComplaintId = action.payload.id;
        // Add to savedComplaints or update existing
        const idx = state.savedComplaints.findIndex(c => c.id === action.payload.id);
        if (idx !== -1) {
          state.savedComplaints[idx] = action.payload;
        } else {
          state.savedComplaints.unshift(action.payload);
        }
      })
      .addCase(saveComplaint.rejected, (state) => {
        state.saveLoading = false;
      })

      // Delete complaint
      .addCase(deleteComplaint.fulfilled, (state, action) => {
        state.savedComplaints = state.savedComplaints.filter(c => c.id !== action.payload);
        if (state.activeComplaintId === action.payload) {
          state.formData = { ...initialFormState };
          state.activeComplaintId = null;
        }
      })

      // Text Extraction
      .addCase(extractFromText.pending, (state) => {
        state.extractionLoading = true;
      })
      .addCase(extractFromText.fulfilled, (state, action) => {
        state.extractionLoading = false;
        // Merge extracted fields into form
        state.formData = { ...state.formData, ...action.payload };
        state.chatHistory.push({
          sender: 'ai',
          text: 'I have analyzed the complaint text and populated the form fields. Please review and save the complaint.'
        });
      })
      .addCase(extractFromText.rejected, (state, action) => {
        state.extractionLoading = false;
        state.chatHistory.push({
          sender: 'ai',
          text: `Failed to extract information: ${action.payload || 'Unknown error'}`
        });
      })

      // File Extraction
      .addCase(extractFromFile.pending, (state) => {
        state.extractionLoading = true;
      })
      .addCase(extractFromFile.fulfilled, (state, action) => {
        state.extractionLoading = false;
        state.formData = { ...state.formData, ...action.payload };
        state.chatHistory.push({
          sender: 'ai',
          text: 'Document processed successfully! The form fields have been populated. Please inspect the details.'
        });
      })
      .addCase(extractFromFile.rejected, (state, action) => {
        state.extractionLoading = false;
        state.chatHistory.push({
          sender: 'ai',
          text: `Failed to process document: ${action.payload || 'Unknown error'}`
        });
      })

      // Chat Messages
      .addCase(sendChatMessage.pending, (state) => {
        state.chatLoading = true;
        // Push user message to history
        state.chatHistory.push({ sender: 'user', text: state.currentChatInput });
        state.currentChatInput = '';
      })
      .addCase(sendChatMessage.fulfilled, (state, action) => {
        state.chatLoading = false;
        state.chatHistory.push({ sender: 'ai', text: action.payload.response });
        // Update form state in case the AI updated fields
        state.formData = { ...state.formData, ...action.payload.suggested_fields };
      })
      .addCase(sendChatMessage.rejected, (state, action) => {
        state.chatLoading = false;
        state.chatHistory.push({
          sender: 'ai',
          text: `Chat error: ${action.payload || 'Something went wrong'}`
        });
      })

      // AI Assessments
      .addCase(runAssessment.pending, (state, action) => {
        const type = action.meta.arg;
        state.assessmentLoading[type] = true;
      })
      .addCase(runAssessment.fulfilled, (state, action) => {
        const { type, result } = action.payload;
        state.assessmentLoading[type] = false;
        
        // Merge results into form
        if (type === 'completeness') {
          state.formData.completeness_status = result.completeness_status;
          state.formData.completeness_feedback = result.completeness_feedback;
        } else if (type === 'root_cause') {
          state.formData.root_cause_recommendation = result.root_cause_recommendation;
        } else if (type === 'capa') {
          state.formData.capa_recommendation = result.capa_recommendation;
        } else if (type === 'risk') {
          state.formData.initial_severity = result.initial_severity;
          state.formData.priority = result.priority;
          state.formData.risk_classification_reasoning = result.risk_classification_reasoning;
          state.formData.next_action = result.next_action || result.next_action;
          state.formData.risk_assessment_details = result.risk_assessment_details || result.risk_assessment_details;
        } else if (type === 'duplicate') {
          state.duplicateAlert = result.is_duplicate ? result.duplicate_details : 'No duplicates found.';
        } else if (type === 'summary') {
          state.formData.summary = result.summary;
        }
      })
      .addCase(runAssessment.rejected, (state, action) => {
        const type = action.meta.arg;
        state.assessmentLoading[type] = false;
      });
  }
});

export const { updateFormField, updateChatInput, resetForm, loadComplaintIntoForm, addManualChatMessage } = complaintSlice.actions;
export default complaintSlice.reducer;
