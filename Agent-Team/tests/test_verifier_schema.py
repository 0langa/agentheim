from ai_team.schemas import VerificationReport


def test_verification_report_accepts_camel_case() -> None:
    report = VerificationReport.model_validate(
        {
            "workOrderId": "wo-1",
            "status": "passed",
            "commandsRun": [["python", "-m", "pytest"]],
            "passedChecks": ["docs updated"],
            "failedChecks": [],
            "diffFindings": [],
            "missingTests": [],
            "regressions": [],
            "securityConcerns": [],
            "performanceConcerns": [],
            "fixRequests": [],
            "finalSummary": "ok",
        }
    )
    assert report.work_order_id == "wo-1"