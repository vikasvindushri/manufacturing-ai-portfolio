from pydantic import BaseModel,Field
class GeminiQualityReview(BaseModel):
    executive_summary:str
    missing_evidence:list[str]=Field(default_factory=list)
    root_cause_hypotheses:list[str]=Field(default_factory=list)
    five_why_path:list[str]=Field(default_factory=list)
    corrective_action_candidates:list[str]=Field(default_factory=list)
    risks_and_cautions:list[str]=Field(default_factory=list)
class GeminiTriageReview(BaseModel):
    classification:str
    rationale:str
    likely_causes:list[str]=Field(default_factory=list)
    diagnostic_checks:list[str]=Field(default_factory=list)
    escalation_triggers:list[str]=Field(default_factory=list)
