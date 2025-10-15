import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional, List
import uuid


class TestLogger:
    """
    Logger to capture test execution data including payloads, parameters, and responses.
    Generates a Markdown report directly at the end of the session (no JSON files written).
    """

    def __init__(self, reports_dir: str = "logs/test_reports"):
        # Directory to write final markdown reports
        self.reports_dir = Path(reports_dir)
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        self.test_session_id = str(uuid.uuid4())
        self.test_results: List[Dict[str, Any]] = []
        self._session_saved: bool = False
        self._last_md_path: Optional[str] = None
    
    def log_test_execution(
        self,
        test_name: str,
        method: str,
        endpoint: str,
        payload: Optional[Dict[str, Any]] = None,
        query_params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        response_status: Optional[int] = None,
        response_body: Optional[Dict[str, Any]] = None,
        test_status: str = "PASSED",
        error_message: Optional[str] = None,
        duration_ms: Optional[float] = None
    ):
        """
        Log a single test execution with all relevant data.
        
        Args:
            test_name: Name of the test function
            method: HTTP method (GET, POST, PUT, PATCH, DELETE)
            endpoint: API endpoint being tested
            payload: Request payload/body
            query_params: URL query parameters
            headers: Request headers (sensitive headers will be masked)
            response_status: HTTP response status code
            response_body: Response body
            test_status: Test result (PASSED, FAILED, SKIPPED)
            error_message: Error message if test failed
            duration_ms: Test execution duration in milliseconds
        """
        
        # Mask sensitive headers
        safe_headers = self._mask_sensitive_headers(headers) if headers else None
        
        test_record = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "test_name": test_name,
            "test_status": test_status,
            "session_id": self.test_session_id,
            "duration_ms": duration_ms,
            "request": {
                "method": method,
                "endpoint": endpoint,
                "payload": payload,
                "query_params": query_params,
                "headers": safe_headers
            },
            "response": {
                "status": response_status,
                "body": response_body
            },
            "error_message": error_message
        }
        
        self.test_results.append(test_record)
    
    def _mask_sensitive_headers(self, headers: Dict[str, str]) -> Dict[str, str]:
        """Mask sensitive information in headers"""
        masked_headers = headers.copy()
        sensitive_keys = ["authorization", "cookie", "x-api-key", "token"]
        
        for key in masked_headers:
            if any(sensitive in key.lower() for sensitive in sensitive_keys):
                if masked_headers[key]:
                    masked_headers[key] = f"{masked_headers[key][:8]}***MASKED***"
        
        return masked_headers
    
    def save_session_summary(self) -> str:
        """Generate and save a Markdown summary of all tests in the session.

        Returns:
            The path to the generated Markdown report file (as a string).
        """
        if self._session_saved and self._last_md_path:
            # Idempotent behavior: return existing report path if already generated
            return self._last_md_path
        # Assemble session summary in-memory
        session_summary = {
            "session_id": self.test_session_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "total_tests": len(self.test_results),
            "passed": len([t for t in self.test_results if t.get("test_status") == "PASSED"]),
            "failed": len([t for t in self.test_results if t.get("test_status") == "FAILED"]),
            "skipped": len([t for t in self.test_results if t.get("test_status") == "SKIPPED"]),
            "tests": self.test_results,
        }

        # Generate Markdown content
        md_content = self._generate_session_markdown(session_summary)

        # Persist Markdown file only (no JSON)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        md_filename = f"test_report_{timestamp}.md"
        md_filepath = self.reports_dir / md_filename
        with open(md_filepath, "w") as f:
            f.write(md_content)
        self._session_saved = True
        self._last_md_path = str(md_filepath)
        return self._last_md_path

    # ---------- Markdown generation helpers ----------
    def _generate_session_markdown(self, session_data: Dict[str, Any]) -> str:
        """Generate markdown content for a test session."""
        md_lines: List[str] = [
            f"# Test Execution Report",
            f"",
            f"**Session ID:** `{session_data.get('session_id', 'N/A')}`  ",
            f"**Timestamp:** {session_data.get('timestamp', 'N/A')}  ",
            f"**Total Tests:** {session_data.get('total_tests', 0)}  ",
            f"**Passed:** {session_data.get('passed', 0)}  ",
            f"**Failed:** {session_data.get('failed', 0)}  ",
            f"**Skipped:** {session_data.get('skipped', 0)}  ",
            f"",
            f"## Test Results Summary",
            f"",
        ]

        tests = session_data.get("tests", []) or []
        if tests:
            md_lines.extend(
                [
                    "| Test Name | Status | Method | Endpoint | Response Status | Duration (ms) |",
                    "|-----------|--------|--------|----------|-----------------|---------------|",
                ]
            )

            for test in tests:
                test_name = test.get("test_name", "N/A")
                status = test.get("test_status", "N/A")
                method = (test.get("request") or {}).get("method", "N/A")
                endpoint = (test.get("request") or {}).get("endpoint", "N/A")
                response_status = (test.get("response") or {}).get("status", "N/A")
                duration = test.get("duration_ms", "N/A")

                status_emoji = "✅" if status == "PASSED" else ("❌" if status == "FAILED" else "⏭️")
                md_lines.append(
                    f"| {test_name} | {status_emoji} {status} | {method} | {endpoint} | {response_status} | {duration} |"
                )

        md_lines.extend(["", "## Detailed Test Execution", ""])

        for i, test in enumerate(tests, 1):
            md_lines.extend(self._generate_test_detail_markdown(test, i))

        return "\n".join(md_lines)

    def _generate_test_detail_markdown(self, test_data: Dict[str, Any], test_number: int) -> List[str]:
        """Generate detailed markdown for a single test."""
        test_name = test_data.get("test_name", "N/A")
        status = test_data.get("test_status", "N/A")
        timestamp = test_data.get("timestamp", "N/A")
        duration = test_data.get("duration_ms", "N/A")

        request = test_data.get("request", {}) or {}
        response = test_data.get("response", {}) or {}
        error_message = test_data.get("error_message")

        status_emoji = "✅" if status == "PASSED" else ("❌" if status == "FAILED" else "⏭️")

        lines: List[str] = [
            f"### {test_number}. {test_name} {status_emoji}",
            f"",
            f"**Status:** {status}  ",
            f"**Timestamp:** {timestamp}  ",
            f"**Duration:** {duration} ms  ",
            f"",
            "#### Request",
            f"",
            f"**Method:** `{request.get('method', 'N/A')}`  ",
            f"**Endpoint:** `{request.get('endpoint', 'N/A')}`  ",
        ]

        query_params = request.get("query_params")
        if query_params:
            lines.extend(
                [
                    f"",
                    f"**Query Parameters:**",
                    f"```json",
                    json.dumps(query_params, indent=2),
                    f"```",
                ]
            )

        payload = request.get("payload")
        if payload is not None:
            lines.extend(
                [
                    f"",
                    f"**Request Payload:**",
                    f"```json",
                    json.dumps(payload, indent=2, default=str),
                    f"```",
                ]
            )

        headers = request.get("headers")
        if headers:
            lines.extend(
                [
                    f"",
                    f"**Headers:**",
                    f"```json",
                    json.dumps(headers, indent=2),
                    f"```",
                ]
            )

        lines.extend(
            [
                f"",
                f"#### Response",
                f"",
                f"**Status Code:** `{response.get('status', 'N/A')}`  ",
            ]
        )

        response_body = response.get("body")
        if response_body is not None:
            lines.extend(
                [
                    f"",
                    f"**Response Body:**",
                    f"```json",
                    json.dumps(response_body, indent=2, default=str),
                    f"```",
                ]
            )

        if error_message:
            lines.extend([f"", f"#### Error Details", f"```", str(error_message), f"```"])

        lines.extend([f"", f"---", f""])
        return lines


# Global test logger instance
test_logger = TestLogger()


def log_api_test(
    test_name: str,
    method: str,
    endpoint: str,
    payload: Optional[Dict[str, Any]] = None,
    query_params: Optional[Dict[str, Any]] = None,
    headers: Optional[Dict[str, str]] = None,
    response_status: Optional[int] = None,
    response_body: Optional[Dict[str, Any]] = None,
    test_status: str = "PASSED",
    error_message: Optional[str] = None,
    duration_ms: Optional[float] = None
):
    """
    Convenience function to log API test execution.
    """
    test_logger.log_test_execution(
        test_name=test_name,
        method=method,
        endpoint=endpoint,
        payload=payload,
        query_params=query_params,
        headers=headers,
        response_status=response_status,
        response_body=response_body,
        test_status=test_status,
        error_message=error_message,
        duration_ms=duration_ms
    )


def save_test_session():
    """Save the current test session summary as Markdown and return its path."""
    return test_logger.save_session_summary()