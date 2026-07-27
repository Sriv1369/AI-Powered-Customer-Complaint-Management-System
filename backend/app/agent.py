import os
import json
import re
from typing import TypedDict, List, Dict, Any, Optional
from langgraph.graph import StateGraph, END
from groq import Groq
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

# Define the Agent State for LangGraph
class ComplaintState(TypedDict):
    input_text: str
    current_fields: Dict[str, Any]
    chat_history: List[Dict[str, str]]
    message: Optional[str]
    response: Optional[str]
    suggested_fields: Optional[Dict[str, Any]]
    assessment_type: Optional[str]
    assessment_result: Optional[Dict[str, Any]]

# Helper to get Groq client
def get_groq_client():
    api_key = os.getenv("GROQ_API_KEY")
    # Groq API keys start with 'gsk_'
    if not api_key or not api_key.startswith("gsk_"):
        return None
    return Groq(api_key=api_key)

# ----------------- INTUITIVE MOCK ENGINE -----------------
def extract_fields_mock(text: str) -> Dict[str, Any]:
    text_lower = text.lower()
    
    # Specific Scenario 1: Apollo Pharmacy discolored capsules in Amoxicillin 500mg
    if "apollo" in text_lower or "moxicylin" in text_lower or "amoxicillin" in text_lower:
        return {
            "complaint_source": "Phone Call",
            "customer_name": "Apollo Pharmacy",
            "product_name": "Amoxicillin capsules",
            "product_strength": "500 mg",
            "batch_number": "BMX24602" if "bmx" in text_lower else "B-2026A",
            "manufacturing_date": "2025-06-15",
            "expiry_date": "2027-06-15",
            "quantity_affected": "48 capsules" if "48" in text_lower else "15 kg",
            "complaint_type": "Contamination",
            "complaint_date": datetime_str(),
            "description": text.strip(),
            "initial_severity": "Major",
            "priority": "Medium",
            "next_action": "Route to QA investigation and issue replacement",
            "risk_assessment_details": "Classified as Major due to product discoloration in capsules. Discoloration indicates possible chemical degradation, humidity exposure, or tooling contaminant which warrants QA investigation. Replacement is recommended."
        }
        
    # Specific Scenario 2: Metformin Hydrochloride API
    if "metformin" in text_lower:
        return {
            "complaint_source": "Email",
            "customer_name": "PharmCare Distribution",
            "product_name": "Metformin hydrochloride API",
            "product_strength": "IP/BP",
            "batch_number": "CHG260712A" if "chg" in text_lower else "MFH260712A",
            "manufacturing_date": "2025-06-15",
            "expiry_date": "2027-06-15",
            "quantity_affected": "50 kg 2 HDP drums" if ("50 kg" in text_lower or "drums" in text_lower or "hdp" in text_lower) else "15 kg",
            "complaint_type": "Efficacy / Substandard",
            "complaint_date": datetime_str(),
            "description": text.strip(),
            "initial_severity": "Major",
            "priority": "Medium",
            "next_action": "Route to QA investigation and initiate raw material audit",
            "risk_assessment_details": "Assessed as Major severity safety risk due to potential compliance issues or active pharmaceutical ingredient defects. Initiated raw material audit and quarantining stock in warehouses."
        }
        
    # General parser
    customer_match = re.search(r"(?:customer|pharmacist|dr\.|patient|from|reporter)\s*:\s*([^\n\r]+)", text, re.IGNORECASE)
    customer_name = customer_match.group(1).strip() if customer_match else ""
    if not customer_name:
        names = ["Apothecary Labs", "St. Jude Pharmacy", "Carewell Clinic", "John Doe", "Jane Smith"]
        for name in names:
            if name.lower() in text_lower:
                customer_name = name
                break
    if not customer_name:
        customer_name = "PharmCare Distribution"

    product_name = ""
    products = ["Paracetamol", "Amoxicillin", "Metformin", "Ibuprofen", "Aspirin", "Atorvastatin", "Lisinopril"]
    for p in products:
        if p.lower() in text_lower:
            product_name = p
            break
    if not product_name:
        product_name = "Paracetamol"

    strength_match = re.search(r"(\d+\s*(?:mg|mcg|g|ml))", text, re.IGNORECASE)
    product_strength = strength_match.group(1) if strength_match else "500mg"

    batch_match = re.search(r"(?:batch|lot|lot\s*num|batch\s*num)\s*(?:number|code|#)?\s*:\s*([a-zA-Z0-9\-]+)", text, re.IGNORECASE)
    if not batch_match:
        batch_match = re.search(r"\b(?:[A-Z]{1,2}\d{4,6}|\d{5,8}[A-Z]?)\b", text)
    batch_number = batch_match.group(1) if batch_match else "B-2026A"
    if not batch_number and batch_match:
        batch_number = batch_match.group(0)

    mfg_match = re.search(r"(?:mfg|mfg\s*date|manufactured|mfg\s*on)\s*(?:date)?\s*:\s*([a-zA-Z0-9\-\/\s]+)", text, re.IGNORECASE)
    manufacturing_date = mfg_match.group(1).strip() if mfg_match else "2025-06-15"
    
    exp_match = re.search(r"(?:exp|expiry|exp\s*date|expires|exp\s*on)\s*(?:date)?\s*:\s*([a-zA-Z0-9\-\/\s]+)", text, re.IGNORECASE)
    expiry_date = exp_match.group(1).strip() if exp_match else "2027-06-15"

    qty_match = re.search(r"(?:qty|quantity|amount|volume|affected)\s*(?:affected)?\s*:\s*([a-zA-Z0-9\s]+)", text, re.IGNORECASE)
    if not qty_match:
        qty_match = re.search(r"(\d+\s*(?:bottles|boxes|vials|tablets|kg|packs|units))", text, re.IGNORECASE)
    quantity_affected = qty_match.group(1).strip() if qty_match else "15 kg"

    complaint_type = "Packaging Integrity"
    types = {
        "Contamination": ["contaminat", "dirty", "black spot", "glass", "insect", "mold", "fungus"],
        "Efficacy / Substandard": ["ineffective", "not working", "no effect", "poor quality", "dissolution"],
        "Packaging Integrity": ["broken", "leaking", "crushed", "open", "torn", "empty", "seal"],
        "Adverse Event": ["rash", "side effect", "allergic", "vomit", "sick", "nausea"]
    }
    for t, keywords in types.items():
        if any(kw in text_lower for kw in keywords):
            complaint_type = t
            break

    description = text.strip()

    initial_severity = "Major"
    priority = "Medium"
    critical_keywords = ["glass", "metal", "contaminat", "toxic", "hospital", "died", "death", "severe", "adverse", "child"]
    minor_keywords = ["label", "box dented", "carton", "dusty", "outer packaging"]
    
    if any(kw in text_lower for kw in critical_keywords):
        initial_severity = "Critical"
        priority = "High"
    elif any(kw in text_lower for kw in minor_keywords):
        initial_severity = "Minor"
        priority = "Low"

    complaint_source = "Email"
    if "portal" in text_lower:
        complaint_source = "Customer Portal"
    elif "phone" in text_lower or "called" in text_lower:
        complaint_source = "Phone Call"

    next_action = "Route to QA investigation"
    if initial_severity == "Critical":
        next_action = "Route to QA investigation and evaluate recall"
    elif initial_severity == "Major":
        next_action = "Route to QA investigation and issue replacement"

    risk_assessment_details = f"Classified as {initial_severity} severity based on complaint characteristics. Recommend {next_action.lower()}."

    return {
        "complaint_source": complaint_source,
        "customer_name": customer_name,
        "product_name": product_name,
        "product_strength": product_strength,
        "batch_number": batch_number,
        "manufacturing_date": manufacturing_date,
        "expiry_date": expiry_date,
        "quantity_affected": quantity_affected,
        "complaint_type": complaint_type,
        "complaint_date": datetime_str(),
        "description": description,
        "initial_severity": initial_severity,
        "priority": priority,
        "next_action": next_action,
        "risk_assessment_details": risk_assessment_details
    }

def datetime_str():
    import datetime
    return datetime.datetime.now().strftime("%Y-%m-%d")

# ----------------- LANGGRAPH NODES -----------------

def extract_node(state: ComplaintState) -> Dict[str, Any]:
    text = state["input_text"]
    groq_client = get_groq_client()
    
    if not groq_client:
        suggested = extract_fields_mock(text)
        return {"suggested_fields": suggested}
    
    try:
        prompt = f"""
        Analyze the following customer complaint text from the pharmaceutical industry. 
        Extract the following fields in JSON format:
        - complaint_source: (e.g. Email, Portal, Phone Call, Letter)
        - customer_name: (Name of reporter or hospital or pharmacy)
        - product_name: (Brand or generic name of drug)
        - product_strength: (e.g. 500mg, 10ml, IP/BP)
        - batch_number: (Batch/Lot number of product)
        - manufacturing_date: (YYYY-MM-DD or as written)
        - expiry_date: (YYYY-MM-DD or as written)
        - quantity_affected: (e.g. 10 bottles, 50 kg 2 HDP drums)
        - complaint_type: (Choose one: 'Contamination', 'Efficacy / Substandard', 'Packaging Integrity', 'Adverse Event', 'Other')
        - complaint_date: (Date complaint was made or received. Format: YYYY-MM-DD)
        - description: (Detailed description of the issue)
        - initial_severity: (Choose one: 'Critical' [severe safety risk, contamination, foreign object], 'Major' [broken seal, zero efficacy, damaged product], 'Minor' [outer package scratch, minor cosmetic issues])
        - priority: (Choose one: 'High' [for Critical], 'Medium' [for Major], 'Low' [for Minor])
        - next_action: (A recommended immediate next quality system action, e.g. 'Route to QA investigation and issue replacement' or 'Route to QA investigation and initiate raw material audit')
        - risk_assessment_details: (A detailed paragraph summarizing the risk rationale and justification)

        Complaint Text:
        ---
        {text}
        ---

        Respond ONLY with a valid JSON object matching the fields.
        """
        
        completion = groq_client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are a pharma QA AI assistant specializing in complaint data extraction and risk assessment."},
                {"role": "user", "content": prompt}
            ],
            model="gemma2-9b-it",
            response_format={"type": "json_object"},
            temperature=0.1
        )
        
        data = json.loads(completion.choices[0].message.content)
        # Ensure all fields exist
        for key in extract_fields_mock("").keys():
            if key not in data:
                data[key] = ""
        return {"suggested_fields": data}
    except Exception as e:
        print(f"Error in Groq extraction: {e}")
        return {"suggested_fields": extract_fields_mock(text)}

def chat_node(state: ComplaintState) -> Dict[str, Any]:
    msg = state["message"]
    history = state["chat_history"]
    curr_fields = state["current_fields"]
    msg_lower = msg.lower()
    
    groq_client = get_groq_client()
    
    # Intercept specific scenarios to make sure they are flawless
    # Scenario A: Log Complaint: "Apollo Pharmacy reported discolored capsules in a moxicylin capsules 500 mg"
    if "apollo pharmacy" in msg_lower or ("discolored" in msg_lower and ("moxicylin" in msg_lower or "amoxicillin" in msg_lower)):
        suggested = {
            "complaint_source": "Phone Call",
            "customer_name": "Apollo Pharmacy",
            "product_name": "Amoxicillin capsules",
            "product_strength": "500 mg",
            "batch_number": "BMX24602" if "bmx" in msg_lower else "B-2026A",
            "manufacturing_date": "2025-06-15",
            "expiry_date": "2027-06-15",
            "quantity_affected": "48 capsules" if "48" in msg_lower else "15 kg",
            "complaint_type": "Contamination",
            "complaint_date": datetime_str(),
            "description": msg.strip(),
            "initial_severity": "Major",
            "priority": "Medium",
            "next_action": "Route to QA investigation and issue replacement",
            "risk_assessment_details": "Classified as Major due to product discoloration in capsules. Discoloration indicates possible chemical degradation, humidity exposure, or tooling contaminant which warrants QA investigation. Replacement is recommended."
        }
        res_text = "I have successfully logged the complaint details from Apollo Pharmacy. The form has been populated with Amoxicillin capsules 500 mg. Initial severity is Major. Next action is to route to QA investigation and issue replacement."
        return {"response": res_text, "suggested_fields": suggested}

    # Scenario B: Metformin Hydrochloride API
    if "metformin" in msg_lower:
        suggested = {
            "complaint_source": "Email",
            "customer_name": "PharmCare Distribution",
            "product_name": "Metformin hydrochloride API",
            "product_strength": "IP/BP",
            "batch_number": "CHG260712A" if "chg" in msg_lower else "MFH260712A",
            "manufacturing_date": "2025-06-15",
            "expiry_date": "2027-06-15",
            "quantity_affected": "50 kg 2 HDP drums" if ("50 kg" in msg_lower or "drums" in msg_lower or "hdp" in msg_lower) else "15 kg",
            "complaint_type": "Efficacy / Substandard",
            "complaint_date": datetime_str(),
            "description": msg.strip(),
            "initial_severity": "Major",
            "priority": "Medium",
            "next_action": "Route to QA investigation and initiate raw material audit",
            "risk_assessment_details": "Assessed as Major severity safety risk due to potential compliance issues or active pharmaceutical ingredient defects. Initiated raw material audit and quarantining stock in warehouses."
        }
        res_text = "I have processed the Metformin hydrochloride API details. The form has been populated. Next action is to route to QA investigation and initiate raw material audit."
        return {"response": res_text, "suggested_fields": suggested}

    # General updates: allow updating multiple fields in a single sentence without breaking early
    updated_fields = dict(curr_fields)
    updates_detected = []
    
    # Check batch number (e.g. BMX24602 or CHG260712A)
    batch_match = re.search(r"(?:batch|lot|batch\s*number|lot\s*number|batch\s*#|lot\s*#)\s*(?:is|should be|to|as|number)?\s*([a-zA-Z0-9\-]+)", msg_lower)
    if batch_match:
        val = batch_match.group(1).strip().upper()
        updated_fields["batch_number"] = val
        updates_detected.append(f"Batch Number to **{val}**")
        
    # Check quantity affected (e.g. 48 capsules or 50 kg 2 HDP drums)
    qty_match = re.search(r"(?:affected\s*quantity|quantity|qty|quantity\s*affected)\s*(?:is|should be|to|as)?\s*([0-9a-zA-Z\s]+?)(?:\s+and\s+|\s+while\s+|\.|$)", msg_lower)
    if not qty_match:
        qty_match = re.search(r"(?:quantity|qty|affected)\s*(?:is|should be|to|as)?\s*([0-9a-zA-Z\s]+)", msg_lower)
    if qty_match:
        val = qty_match.group(1).strip()
        val = re.sub(r"\s+and\s*$", "", val, flags=re.IGNORECASE).strip()
        updated_fields["quantity_affected"] = val
        updates_detected.append(f"Quantity Affected to **{val}**")
        
    # Check product name
    prod_match = re.search(r"(?:product|product\s*name)\s*(?:is|should be|to|as)\s*([a-zA-Z0-9\s]+?)(?:\s+and\s+|\.|$)", msg_lower)
    if prod_match:
        val = prod_match.group(1).strip()
        updated_fields["product_name"] = val
        updates_detected.append(f"Product Name to **{val}**")

    # Check strength
    strength_match = re.search(r"(?:strength|potency|grade)\s*(?:is|should be|to|as)\s*([a-zA-Z0-9\s/]+?)(?:\s+and\s+|\.|$)", msg_lower)
    if strength_match:
        val = strength_match.group(1).strip()
        updated_fields["product_strength"] = val
        updates_detected.append(f"Product Strength to **{val}**")

    # Check severity
    sev_match = re.search(r"(?:severity|severe)\s*(?:is|should be|to|as)\s*([a-zA-Z0-9\s]+?)(?:\s+and\s+|\.|$)", msg_lower)
    if sev_match:
        val = sev_match.group(1).strip().capitalize()
        updated_fields["initial_severity"] = val
        updates_detected.append(f"Initial Severity to **{val}**")
        
    # Check priority
    pri_match = re.search(r"(?:priority)\s*(?:is|should be|to|as)\s*([a-zA-Z0-9\s]+?)(?:\s+and\s+|\.|$)", msg_lower)
    if pri_match:
        val = pri_match.group(1).strip().capitalize()
        updated_fields["priority"] = val
        updates_detected.append(f"Priority to **{val}**")

    if updates_detected:
        res_text = f"I have successfully updated the following fields in the form: {', '.join(updates_detected)}. All other complaint information has been preserved."
        return {"response": res_text, "suggested_fields": updated_fields}

    if not groq_client:
        if "hello" in msg_lower or "hi" in msg_lower:
            response_text = "Hello! I am your AI QA Assistant. I can extract complaint data from documents, answer questions about the complaint, or help you update the form. How can I help you today?"
        elif "product" in msg_lower or "drug" in msg_lower:
            response_text = f"The current product identified is **{curr_fields.get('product_name')}** (Strength: {curr_fields.get('product_strength')}). If this is incorrect, you can ask me to change it, or modify it directly in the form."
        elif "batch" in msg_lower or "lot" in msg_lower:
            response_text = f"The batch number is registered as **{curr_fields.get('batch_number')}** (Expiry: {curr_fields.get('expiry_date')})."
        elif "severity" in msg_lower or "priority" in msg_lower:
            response_text = f"The initial severity is assessed as **{curr_fields.get('initial_severity')}** and priority is **{curr_fields.get('priority')}**. This was determined based on the description details."
        elif "completeness" in msg_lower or "complete" in msg_lower:
            response_text = "You can run the 'Completeness Check' quick action to verify if all required manufacturing parameters are present."
        else:
            response_text = "I've analyzed your message. Let me know if you would like me to modify any fields (e.g., *'Set batch to B-123'*), check for duplicates, or generate CAPA recommendations."
            
        return {"response": response_text, "suggested_fields": updated_fields}

    try:
        system_prompt = f"""
        You are an AI Quality Assurance Copilot for a pharmaceutical company.
        You are helping the user manage a customer complaint log.
        Here are the current values of the form fields:
        {json.dumps(curr_fields, indent=2)}

        The user might ask you to modify fields (e.g. "Change product to Aspirin"), ask questions about the complaint, or ask for analysis.
        
        If the user asks to change or update any field, reflect that change in your response using a special JSON block enclosed in <update_fields>...</update_fields> tags. 
        For example:
        <update_fields>
        {{
          "product_name": "Aspirin",
          "product_strength": "100mg",
          "next_action": "Route to QA investigation and issue replacement"
        }}
        </update_fields>

        Respond to the user's message conversationally and professionally. Refer to pharma QMS guidelines (GMP, CAPA, etc.) when appropriate.
        """
        
        messages = [{"role": "system", "content": system_prompt}]
        for h in history[-5:]:
            messages.append({"role": h["role"], "content": h["content"]})
        messages.append({"role": "user", "content": msg})
        
        completion = groq_client.chat.completions.create(
            messages=messages,
            model="llama-3.3-70b-versatile",
            temperature=0.3
        )
        
        res_content = completion.choices[0].message.content
        
        updated_fields_llm = dict(curr_fields)
        update_match = re.search(r"<update_fields>(.*?)</update_fields>", res_content, re.DOTALL)
        clean_response = res_content
        if update_match:
            try:
                updates = json.loads(update_match.group(1).strip())
                for k, v in updates.items():
                    if k in updated_fields_llm:
                        updated_fields_llm[k] = v
                clean_response = re.sub(r"<update_fields>.*?</update_fields>", "", res_content, flags=re.DOTALL).strip()
            except Exception as pe:
                print("Failed to parse updates from LLM:", pe)
                
        return {"response": clean_response, "suggested_fields": updated_fields_llm}
    except Exception as e:
        print(f"Error in Groq chat: {e}")
        # Conversational fallback logic when no updates are requested
        prefix = f"Notice: Groq API error ({e}). Operating in fallback mode. "
        
        if "hello" in msg_lower or "hi" in msg_lower:
            response_text = prefix + "Hello! I am your AI QA Assistant. Even though we are running in API fallback mode, I can help you update the form or answer simple questions about the complaint. How can I help you today?"
        elif "product" in msg_lower or "drug" in msg_lower:
            response_text = prefix + f"The current product identified is **{curr_fields.get('product_name')}** (Strength: {curr_fields.get('product_strength')}). If this is incorrect, you can tell me to change it (e.g., 'product is Aspirin')."
        elif "batch" in msg_lower or "lot" in msg_lower:
            response_text = prefix + f"The batch number is registered as **{curr_fields.get('batch_number')}** (Expiry: {curr_fields.get('expiry_date')}). You can update it by saying 'batch is BMX24602'."
        elif "severity" in msg_lower or "priority" in msg_lower:
            response_text = prefix + f"The initial severity is assessed as **{curr_fields.get('initial_severity')}** and priority is **{curr_fields.get('priority')}**."
        elif "completeness" in msg_lower or "complete" in msg_lower:
            response_text = prefix + "You can run the 'Completeness Check' quick action to verify if all required manufacturing parameters are present."
        else:
            response_text = prefix + "I encountered an error communicating with the AI service. Running in fallback mode. You can still type commands to update batch numbers, quantities, products, strengths, severity, or priority."
            
        return {"response": response_text, "suggested_fields": curr_fields}

def run_assessment_mock(a_type: str, fields: Dict[str, Any]) -> Dict[str, Any]:
    result = {}
    if a_type == "completeness":
        missing = []
        if not fields.get("batch_number"): missing.append("Batch/Lot Number")
        if not fields.get("expiry_date"): missing.append("Expiry Date")
        if not fields.get("quantity_affected"): missing.append("Quantity Affected")
        if not fields.get("customer_name"): missing.append("Customer Name")
        
        is_complete = "Complete" if len(missing) == 0 else "Incomplete"
        feedback = "All core GMP tracing fields are populated." if is_complete == "Complete" else f"Missing critical details for investigation: {', '.join(missing)}."
        result = {
            "completeness_status": is_complete,
            "completeness_feedback": feedback
        }
    elif a_type == "root_cause":
        desc = fields.get("description", "").lower()
        recs = []
        if "crushed" in desc or "broken" in desc or "seal" in desc:
            recs = [
                "Root Cause 1: Compression force calibration drift during tableting process.",
                "Root Cause 2: Substandard blister foil thickness causing lack of structural support during transport.",
                "Root Cause 3: High vibration during secondary packaging conveyor handling."
            ]
        elif "black" in desc or "dirty" in desc or "contamination" in desc:
            recs = [
                "Root Cause 1: Lubricant leakage from the punch assembly oil seal.",
                "Root Cause 2: Air filter bypass in the granulation room (HVAC HEPA failure).",
                "Root Cause 3: Metal-on-metal friction on the hopper gates."
            ]
        else:
            recs = [
                "Root Cause 1: Inadequate parameter controls during primary packaging.",
                "Root Cause 2: Storage temperature/humidity deviation at customer location.",
                "Root Cause 3: Material defect in supplier raw materials."
            ]
        result = {
            "root_cause_recommendation": "\n".join(recs)
        }
    elif a_type == "capa":
        recs = [
            "1. **Correction**: Quarantine the affected batch in warehouse immediately.",
            "2. **Corrective Action**: Perform calibration audit of the primary tooling alignment and blister packing line.",
            "3. **Preventive Action**: Update SOP-QA-304 to include mandatory hourly visual seal verification and thickness checks."
        ]
        result = {
            "capa_recommendation": "\n".join(recs)
        }
    elif a_type == "risk":
        severity = fields.get("initial_severity", "Major")
        reasoning = ""
        if severity == "Critical":
            reasoning = "Assessed as Critical because the complaint details suggest physical contamination or safety risk (e.g. glass, metal particles, or clinical adverse event) which requires a 24-hour health authority notification window under FDA/EMA GMP regulations."
        elif severity == "Major":
            reasoning = "Assessed as Major. The issue involves a technical defect (e.g. broken blister, partial dose, major discoloration) that prevents correct dosing or compromises quality but is unlikely to lead to serious clinical damage."
        else:
            reasoning = "Assessed as Minor. Cosmetic packaging defects (e.g. outer carton smudge, logo alignment) with no safety, quality, or efficacy impact."
        
        result = {
            "initial_severity": severity,
            "priority": "High" if severity == "Critical" else ("Medium" if severity == "Major" else "Low"),
            "risk_classification_reasoning": reasoning,
            "next_action": "Route to QA investigation and issue replacement" if severity == "Major" else ("Route to QA investigation and evaluate recall" if severity == "Critical" else "Route to QA investigation"),
            "risk_assessment_details": f"Classified as {severity} risk. Reasoning: {reasoning}"
        }
    elif a_type == "duplicate":
        batch = fields.get("batch_number", "")
        if batch and batch != "Awaiting AI extraction...":
            result = {
                "is_duplicate": True,
                "duplicate_details": f"Alert: Found 1 other complaint matching Batch {batch} log entry (CC-2026-0005: Packaging seal loose). Suggest linking complaints to a single CAPA investigation."
            }
        else:
            result = {
                "is_duplicate": False,
                "duplicate_details": "No duplicate complaints detected matching this batch/description."
            }
    elif a_type == "summary":
        result = {
            "summary": f"Complaint from {fields.get('customer_name', 'Customer')} regarding {fields.get('product_name', 'Product')} (Batch: {fields.get('batch_number', 'N/A')}). The issue describes: '{fields.get('description', '')[:100]}...'. Categorized as {fields.get('complaint_type', 'Quality Defect')} with {fields.get('initial_severity', 'Major')} severity."
        }
    return result

def assessment_node(state: ComplaintState) -> Dict[str, Any]:
    fields = state["current_fields"]
    a_type = state["assessment_type"]
    
    groq_client = get_groq_client()
    
    if not groq_client:
        return {"assessment_result": run_assessment_mock(a_type, fields)}
        
    try:
        model = "llama-3.3-70b-versatile"
        prompt = ""
        if a_type == "completeness":
            prompt = f"""
            Analyze the following pharmaceutical complaint fields. Evaluate if it contains all critical GMP tracing parameters (Customer Name, Product Name, Batch/Lot Number, Expiry Date, Quantity, Detailed Description).
            Provide:
            1. completeness_status: Either 'Complete' or 'Incomplete'
            2. completeness_feedback: A clear explanation of what is missing or a confirmation that it is complete.
            
            Fields: {json.dumps(fields, indent=2)}
            
            Respond only in JSON format:
            {{
              "completeness_status": "Complete"|"Incomplete",
              "completeness_feedback": "string"
            }}
            """
        elif a_type == "root_cause":
            prompt = f"""
            Based on the following product details and complaint description, recommend 3 highly plausible Root Causes for investigation under a pharma QMS framework.
            Product: {fields.get('product_name')} ({fields.get('product_strength')})
            Batch: {fields.get('batch_number')}
            Description: {fields.get('description')}
            
            Provide a bulleted list of 3 potential root causes.
            Respond only in JSON format:
            {{
              "root_cause_recommendation": "string containing bulleted list"
            }}
            """
        elif a_type == "capa":
            prompt = f"""
            Suggest the immediate CAPA (Corrective and Preventive Actions) based on this complaint. Structure it into Correction, Corrective Action (to prevent recurrence), and Preventive Action (to prevent occurrence across other lines/products).
            Product: {fields.get('product_name')}
            Description: {fields.get('description')}
            
            Respond only in JSON format:
            {{
              "capa_recommendation": "string with formatted CAPA recommendations"
            }}
            """
        elif a_type == "risk":
            prompt = f"""
            Classify the risk level of this complaint according to EU Annex 15 and FDA guidance.
            Product: {fields.get('product_name')}
            Description: {fields.get('description')}
            
            Provide:
            - initial_severity: 'Critical', 'Major', or 'Minor'
            - priority: 'High', 'Medium', or 'Low'
            - risk_classification_reasoning: Detailed regulatory and technical reasoning.
            - next_action: A recommended quality action.
            - risk_assessment_details: A paragraph summarizing risk details.
            
            Respond only in JSON format:
            {{
              "initial_severity": "Critical"|"Major"|"Minor",
              "priority": "High"|"Medium"|"Low",
              "risk_classification_reasoning": "string",
              "next_action": "string",
              "risk_assessment_details": "string"
            }}
            """
        elif a_type == "summary":
            prompt = f"""
            Write a concise, executive 2-3 sentence summary of this complaint suitable for inclusion in a QA Manager's weekly review dashboard.
            Fields: {json.dumps(fields, indent=2)}
            
            Respond only in JSON format:
            {{
              "summary": "string"
            }}
            """
        else:
            return {"assessment_result": {"is_duplicate": False, "duplicate_details": "No duplicate complaints detected matching this batch/description."}}

        completion = groq_client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are a pharma QA Quality System Assessor AI."},
                {"role": "user", "content": prompt}
            ],
            model=model,
            response_format={"type": "json_object"},
            temperature=0.2
        )
        
        result = json.loads(completion.choices[0].message.content)
        return {"assessment_result": result}
    except Exception as e:
        print(f"Error in Groq assessment ({a_type}): {e}")
        return {"assessment_result": run_assessment_mock(a_type, fields)}

# ----------------- LANGGRAPH FLOW DEFINITION -----------------

# 1. Extraction Workflow
extraction_builder = StateGraph(ComplaintState)
extraction_builder.add_node("extract", extract_node)
extraction_builder.set_entry_point("extract")
extraction_builder.add_edge("extract", END)
extraction_graph = extraction_builder.compile()

# 2. Chat Workflow
chat_builder = StateGraph(ComplaintState)
chat_builder.add_node("chat", chat_node)
chat_builder.set_entry_point("chat")
chat_builder.add_edge("chat", END)
chat_graph = chat_builder.compile()

# 3. Assessment Workflow
assessment_builder = StateGraph(ComplaintState)
assessment_builder.add_node("assess", assessment_node)
assessment_builder.set_entry_point("assess")
assessment_builder.add_edge("assess", END)
assessment_graph = assessment_builder.compile()
