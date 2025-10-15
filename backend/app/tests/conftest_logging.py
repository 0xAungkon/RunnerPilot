"""
Pytest plugin for test logging and markdown generation (direct Markdown, no JSON).
"""
import pytest
from app.tests.utils.test_logger import save_test_session


def pytest_sessionfinish(session, exitstatus):
    """
    Called after whole test run finished, right before
    returning the exit status to the system.
    """
    # Save the test session summary as Markdown
    try:
        md_report = save_test_session()
        print(f"\n� Test session markdown report saved to: {md_report}")
    except Exception as e:
        print(f"⚠️  Warning: Could not generate test report: {e}")


@pytest.fixture(autouse=True)
def setup_test_logging(request):
    """
    Auto-fixture that runs for every test to set up logging context.
    """
    test_name = request.node.name
    # Any per-test setup can go here
    yield
    # Any per-test cleanup can go here


def pytest_configure(config):
    """
    Called after command line options have been parsed.
    """
    # Add custom markers
    config.addinivalue_line(
        "markers", "api_test: mark test as an API integration test"
    )
    config.addinivalue_line(
        "markers", "logged: mark test to be automatically logged"
    )