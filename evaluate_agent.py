import os
import sys

# Mock environment variables to ensure independence
os.environ["GOOGLE_API_KEY"] = "dummy_key"
os.environ["GEMINI_MODEL"] = "dummy_model"

try:
    from agent import Coordinator_run
except ImportError:
    print("Error: Could not import Coordinator_run from agent.py")
    sys.exit(1)
except RuntimeError as e:
    print(f"Error during import: {e}")
    sys.exit(1)

def run_evaluation():
    test_cases = [
        {"company": "TechNova", "contact": "Sarah"},
        {"company": "GreenEnergy", "contact": "Mike"},
        {"company": "QuantumSoft", "contact": "Jen"}
    ]

    print(f"{'Company':<15} | {'Contact':<10} | {'Status':<10} | {'Validation':<10}")
    print("-" * 55)

    for case in test_cases:
        company = case["company"]
        contact = case["contact"]
        
        try:
            result = Coordinator_run(company, contact)
            
            # Verify structure
            has_session = "session_id" in result
            has_research = "research_results" in result
            has_outreach = "outreach_results" in result
            
            status = "PASS" if (has_session and has_research and has_outreach) else "FAIL"
            
            # Check validation
            outreach = result.get("outreach_results", {}).get("outreach", {})
            validation_status = outreach.get("validation_status", "unknown")
            
            print(f"{company:<15} | {contact:<10} | {status:<10} | {validation_status:<10}")
            
        except Exception as e:
            print(f"{company:<15} | {contact:<10} | ERROR      | {str(e)}")

if __name__ == "__main__":
    run_evaluation()
