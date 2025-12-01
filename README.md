# Sales Pipeline Agent

The **Sales Pipeline Agent** is an enterprise-focused AI system that automates the early stages of sales operations.  
It performs company research, lead scoring, and outreach drafting using a combination of deterministic tools and controlled LLM-based refinement.  
This project was built using the `google.adk` framework and Gemini models, with a focus on reliability, interpretability, and production-friendly behavior.

---

## How It Works

The agent follows a three-step workflow that mirrors real sales development processes:

1. **Company Research**  
   The agent gathers basic firmographic information such as industry, employee count, and company stage. A deterministic mock provides consistent test data, and an optional enrichment adapter can add real external data when enabled.

2. **Lead Scoring**  
   Based on employee count and intent, the agent computes a numerical score and assigns a tier (A, B, or C). This ensures lead prioritization is consistent and repeatable.

3. **Outreach Generation**  
   The agent drafts an outreach email tailored to the company and contact. If enabled, Gemini is used to refine tone and clarity while respecting strict safety constraints (no adding facts, no assumptions).

A built-in validation step ensures emails meet structural requirements. If validation fails, the system attempts a repair and ultimately falls back to a deterministic message if needed.

---

## Key Features

- **Deterministic + LLM Hybrid Design**
  - Predictable tool-driven logic for research and scoring.
  - Optional Gemini polish for more natural outreach emails.

- **Data Safety**
  - PII scrubbing ensures outputs are clean and safe to store or log.
  - Strict instructions prevent hallucinated details or invented company facts.

- **Extension-Friendly Architecture**
  - Easily add additional enrichment APIs, custom scoring rules, outreach templates, or CRM integrations.

- **Test Coverage**
  - Includes unit tests for major components to ensure reliability across updates.

---

## Project Structure

sales_pipeline_agent/
    agent.py             # Main agent definition and tool registration
    tools.py             # Company research, scoring, outreach, validation logic
    config.py            # Environment variable configuration
    utils.py             # Logging, safety, and helper functions
    session_manager.py   # In-memory session handling
    observability.py     # Timing + structured logging utilities
    evaluate_agent.py    # Lightweight evaluation harness
    tests/               # Unit and workflow tests

---

## Setup

1. **Clone the repository**
   - git clone [<Sales-Pipeline-Intelligence-Agent>](https://github.com/yuno7777/sales-pipeline-intelligence-agent-kaggle-capstone-project/tree/main)
   - cd sales_pipeline_agent

2. **Create and activate a virtual environment**
   - python -m venv venv
   - Windows: venv\Scripts\activate
   - macOS/Linux: source venv/bin/activate

3. **Install dependencies**
   - pip install -r requirements.txt

4. **Configure environment variables**
   - Create a `.env` or export manually:
     - GOOGLE_API_KEY="your_api_key"
     - GEMINI_MODEL="gemini-2.5-flash"
     - ENABLE_ENRICHMENT="false"
     - ENRICHMENT_API_KEY=""

---

## Running the Agent

**Option 1: Direct ADK Runtime Execution (conceptual)**
- from agent import root_agent
- from google.adk.runtime import run_agent
- query = "Research Acme Corp and draft an email to Sarah."
- response = run_agent(root_agent, query)
- print(response)

**Option 2: Programmatic Flow (Procedural Pipeline)**
- from agent import Coordinator_run
- result = Coordinator_run("Acme Corp", "Sarah Thompson")
- print(result)

The procedural pipeline is fast and deterministic; use it for batch processing or evaluation.

---

## Running the Agent in ADK Web UI

### Introduction
The ADK Web UI provides a visual interface for interacting with and debugging your agent. It allows you to:
- **Chat** with the agent in a user-friendly environment.
- **Inspect** tool calls, arguments, and outputs in real-time.
- **Trace** execution flows for debugging and evaluation.

### Setup & Run

1. **Navigate to the project root**:
   ```bash
   cd sales_pipeline_agent
   ```

2. **Launch the Web UI**:
   ```bash
   adk web .
   ```
   *Alternatively:* `adk web sales_pipeline_agent` (if running from the parent directory).

3. **Open the Interface**:
   Visit [http://127.0.0.1:8000/dev-ui/](http://127.0.0.1:8000/dev-ui/) in your browser.

**Expected Behavior:**
- The "Sales Pipeline Agent" should appear in the agent dropdown.
- You can type messages like "Research Acme Corp".
- The side panel will show tool execution details (e.g., `research_company`, `score_lead`).

### Project Structure Requirements
ADK loads agents from folders that contain:
- An `__init__.py` file (marks it as a package).
- An `__adk__.yaml` file (defines metadata and the root agent).
- An exported `root_agent` object in the specified module.

**Example Structure:**
```text
sales_pipeline_agent/
    __init__.py
    __adk__.yaml      <-- Critical for ADK loading
    agent.py          <-- Contains 'root_agent'
    tools.py
    ...
```

## Example Output (representative)

{
  "session_id": "uuid",
  "research": {
    "company_name": "Acme Corp",
    "industry": "SaaS",
    "employee_count_est": 500,
    "summary": "Acme Corp operates in the SaaS sector..."
  },
  "outreach": {
    "score": 12.5,
    "tier": "A",
    "email": "Hi Sarah, ...",
    "validation_status": "valid"
  }
}

Exact output varies depending on whether enrichment or Gemini polishing is enabled.

---

## Testing

Run all tests:

- python -m unittest discover tests

Included tests cover:
- Research logic
- Lead scoring
- Outreach generation
- Validation and safety checks
- End-to-end Coordinator workflow

---

## Evaluation Script (Optional)

An included script `evaluate_agent.py` runs sample scenarios and prints a structured evaluation of:
- Research output presence
- Scoring behavior
- Email generation quality
- Validation and fallback correctness

Run with:

- python evaluate_agent.py

---

## Extending This Project

- **Real-world enrichment:** Integrate Clearbit, Apollo, Crunchbase, or internal datasets.
- **Deployment:** Wrap as a FastAPI service and deploy via Cloud Run.
- **Parallelization:** Add parallel or loop agents to handle bulk lead lists.
- **Persistent memory:** Replace in-memory sessions with Redis, Firestore, or Postgres for long-term state.

---

## Security & Privacy Notes

- Do not commit API keys or secrets to version control.
- PII scrubbing is implemented for outputs, but you should verify compliance with your organization's policies before storing or sharing generated content.
- The LLM is restricted from inventing company facts via guardrails; however, always include human review before sending production outreach.

---

### Configuration Requirements
Ensure your environment variables are set. ADK automatically loads `.env` files located inside the agent directory.

**Required Variables:**
```bash
export GOOGLE_API_KEY="your_api_key"
```

### Troubleshooting

| Issue | Cause | Fix |
| :--- | :--- | :--- |
| **Agent not in dropdown** | ADK cannot find the agent definition. | Ensure `__adk__.yaml` exists and `root_agent` path is correct (`agent:root_agent`). |
| **"No root_agent found"** | Running `adk web` from the wrong folder. | Run `adk web .` from *inside* the `sales_pipeline_agent` folder. |
| **Port 8000 in use** | Another process is using the port. | Kill the process or run on a different port: `adk web . --port 8001`. |
| **Tool calls missing** | Import errors or missing dependencies. | Check the terminal logs for `ModuleNotFoundError` and install missing packages. |

---

## License

This project is provided for educational and demonstration purposes.


