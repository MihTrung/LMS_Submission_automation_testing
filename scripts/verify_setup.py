import os
import sys
from playwright.sync_api import sync_playwright
from dotenv import load_dotenv

# Path adjustments to allow importing from the 'code' directory
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "code"))
from pages.submission_page import SubmissionPage

# Load environment variables
load_dotenv()

def run_verification():
    """
    A quick manual check to verify that:
    1. The storage_state.json is valid and skipping login.
    2. The SubmissionPage POM locators are working.
    """
    state_path = os.path.join(os.path.dirname(__file__), "..", "code", "auth", "storage_state.json")
    url = os.getenv("TARGET_URL")

    if not os.path.exists(state_path):
        print(f"Error: Storage state not found at {state_path}")
        print("Please run 'python scripts/get_state.py' first.")
        sys.exit(1)

    with sync_playwright() as p:
        print(f"Launching browser to verify setup on: {url}")
        
        # Load the saved state
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(storage_state=state_path)
        page = context.new_page()
        
        # Initialize POM
        submission_page = SubmissionPage(page)
        
        try:
            # 1. Test Navigation
            print("[1/3] Navigating to target URL...")
            submission_page.navigate(url)
            
            # 2. Test Locator Sensitivity (Check if 'Add submission' or 'Submission status' is visible)
            print("[2/3] Checking for key UI elements using POM locators...")
            is_btn_visible = submission_page.add_submission_btn.is_visible(timeout=5000)
            is_table_visible = submission_page.status_table.is_visible(timeout=5000)
            
            if is_btn_visible or is_table_visible:
                print("✅ POM Locators: Successfully identified UI elements.")
            else:
                print("⚠️ POM Locators: Could not find key elements. You might be on the login page or selectors need updating.")

            # 3. Verify Auth State
            print("[3/3] Verifying authentication status...")
            # If we see the submission elements, we are logged in.
            if is_btn_visible or is_table_visible:
                print("✅ Auth State: Login session is ACTIVE.")
            else:
                print("❌ Auth State: Login session seems EXPIRED or INVALID.")

            print("\nVerification complete. Closing browser in 3 seconds...")
            page.wait_for_timeout(3000)

        except Exception as e:
            print(f"\n❌ Verification failed with error: {e}")
        
        finally:
            browser.close()

if __name__ == "__main__":
    run_verification()
