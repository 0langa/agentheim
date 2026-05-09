from ai_team.schemas import VerificationReport, WorkOrder
from ai_team.runtime import _build_fix_work_order


def test_build_fix_work_order_includes_verifier_findings() -> None:
    work_order = WorkOrder(id="wo-1", title="Docs", objective="Update docs", max_edit_scope="README only")
    report = VerificationReport(work_order_id="wo-1", status="failed", failed_checks=["missing section"], fix_requests=["add section"])
    fix = _build_fix_work_order(work_order, report, 1)
    assert fix.id == "wo-1-fix-1"
    assert "add section" in " ".join(fix.required_context_excerpts)