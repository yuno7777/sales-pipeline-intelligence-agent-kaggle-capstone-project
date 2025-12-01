# agent.py
from google.adk.agents import LlmAgent
from google.adk.models.google_llm import Gemini
from google.genai import types
import config, utils, tools

# runtime checks
utils.require_env("GOOGLE_API_KEY", config.GEMINI_API_KEY)

# configure retry for model
retry_config = types.HttpRetryOptions(
    attempts=5, exp_base=7, initial_delay=1,
    http_status_codes=[429, 500, 503, 504]
)

# instantiate Gemini model (ADK wrapper)
model = Gemini(model=config.MODEL_NAME, retry_options=retry_config)

# Provide a safe instruction set - constrain behavior to tool usage
instruction = """
You are a Sales Pipeline Agent. You must:
- Ask clarifying questions when user input lacks required fields.
- Always prefer calling the matching tool (research_company, score_lead, generate_outreach).
- Never fabricate facts beyond the tool outputs.
- When polishing emails, do not add company-specific factual claims.
- Keep outputs concise and structured in JSON when asked.
"""

# expose the tools but wrap generate_outreach to pass model if desired
def generate_outreach_wrapper(company_name: str, contact_name: str, tier: str) -> dict:
    # pass model for polish, but keep failure-safe fallback
    return tools.generate_outreach(company_name, contact_name, tier, model_client=model)

root_agent = LlmAgent(
    model=model,
    name="sales_pipeline_agent",
    description="Enterprise-grade Sales Pipeline assistant.",
    instruction=instruction,
    tools=[tools.research_company, tools.score_lead, generate_outreach_wrapper],
)

# --- Procedural Workflow Extensions ---
from session_manager import InMemorySessionService

# Single instance of session service
session_service = InMemorySessionService()

def summarize_lead(research_data: dict) -> str:
    """Helper to summarize research data."""
    return (
        f"Company: {research_data.get('company_name')}\n"
        f"Industry: {research_data.get('industry')}\n"
        f"Stage: {research_data.get('stage')}\n"
        f"Employees: {research_data.get('employee_count_est')}\n"
        f"Summary: {research_data.get('summary')}"
    )

def ResearchAgent(company_name: str, session_id: str) -> dict:
    """
    Procedural agent for research.
    Calls research_company + summarize_lead.
    Saves results to session.
    """
    # 1. Research
    research_data = tools.research_company(company_name)
    
    # 2. Summarize
    summary = summarize_lead(research_data)
    research_data["lead_summary"] = summary
    
    # 3. Save to session
    session_service.update_session(session_id, {"research": research_data})
    
    return research_data

def validate_email(email: str) -> bool:
    """Simple validation helper."""
    if not email or len(email) < 10:
        return False
    if "@" not in email: # Very basic check
        return False
    return True

def OutreachAgent(company_name: str, contact_name: str, session_id: str) -> dict:
    """
    Procedural agent for outreach.
    Loads research -> Scoring -> Outreach -> Validation -> Explanation.
    Saves results to session.
    """
    # 1. Load research from session
    session = session_service.get_session(session_id)
    if not session or "research" not in session["state"]:
        raise ValueError(f"No research data found for session {session_id}")
    
    research_data = session["state"]["research"]
    employee_count = research_data.get("employee_count_est", 0)
    
    # 2. Scoring
    intent_score = 5 
    score_data = tools.score_lead(company_name, employee_count, intent_score)
    
    # 3. Outreach Generation (Initial Attempt)
    outreach_data = tools.generate_outreach(company_name, contact_name, score_data["tier"], model_client=None)
    email_content = outreach_data.get("email", "")
    
    # 4. Validation & Repair Loop
    is_valid = validate_email(email_content)
    
    if not is_valid:
        # Attempt Repair (Single Cycle)
        # Try using the model to fix it if available, or just re-generate
        # Since we want a "repair", let's try the model-polished version as the repair strategy
        # This aligns with "repair should try either a model-polished rewrite..."
        outreach_data = tools.generate_outreach(company_name, contact_name, score_data["tier"], model_client=model)
        email_content = outreach_data.get("email", "")
        is_valid = validate_email(email_content)
        
        if not is_valid:
            # Fallback to safe deterministic variant
            email_content = (
                f"Hi {contact_name},\n\n"
                f"Checking in regarding {company_name}. We have some updates that might interest you.\n\n"
                "Best,\nSales Team"
            )
            outreach_data["email"] = email_content
            outreach_data["validation_status"] = "fallback"
        else:
            outreach_data["validation_status"] = "repaired"
    else:
        outreach_data["validation_status"] = "valid"

    # 5. Explanation
    outreach_data["score_explanation"] = (
        f"Score {score_data['score']} (Tier {score_data['tier']}) based on "
        f"{employee_count} employees and intent {intent_score}."
    )
    
    # 6. Save to session
    result = {
        "score": score_data,
        "outreach": outreach_data
    }
    session_service.update_session(session_id, result)
    
    return result

def Coordinator_run(company_name: str, contact_name: str) -> dict:
    """
    Coordinator function.
    Creates session -> ResearchAgent -> OutreachAgent.
    Returns structured dict.
    """
    # 1. Create Session
    import uuid
    session_id = str(uuid.uuid4())
    session_service.create_session(session_id)
    
    # 2. Run ResearchAgent
    research_results = ResearchAgent(company_name, session_id)
    
    # 3. Run OutreachAgent
    outreach_results = OutreachAgent(company_name, contact_name, session_id)
    
    return {
        "session_id": session_id,
        "research_results": research_results,
        "outreach_results": outreach_results
    }

if __name__ == "__main__":
    import json
    print("Sales Pipeline Agent - Demo Run")
    print("-------------------------------")
    try:
        # Example run
        result = Coordinator_run("Acme Corp", "Alice")
        print(json.dumps(result, indent=2))
        print("\n[Success] Agent workflow completed.")
    except Exception as e:
        print(f"\n[Error] Agent workflow failed: {e}")

