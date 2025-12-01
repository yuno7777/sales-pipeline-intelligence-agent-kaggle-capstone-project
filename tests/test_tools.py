# tests/test_tools.py
import tools

def test_research_company():
    r = tools.research_company("Acme Corp")
    assert "company_name" in r
    assert "summary" in r

def test_score_lead():
    out = tools.score_lead("X", 1000, 5)
    assert out["tier"] in ("A","B","C")
    assert isinstance(out["score"], float) or isinstance(out["score"], int)

def test_generate_outreach_no_model():
    r = tools.generate_outreach("Acme", "Alice", "B", model_client=None)
    assert "email" in r
    assert "Acme" in r["email"] or "Alice" in r["email"]
