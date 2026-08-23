from shared.config import load_config
from shared.validation import validate_quality,validate_fault,validate_query
from shared.history import add_history,save_draft,load_draft
from shared.audit import audit_event

def test_profiles_load():
    assert load_config("local").gemini_enabled is False
    assert load_config("gemini").gemini_enabled is True

def test_form_validation():
    _,q=validate_quality({});_,f=validate_fault({});_,k=validate_query("x")
    assert q and f and k

def test_history_and_draft():
    s={};save_draft(s,"quality",{"id":1});assert load_draft(s,"quality")["id"]==1
    add_history(s,"quality",{"id":1},1);add_history(s,"fault",{"id":2},1);assert len(s["history"])==1

def test_audit_redacts_sensitive(tmp_path,monkeypatch):
    import shared.audit as a
    monkeypatch.setattr(a,"ROOT",tmp_path)
    e=a.audit_event("test","quality",metadata={"owner":"A","count":1},path="audit.jsonl")
    assert e["metadata"]["owner"]=="[REDACTED]" and (tmp_path/"audit.jsonl").exists()
