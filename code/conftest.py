import os
import pytest
from dotenv import load_dotenv
from pages.submission_page import SubmissionPage

# Explicitly load .env from the root directory
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", ".env"))

# browser_context_args: Một phần tài nguyên để tạo browser context
@pytest.fixture(scope="session") # session: chỉ chạy 1 lần cho cả project
def browser_context_args(browser_context_args):
    state = os.path.join(os.path.dirname(__file__), "auth", "storage_state.json")
    if os.path.exists(state):
        return {**browser_context_args, "storage_state": state}
    return browser_context_args

# Định vị URL từ env
@pytest.fixture
def target_url():
    return os.getenv("TARGET_URL")


@pytest.fixture
def submission_page(page, target_url):
    """
    Finalized fixture: Initializes, navigates, and CLEANS the SubmissionPage.
    Ensures every test starts with 'No Submission'.
    """
    page_obj = SubmissionPage(page)
    page_obj.navigate(target_url)
    page_obj.cleanup_submission()
    return page_obj
