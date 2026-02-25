import os
import sys
from playwright.sync_api import sync_playwright
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_auth_state():
    """
    Launches a browser for manual login and saves the storage state.
    """
    # Ensure the auth directory exists
    auth_dir = os.path.join(os.path.dirname(__file__), "..", "code", "auth")
    os.makedirs(auth_dir, exist_ok=True)
    state_path = os.path.join(auth_dir, "storage_state.json")

    url = os.getenv("TARGET_URL")
    # If the URL is a deep link, we might want to go to the base domain for login
    # but usually navigating to the target triggers the login redirect anyway.
    if not url:
        print("Error: TARGET_URL not found in .env file.")
        sys.exit(1)

    with sync_playwright() as p:
        print(f"Opening browser to: {url}")
        print("Please log in manually in the opened browser window.")
        
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        
        page.goto(url)

        print("\nWaiting for you to log in...")
        print("Close the browser window ONCE YOU ARE LOGGED IN to save the state.")
        
        # Keep the script running until the browser is closed manually by the user
        browser.on("disconnected", lambda _: None)
        
        # Logic to wait until the user is done
        # We can detect a URL change or just wait for the browser to close
        while True:
            if page.is_closed():
                break
            try:
                page.wait_for_timeout(1000)
            except:
                break

        # Save the state
        context.storage_state(path=state_path)
        print(f"\n[SUCCESS] Authentication state saved to: {state_path}")
        browser.close()

if __name__ == "__main__":
    get_auth_state()
