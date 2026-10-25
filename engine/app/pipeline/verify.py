# For: Verification stage comparing extracted fields against submitted biodata
# Must never: Execute verification without logging mismatch reasons

from typing import Any
from engine.app.core.config import settings
from engine.app.pipeline.context import PipelineContext, ExtractedFieldData
from engine.app.rules.validation import verify_field_value


def lookup_biodata_value(field_name: str, biodata: dict[str, Any]) -> str | None:
    """Finds matching expected value from hierarchical biodata dictionary."""
    if field_name in biodata and biodata[field_name] is not None:
        return str(biodata[field_name])
    
    qual = biodata.get("qualification", {})
    if isinstance(qual, dict) and field_name in qual and qual[field_name] is not None:
        return str(qual[field_name])
    
    gate = biodata.get("gate", {})
    if isinstance(gate, dict) and field_name in gate and gate[field_name] is not None:
        return str(gate[field_name])
    
    return None


def run_verify_stage(ctx: PipelineContext) -> PipelineContext:
    """Compare extracted field values against expected application biodata.
    
    Input: Extracted fields and applicant biodata.
    Output: Verified fields marked with status, confidence, and alerts.
    Time budget: 0.1 seconds.
    """
    if not ctx.biodata:
        return ctx
    
    for field in ctx.fields:
        expected = lookup_biodata_value(field.name, ctx.biodata)
        field.expected = expected
        if not expected or not field.extracted:
            field.status = "not_found"
            field.confidence = 0.50
            continue
        
        status, conf, reason = verify_field_value(field.name, field.extracted, expected)
        field.status = status
        field.confidence = conf
        field.reason = reason
        
        # Three Sigma auto-accept criteria
        if status == "match" and conf >= settings.auto_accept_threshold:
            field.auto_accepted = True
        else:
            field.auto_accepted = False
            
        if status == "mismatch":
            alert_msg = f"{field.name.replace('_', ' ').title()}: entered '{expected}' but document shows '{field.extracted}'."
            ctx.alerts.append(alert_msg)
            
    return ctx
