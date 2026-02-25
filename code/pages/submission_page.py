import os
import re
from playwright.sync_api import Page, expect

class SubmissionPage:
    """
    Encapsulates the LMS Assignment Submission page actions and locators.
    Updated with real selectors from codegen.py for lms.uel.edu.vn.
    """
    def __init__(self, page: Page):
        self.page = page
        
        # Locators from codegen.py
        self.add_submission_btn = page.get_by_role("button", name="Thêm bài nộp")
        self.add_file_btn = page.get_by_role("button", name="Thêm...")
        self.file_input_field = page.get_by_role("textbox", name="Đính kèm")
        self.save_as_field = page.get_by_role("textbox", name="Lưu thành")
        self.upload_this_file_btn = page.get_by_role("button", name="Đăng tải tệp này")
        self.save_changes_btn = page.get_by_role("button", name="Lưu những thay đổi")
        # Final surgical locator: target standard ID or form-footer elements, excluding file picker
        self.cancel_btn = page.locator("#id_cancel, [name='cancel']").or_(
            page.locator(".form-buttons, .fitem, .submission-form").locator("a:visible, button:visible").filter(
                has_text=re.compile(r"Hủy|Huỷ|Cancel", re.I)
            )
        ).filter(has_not=page.locator("[class*='fp-']"))
        
        # New Locators from User Findings
        self.edit_submission_btn = page.get_by_role("button", name="Sửa bài nộp")
        self.remove_submission_btn = page.get_by_role("button", name="Loại bỏ bài nộp")
        self.confirm_remove_btn = page.get_by_role("button", name="Tiếp tục")
        
        # New Locators from User Codegen
        self.overwrite_rename_btn = page.get_by_role("button", name="Đặt tên thành")
        self.error_dialog = page.locator(".moodle-dialogue-base")
        self.create_folder_btn = page.get_by_role("button", name="Tạo thư mục")
        
        # Status & Success Locators
        self.status_table = page.locator(".submissionstatustable")
        self.success_indicator = page.get_by_text("Đã nộp để chấm điểm") # Based on Vietnamese UI
        self.login_error_box = page.locator(".alert-danger, #loginerrormessage")

    def navigate(self, url: str):
        """Navigates directly to the assignment page and checks session."""
        self.page.goto(url)
        self.page.wait_for_load_state("networkidle")
        self.check_session()

    def check_session(self):
        """Checks if the session is still valid or redirected to login."""
        if "login/index.php" in self.page.url:
            # Use .first to avoid strict mode violation if multiple error elements exist
            error_loc = self.login_error_box.first
            error_text = error_loc.inner_text() if error_loc.is_visible() else "Unknown login error"
            print(f"Auth Failure: Redirected to login page. Current URL: {self.page.url}")
            print(f"Login Error Message: {error_text}")
            raise Exception(f"Authentication Session Expired or Invalid. Please run 'python scripts/get_state.py' to re-authenticate. Details: {error_text}")

    def cleanup_submission(self):
        """
        Aggressively ensures a clean state by removing any existing submission using target locators.
        """
        self.page.wait_for_load_state("networkidle")
        
        try:
            if self.remove_submission_btn.is_visible(timeout=3000):
                print("Cleanup: Detected existing submission ('Loại bỏ bài nộp'). Removing...")
                self.remove_submission_btn.click()
                
                # Moodle confirmation page
                self.confirm_remove_btn.wait_for(state="visible", timeout=5000)
                self.confirm_remove_btn.click()
                
                self.page.wait_for_load_state("load")
                print("Cleanup: Existing submission removed.")
            else:
                print("Cleanup: No 'Loại bỏ bài nộp' button found. State is likely clean.")
        except Exception as e:
            print(f"Cleanup: Warning - Error during state reset: {e}")

    def start_submission(self):
        """Clicks 'Thêm bài nộp' or 'Sửa bài nộp' (if in draft)."""
        btn = self.add_submission_btn.or_(self.edit_submission_btn)
        btn.wait_for(state="visible", timeout=5000)
        btn.click()

    def upload_file(self, file_path: str, save_as_name: str = "", handle_conflict: bool = True):
        """
        Handles the complex file upload flow:
        1. Click 'Thêm...' (Add)
        2. Wait for the upload dialog
        3. Set file in the file input
        4. Optional: Fill 'Lưu thành' (Save as)
        5. Click 'Đăng tải tệp này' (Upload this file)
        6. Handle conflict if requested (Rename/Overwrite)
        """
        self.add_file_btn.click()
        
        # Wait for the file picker modal to be ready
        file_input = self.page.locator("input[type='file']")
        file_input.wait_for(state="visible", timeout=5000)
        file_input.set_input_files(file_path)
        
        if save_as_name:
            self.save_as_field.fill(save_as_name)
            
        self.upload_this_file_btn.click(timeout=120000) # Wait up to 2 min for upload trigger
        
        # Wait for the processing modal to disappear
        # In Moodle, the '.moodle-dialogue-base' with the file picker usually disappears
        try:
            self.page.locator(".moodle-dialogue-base:visible").wait_for(state="hidden", timeout=10000)
        except:
            pass # Might still be visible if an error or conflict appeared
            
        # Handle Rename/Overwrite modal if it appears (conflict)
        try:
            if handle_conflict and self.overwrite_rename_btn.first.is_visible(timeout=5000):
                self.overwrite_rename_btn.first.click()
                self.page.wait_for_load_state("networkidle")
        except:
            pass 

    def get_error_message(self, filename: str) -> str:
        """
        Returns error text if a file upload fails. 
        Waits up to 30s for server rejection on large files.
        """
        quoted_filename = re.escape(filename)
        error_regex = re.compile(f"The file ['\"]?{quoted_filename}['\"]?", re.IGNORECASE)
        
        # 1. Look for the error text anywhere on the page (Global search)
        # This is more robust than scoping to dialogs initially
        try:
            error_loc = self.page.get_by_text(error_regex).last
            error_loc.wait_for(state="visible", timeout=30000)
            return error_loc.inner_text()
        except:
            pass
        
        # 2. Fallback to general visible error notification containers
        try:
            notif_loc = self.page.locator(".moodle-exception, .fp-error, .moodle-dialogue-base:visible").last
            if notif_loc.is_visible(timeout=5000):
                return notif_loc.inner_text()
        except:
            pass
            
        return ""

    def close_error_dialog(self):
        """Clicks 'Đóng' or 'OK' on the TOPMOST Moodle error popup."""
        ok_btn = self.page.locator(".moodle-dialogue-base:visible").last.get_by_role("button", name="Đóng").or_(
                 self.page.locator(".moodle-dialogue-base:visible").last.get_by_role("button", name="Xác nhận")).or_(
                 self.page.locator(".moodle-dialogue-base:visible").last.get_by_role("button", name="OK"))
        
        if ok_btn.is_visible(timeout=3000):
            ok_btn.click()
            print("Cleanup: Topmost error dialog closed.")

    def is_at_file_limit(self) -> bool:
        """Verifies limit reached by checking if 'Thêm...' button is hidden."""
        try:
            # Check for hidden state which is more reliable than checking for the folder button
            self.add_file_btn.wait_for(state="hidden", timeout=5000)
            return True
        except:
            return False

    def confirm_submission(self):
        """Clicks 'Lưu những thay đổi' (Save changes) to finalize the submission."""
        self.save_changes_btn.click()

    def cancel_submission(self):
        """Clicks 'Hủy' (Cancel) to return to status page without saving."""
        # Wait for settling
        self.page.wait_for_timeout(2000)
        btn = self.cancel_btn.last
        btn.wait_for(state="visible", timeout=5000)
        btn.click(force=True)
        # Wait for the status table to appear
        self.status_table.wait_for(state="visible", timeout=10000)

    def is_submission_successful(self) -> bool:
        """Verifies if the status indicates successful submission."""
        return self.success_indicator.is_visible()

    def get_status_text(self) -> str:
        """Returns the full text of the submission status table."""
        return self.status_table.inner_text()
