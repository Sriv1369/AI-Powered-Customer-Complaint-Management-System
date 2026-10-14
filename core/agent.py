import os
import json
import re
import datetime
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())


def datetime_str() -> str:
    return datetime.datetime.now().strftime("%Y-%m-%d")


def get_groq_client():
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key or not api_key.startswith("gsk_"):
        return None
    try:
        from groq import Groq
        return Groq(api_key=api_key)
    except ImportError:
        return None


# ----------------- INTUITIVE MOCK ENGINE -----------------

def extract_fields_mock(text: str) -> Dict[str, Any]:
    text_lower = text.lower()

    # Scenario 1: Apollo Pharmacy
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

    # Scenario 2: Metformin Hydrochloride API
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
        names = ["Apothecary Labs", "Saint Jude Pharmacy", "Carewell Clinic", "John Doe", "Jane Smith"]
        for name in names:
            if name.lower() in text_lower:
                customer_name = name
                break
    if not customer_name:
        customer_name = "Saint Jude Pharmacy Distribution"

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
    batch_number = batch_match.group(1) if batch_match and hasattr(batch_match, "group") and batch_match.lastindex else (batch_match.group(0) if batch_match else "P1234")

    mfg_match = re.search(r"(?:mfg|mfg\s*date|manufactured|mfg\s*on)\s*(?:date)?\s*:\s*([a-zA-Z0-9\-\/\s]+)", text, re.IGNORECASE)
    manufacturing_date = mfg_match.group(1).strip() if mfg_match else "2025-06-15"

    exp_match = re.search(r"(?:exp|expiry|exp\s*date|expires|exp\s*on)\s*(?:date)?\s*:\s*([a-zA-Z0-9\-\/\s]+)", text, re.IGNORECASE)
    expiry_date = exp_match.group(1).strip() if exp_match else "2027-06-15"

    qty_match = re.search(r"(?:qty|quantity|amount|volume|affected)\s*(?:affected)?\s*:\s*([a-zA-Z0-9\s]+)", text, re.IGNORECASE)
    if not qty_match:
        qty_match = re.search(r"(\d+\s*(?:bottles|boxes|vials|tablets|kg|packs|units))", text, re.IGNORECASE)
    quantity_affected = qty_match.group(1).strip() if qty_match else "15 kg (20 bottles)"

    complaint_type = "Packaging Integrity"
    types = {
        "Contamination": ["contaminat", "dirty", "black spot", "glass", "insect", "mold", "fungus", "discoloration", "residue"],
        "Efficacy / Substandard": ["ineffective", "not working", "no effect", "poor quality", "dissolution"],
        "Packaging Integrity": ["broken", "leaking", "crushed", "open", "torn", "empty", "seal", "foil"],
        "Adverse Event": ["rash", "side effect", "allergic", "vomit", "sick", "nausea"]
    }
    for t, keywords in types.items():
        if any(kw in text_lower for kw in keywords):
            complaint_type = t
            break

    initial_severity = "Major"
    priority = "Medium"
    critical_keywords = ["glass", "metal", "toxic", "hospital", "died", "death", "severe", "adverse", "child"]
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

    risk_assessment_details = f"Classified as {initial_severity} severity based on defect inspection and pharmaceutical GMP risk profile. Recommend {next_action.lower()}."

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
        "description": text.strip(),
        "initial_severity": initial_severity,
        "priority": priority,
        "next_action": next_action,
        "risk_assessment_details": risk_assessment_details
    }


def run_assessment_mock(a_type: str, fields: Dict[str, Any]) -> Dict[str, Any]:
    if a_type == "completeness":
        missing = []
        if not fields.get("batch_number"): missing.append("Batch/Lot Number")
        if not fields.get("expiry_date"): missing.append("Expiry Date")
        if not fields.get("quantity_affected"): missing.append("Quantity Affected")
        if not fields.get("customer_name"): missing.append("Customer Name")

        is_complete = "Complete" if len(missing) == 0 else "Incomplete"
        feedback = "All core GMP tracing fields are populated." if is_complete == "Complete" else f"Missing critical details for investigation: {', '.join(missing)}."
        return {
            "completeness_status": is_complete,
            "completeness_feedback": feedback
        }

    elif a_type == "root_cause":
        desc = (fields.get("description") or "").lower()
        if "crushed" in desc or "broken" in desc or "seal" in desc or "foil" in desc:
            recs = [
                "Root Cause 1: Compression force calibration drift during primary blister packaging.",
                "Root Cause 2: Substandard blister sealing foil thickness causing lack of barrier integrity during transit.",
                "Root Cause 3: High mechanical vibration during secondary packing conveyor sorting."
            ]
        elif "black" in desc or "dirty" in desc or "contamination" in desc or "discoloration" in desc:
            recs = [
                "Root Cause 1: Lubricant leakage from the rotary tableting punch assembly oil seal.",
                "Root Cause 2: Air filter bypass in the granulation room (HVAC HEPA filter gasket failure).",
                "Root Cause 3: Tooling friction and metal wear on feed hopper gate plates."
            ]
        else:
            recs = [
                "Root Cause 1: Inadequate environmental parameter control during primary dosage packaging.",
                "Root Cause 2: Storage temperature/humidity excursion during intermediate transit.",
                "Root Cause 3: Raw material supplier lot-to-lot consistency deviation."
            ]
        return {
            "root_cause_recommendation": "\n".join(recs)
        }

    elif a_type == "capa":
        recs = [
            "1. **Correction**: Immediately quarantine all remaining units of the affected batch in warehouse staging.",
            "2. **Corrective Action**: Conduct root-cause inspection of primary sealing jaws and recalibrate sealing temperature sensors.",
            "3. **Preventive Action**: Update SOP-QA-304 to mandate double-check visual seal verification every 30 minutes on active packaging lines."
        ]
        return {
            "capa_recommendation": "\n".join(recs)
        }

    elif a_type == "risk":
        severity = fields.get("initial_severity", "Major") or "Major"
        if severity == "Critical":
            reasoning = "Assessed as Critical because the defect indicates physical foreign object contamination or acute patient safety risk, triggering a mandatory 24-hour health authority alert under FDA 21 CFR §211.198 and EU GMP Chapter 8."
        elif severity == "Major":
            reasoning = "Assessed as Major. The defect involves compromised packaging barrier or potential active ingredient degradation affecting product quality without immediate irreversible clinical harm."
        else:
            reasoning = "Assessed as Minor. Cosmetic packaging defects (outer carton abrasion, labeling alignment) with no product efficacy or patient safety impact."

        return {
            "initial_severity": severity,
            "priority": "High" if severity == "Critical" else ("Medium" if severity == "Major" else "Low"),
            "risk_classification_reasoning": reasoning,
            "next_action": "Route to QA investigation and issue replacement" if severity == "Major" else ("Route to QA investigation and evaluate recall" if severity == "Critical" else "Route to QA investigation"),
            "risk_assessment_details": f"Classified as {severity} risk. Regulatory Rationale: {reasoning}"
        }

    elif a_type == "duplicate":
        batch = fields.get("batch_number", "")
        if batch and batch.lower() not in ("awaiting ai extraction...", "n/a", ""):
            return {
                "is_duplicate": True,
                "duplicate_details": f"Alert: Found 1 other logged complaint matching Batch {batch} (CC-2026-0005: Packaging seal loose). Suggested Action: Link complaints to a single CAPA investigation."
            }
        else:
            return {
                "is_duplicate": False,
                "duplicate_details": "No duplicate complaints detected matching this batch/description."
            }

    elif a_type == "summary":
        cust = fields.get("customer_name") or "Customer"
        prod = fields.get("product_name") or "Product"
        batch = fields.get("batch_number") or "N/A"
        desc = (fields.get("description") or "")[:120]
        sev = fields.get("initial_severity") or "Major"
        c_type = fields.get("complaint_type") or "Quality Defect"
        return {
            "summary": f"Quality complaint received from {cust} regarding {prod} (Batch {batch}). Issue reports: '{desc}...'. Triage assessment classified as {c_type} with {sev} severity level."
        }

    return {}


# ----------------- MAIN AGENT APIS -----------------

def extract_complaint_from_text(text: str) -> Dict[str, Any]:
    """Extracts structured complaint fields from raw text using Groq or fallback mock."""
    groq_client = get_groq_client()
    if not groq_client:
        return extract_fields_mock(text)

    try:
        prompt = f"""
        Analyze the following customer complaint text from the pharmaceutical industry. 
        Extract the following fields in JSON format:
        - complaint_source: (e.g. Email, Customer Portal, Phone Call, Letter)
        - customer_name: (Name of reporter, hospital, or pharmacy)
        - product_name: (Brand or generic name of drug)
        - product_strength: (e.g. 500mg, 10ml, IP/BP)
        - batch_number: (Batch/Lot number of product)
        - manufacturing_date: (YYYY-MM-DD or as written)
        - expiry_date: (YYYY-MM-DD or as written)
        - quantity_affected: (e.g. 10 bottles, 50 kg 2 HDP drums)
        - complaint_type: (Choose one: 'Contamination', 'Efficacy / Substandard', 'Packaging Integrity', 'Adverse Event', 'Other')
        - complaint_date: (Date complaint was made or received. Format: YYYY-MM-DD)
        - description: (Detailed description of the issue)
        - initial_severity: (Choose one: 'Critical', 'Major', 'Minor')
        - priority: (Choose one: 'High', 'Medium', 'Low')
        - next_action: (A recommended immediate next quality system action)
        - risk_assessment_details: (A paragraph summarizing the risk rationale and justification)

        Complaint Text:
        ---
        {text}
        ---

        Respond ONLY with a valid JSON object matching the fields.
        """
        completion = groq_client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are a pharma QA AI assistant specializing in GMP complaint data extraction and risk assessment."},
                {"role": "user", "content": prompt}
            ],
            model="gemma2-9b-it",
            response_format={"type": "json_object"},
            temperature=0.1
        )
        data = json.loads(completion.choices[0].message.content)
        mock_sample = extract_fields_mock("")
        for key in mock_sample.keys():
            if key not in data:
                data[key] = mock_sample[key]
        return data
    except Exception as e:
        print(f"Groq extraction failed ({e}), using mock engine.")
        return extract_fields_mock(text)


def chat_with_copilot(
    message: str,
    chat_history: List[Dict[str, str]],
    current_fields: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Handles conversational copilot chat and updates form fields dynamically.
    Returns: {"response": str, "suggested_fields": Dict[str, Any]}
    """
    msg_lower = message.lower().strip()
    updated_fields = dict(current_fields)

    # Scenario A: Apollo Pharmacy
    if "apollo pharmacy" in msg_lower or ("discolored" in msg_lower and ("moxicylin" in msg_lower or "amoxicillin" in msg_lower)):
        mock_data = extract_fields_mock(message)
        res_text = "I have logged the complaint details for Apollo Pharmacy regarding Amoxicillin capsules 500 mg. The form fields have been populated. Initial severity is Major. Recommended next action: Route to QA investigation and issue replacement."
        return {"response": res_text, "suggested_fields": mock_data}

    # Scenario B: Metformin
    if "metformin" in msg_lower:
        mock_data = extract_fields_mock(message)
        res_text = "I have logged the Metformin hydrochloride API details. The form fields have been populated. Recommended next action: Route to QA investigation and initiate raw material audit."
        return {"response": res_text, "suggested_fields": mock_data}

    # Heuristic field modification rules
    updates_detected = []

    # Batch number
    batch_match = re.search(r"(?:batch|lot|batch\s*number|lot\s*number|batch\s*#|lot\s*#)\s*(?:is|should be|to|as|number)?\s*([a-zA-Z0-9\-]+)", msg_lower)
    if batch_match:
        val = batch_match.group(1).strip().upper()
        updated_fields["batch_number"] = val
        updates_detected.append(f"Batch Number to **{val}**")

    # Quantity affected
    qty_match = re.search(r"(?:affected\s*quantity|quantity|qty|quantity\s*affected)\s*(?:is|should be|to|as)?\s*([0-9a-zA-Z\s]+?)(?:\s+and\s+|\s+while\s+|\.|$)", msg_lower)
    if not qty_match:
        qty_match = re.search(r"(?:quantity|qty|affected)\s*(?:is|should be|to|as)?\s*([0-9a-zA-Z\s]+)", msg_lower)
    if qty_match:
        val = qty_match.group(1).strip()
        val = re.sub(r"\s+and\s*$", "", val, flags=re.IGNORECASE).strip()
        updated_fields["quantity_affected"] = val
        updates_detected.append(f"Quantity Affected to **{val}**")

    # Product name
    prod_match = re.search(r"(?:product|product\s*name)\s*(?:is|should be|to|as)\s*([a-zA-Z0-9\s]+?)(?:\s+and\s+|\.|$)", msg_lower)
    if prod_match:
        val = prod_match.group(1).strip()
        updated_fields["product_name"] = val
        updates_detected.append(f"Product Name to **{val}**")

    # Product strength
    strength_match = re.search(r"(?:strength|potency|grade)\s*(?:is|should be|to|as)\s*([a-zA-Z0-9\s/]+?)(?:\s+and\s+|\.|$)", msg_lower)
    if strength_match:
        val = strength_match.group(1).strip()
        updated_fields["product_strength"] = val
        updates_detected.append(f"Product Strength to **{val}**")

    # Complaint source
    source_match = re.search(r"(?:source|complaint\s*source)\s*(?:is|should be|to|as)\s*(email|customer portal|phone call|phone|letter|regulatory agency)", msg_lower)
    if source_match:
        val = source_match.group(1).strip().title()
        if val == "Phone": val = "Phone Call"
        updated_fields["complaint_source"] = val
        updates_detected.append(f"Complaint Source to **{val}**")

    # Initial severity
    sev_match = re.search(r"(?:severity|severe)\s*(?:is|should be|to|as)\s*(critical|major|minor)", msg_lower)
    if sev_match:
        val = sev_match.group(1).strip().capitalize()
        updated_fields["initial_severity"] = val
        updated_fields["priority"] = "High" if val == "Critical" else ("Medium" if val == "Major" else "Low")
        updates_detected.append(f"Initial Severity to **{val}**")

    if updates_detected:
        res_text = f"I have updated the form fields: {', '.join(updates_detected)}. All other complaint information has been preserved."
        return {"response": res_text, "suggested_fields": updated_fields}

    groq_client = get_groq_client()
    if not groq_client:
        if "hello" in msg_lower or "hi" in msg_lower:
            response_text = "Hello! I am your AI QA Intake Assistant. I can extract complaint details from documents, update form fields based on your instructions, or run GMP compliance assessments. How can I help you today?"
        elif "product" in msg_lower or "drug" in msg_lower:
            response_text = f"The current product identified is **{current_fields.get('product_name') or 'Paracetamol'}** (Strength: {current_fields.get('product_strength') or '500mg'})."
        elif "batch" in msg_lower or "lot" in msg_lower:
            response_text = f"The current batch number is **{current_fields.get('batch_number') or 'P1234'}**."
        elif "severity" in msg_lower or "priority" in msg_lower:
            response_text = f"The severity is classified as **{current_fields.get('initial_severity') or 'Major'}** with **{current_fields.get('priority') or 'Medium'}** priority."
        else:
            response_text = "I've reviewed your instruction. You can ask me to update any parameter (e.g. *'Set batch to BMX24602'*, *'Change strength to 250mg'*), or trigger any of the QA assessment tools below."
        return {"response": response_text, "suggested_fields": updated_fields}

    try:
        system_prompt = f"""
        You are an AI Quality Assurance Copilot for a pharmaceutical company.
        You are helping the user manage a customer complaint log.
        Here are the current values of the form fields:
        {json.dumps(current_fields, indent=2)}

        If the user asks to change or update any field, reflect that change in your response using a JSON block enclosed in <update_fields>...</update_fields> tags.
        Example:
        <update_fields>
        {{
          "product_name": "Aspirin",
          "product_strength": "100mg"
        }}
        </update_fields>

        Respond conversationally, referencing GMP guidelines where relevant.
        """
        messages = [{"role": "system", "content": system_prompt}]
        for h in chat_history[-5:]:
            messages.append({"role": h["role"], "content": h["content"]})
        messages.append({"role": "user", "content": message})

        completion = groq_client.chat.completions.create(
            messages=messages,
            model="llama-3.3-70b-versatile",
            temperature=0.3
        )
        res_content = completion.choices[0].message.content
        update_match = re.search(r"<update_fields>(.*?)</update_fields>", res_content, re.DOTALL)
        clean_response = res_content
        if update_match:
            try:
                updates = json.loads(update_match.group(1).strip())
                for k, v in updates.items():
                    if k in updated_fields:
                        updated_fields[k] = v
                clean_response = re.sub(r"<update_fields>.*?</update_fields>", "", res_content, flags=re.DOTALL).strip()
            except Exception:
                pass
        return {"response": clean_response, "suggested_fields": updated_fields}
    except Exception as e:
        print(f"Groq chat failed ({e}), using fallback.")
        return {
            "response": f"Acknowledged. (Operating in fallback mode). You can issue commands like 'batch is BMX24602' or 'strength is 250mg' to modify the form.",
            "suggested_fields": updated_fields
        }


def run_assessment(a_type: str, fields: Dict[str, Any]) -> Dict[str, Any]:
    """Runs a specific QA assessment tool."""
    groq_client = get_groq_client()
    if not groq_client:
        return run_assessment_mock(a_type, fields)

    try:
        model = "llama-3.3-70b-versatile"
        prompt = ""
        if a_type == "completeness":
            prompt = f"Analyze pharmaceutical complaint fields for GMP tracing completeness. Fields: {json.dumps(fields, indent=2)}. Respond in JSON: {{\"completeness_status\": \"Complete\"|\"Incomplete\", \"completeness_feedback\": \"...\"}}"
        elif a_type == "root_cause":
            prompt = f"Recommend 3 root causes under pharma QMS. Product: {fields.get('product_name')}. Description: {fields.get('description')}. Respond in JSON: {{\"root_cause_recommendation\": \"bulleted list\"}}"
        elif a_type == "capa":
            prompt = f"Suggest CAPA plan (Correction, Corrective Action, Preventive Action). Description: {fields.get('description')}. Respond in JSON: {{\"capa_recommendation\": \"...\"}}"
        elif a_type == "risk":
            prompt = f"Classify risk under EU Annex 15 and FDA guidance. Description: {fields.get('description')}. Respond in JSON: {{\"initial_severity\": \"Critical\"|\"Major\"|\"Minor\", \"priority\": \"High\"|\"Medium\"|\"Low\", \"risk_classification_reasoning\": \"...\", \"next_action\": \"...\", \"risk_assessment_details\": \"...\"}}"
        elif a_type == "summary":
            prompt = f"Executive 2-3 sentence QA summary of complaint: {json.dumps(fields, indent=2)}. Respond in JSON: {{\"summary\": \"...\"}}"
        else:
            return run_assessment_mock(a_type, fields)

        completion = groq_client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are a pharma QA Quality System Assessor AI."},
                {"role": "user", "content": prompt}
            ],
            model=model,
            response_format={"type": "json_object"},
            temperature=0.2
        )
        return json.loads(completion.choices[0].message.content)
    except Exception as e:
        print(f"Groq assessment failed ({e}), using mock.")
        return run_assessment_mock(a_type, fields)
