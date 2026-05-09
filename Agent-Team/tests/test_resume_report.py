import json

from ai_team.reports.final_report import FinalReport
from ai_team.resume import list_runs, load_final_report, load_run


def test_resume_and_report_loading(tmp_path) -> None:
    run_dir = tmp_path / ".ai-team" / "runs" / "run-1"
    run_dir.mkdir(parents=True)
    (run_dir / "run.json").write_text(json.dumps({"action": "run", "task": "x"}), encoding="utf-8")
    report = FinalReport(task_summary="x", run_id="run-1")
    (run_dir / "final_report.json").write_text(report.model_dump_json(), encoding="utf-8")

    assert list_runs(tmp_path) == ["run-1"]
    assert load_run(tmp_path, "run-1")["task"] == "x"
    assert load_final_report(tmp_path, "run-1").task_summary == "x"
