import os
import re
import html
import requests
import customtkinter as ctk
import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException
from tkinter import messagebox


# ============================================================
# CONFIGURATION
# ============================================================

APP_TITLE = "NDMU Notification Console"

BREVO_API_KEY = os.getenv("BREVO_API_KEY", "")
SENDER_EMAIL = os.getenv(
    "BREVO_SENDER_EMAIL",
    "your-email@example.com"
)
SENDER_NAME = os.getenv(
    "BREVO_SENDER_NAME",
    "NDMU Notification"
)

# SMS sender name
SMS_SENDER = os.getenv(
    "BREVO_SMS_SENDER",
    "NDMU"
)


# ============================================================
# APPEARANCE
# ============================================================

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("green")


# ============================================================
# APPLICATION
# ============================================================

class NotificationApp(ctk.CTk):

    def __init__(self):
        super().__init__()

        # Window settings
        self.title(APP_TITLE)
        self.geometry("620x700")
        self.resizable(False, False)

        # Colors
        self.bg_color = "#101010"
        self.card_color = "#181818"
        self.input_color = "#242424"
        self.text_color = "#F2F2F7"
        self.secondary_text = "#8E8E93"
        self.success_color = "#30D158"

        self.configure(fg_color=self.bg_color)

        self.create_widgets()

        # Set initial field to Email
        self.update_recipient_field("Email")

    # ========================================================
    # GUI
    # ========================================================

    def create_widgets(self):

        # ----------------------------------------------------
        # Header
        # ----------------------------------------------------

        header_frame = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )
        header_frame.pack(
            fill="x",
            padx=30,
            pady=(25, 10)
        )

        title = ctk.CTkLabel(
            header_frame,
            text="NDMU Notification Console",
            font=ctk.CTkFont(
                family="Inter",
                size=24,
                weight="bold"
            ),
            text_color=self.text_color
        )
        title.pack(anchor="w")

        subtitle = ctk.CTkLabel(
            header_frame,
            text="Multi-channel notification system",
            font=ctk.CTkFont(size=13),
            text_color=self.secondary_text
        )
        subtitle.pack(
            anchor="w",
            pady=(3, 0)
        )

        # ----------------------------------------------------
        # Input Card
        # ----------------------------------------------------

        input_card = ctk.CTkFrame(
            self,
            corner_radius=14,
            fg_color=self.card_color
        )
        input_card.pack(
            fill="x",
            padx=30,
            pady=10
        )

        # ----------------------------------------------------
        # Channel
        # ----------------------------------------------------

        channel_label = ctk.CTkLabel(
            input_card,
            text="Notification Channel",
            font=ctk.CTkFont(
                size=13,
                weight="bold"
            ),
            text_color=self.text_color
        )
        channel_label.pack(
            anchor="w",
            padx=18,
            pady=(18, 6)
        )

        self.channel_var = ctk.StringVar(
            value="Email"
        )

        self.channel_dropdown = ctk.CTkOptionMenu(
            input_card,
            values=[
                "Email",
                "SMS",
                "Push Notification"
            ],
            variable=self.channel_var,
            width=250,
            height=38,
            corner_radius=8,
            command=self.on_channel_change
        )
        self.channel_dropdown.pack(
            anchor="w",
            padx=18,
            pady=(0, 15)
        )

        # ----------------------------------------------------
        # Message
        # ----------------------------------------------------

        message_label = ctk.CTkLabel(
            input_card,
            text="Message",
            font=ctk.CTkFont(
                size=13,
                weight="bold"
            ),
            text_color=self.text_color
        )
        message_label.pack(
            anchor="w",
            padx=18,
            pady=(0, 6)
        )

        self.message_entry = ctk.CTkTextbox(
            input_card,
            height=90,
            corner_radius=8,
            fg_color=self.input_color,
            border_width=0,
            font=ctk.CTkFont(size=13)
        )
        self.message_entry.pack(
            fill="x",
            padx=18,
            pady=(0, 15)
        )

        # ----------------------------------------------------
        # Recipient Label
        # ----------------------------------------------------

        self.recipient_label = ctk.CTkLabel(
            input_card,
            text="Recipient Email",
            font=ctk.CTkFont(
                size=13,
                weight="bold"
            ),
            text_color=self.text_color
        )
        self.recipient_label.pack(
            anchor="w",
            padx=18,
            pady=(0, 6)
        )

        # ----------------------------------------------------
        # Recipient Entry
        # ----------------------------------------------------

        self.recipient_entry = ctk.CTkEntry(
            input_card,
            height=40,
            corner_radius=8,
            fg_color=self.input_color,
            border_width=0,
            font=ctk.CTkFont(size=13)
        )
        self.recipient_entry.pack(
            fill="x",
            padx=18,
            pady=(0, 18)
        )

        # ----------------------------------------------------
        # Buttons
        # ----------------------------------------------------

        button_frame = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )
        button_frame.pack(
            fill="x",
            padx=30,
            pady=5
        )

        self.send_btn = ctk.CTkButton(
            button_frame,
            text="Send Notification",
            height=40,
            width=180,
            corner_radius=8,
            font=ctk.CTkFont(
                size=13,
                weight="bold"
            ),
            command=self.on_send
        )
        self.send_btn.pack(
            side="left",
            padx=(0, 10)
        )

        self.clear_btn = ctk.CTkButton(
            button_frame,
            text="Clear Log",
            height=40,
            width=110,
            corner_radius=8,
            fg_color="#2C2C2E",
            hover_color="#3A3A3C",
            text_color="#E5E5EA",
            command=self.on_clear
        )
        self.clear_btn.pack(
            side="left"
        )

        # ----------------------------------------------------
        # Delivery Log
        # ----------------------------------------------------

        log_frame = ctk.CTkFrame(
            self,
            corner_radius=14,
            fg_color=self.card_color
        )
        log_frame.pack(
            fill="both",
            expand=True,
            padx=30,
            pady=(15, 10)
        )

        log_label = ctk.CTkLabel(
            log_frame,
            text="Delivery Log",
            font=ctk.CTkFont(
                size=13,
                weight="bold"
            ),
            text_color=self.success_color
        )
        log_label.pack(
            anchor="w",
            padx=18,
            pady=(15, 7)
        )

        self.log_text = ctk.CTkTextbox(
            log_frame,
            font=ctk.CTkFont(
                family="Consolas",
                size=11
            ),
            fg_color="#0C0C0C",
            text_color="#30D158",
            corner_radius=8,
            border_width=0
        )
        self.log_text.pack(
            fill="both",
            expand=True,
            padx=18,
            pady=(0, 18)
        )

        # ----------------------------------------------------
        # Footer
        # ----------------------------------------------------

        footer = ctk.CTkLabel(
            self,
            text="NDMU Notification System • Email + SMS",
            font=ctk.CTkFont(size=11),
            text_color="#636366"
        )
        footer.pack(
            pady=(0, 15)
        )

    # ========================================================
    # CHANNEL CHANGE
    # ========================================================

    def on_channel_change(self, selected_channel):

        self.update_recipient_field(selected_channel)

        if selected_channel == "Email":
            self.add_log(
                "[SYSTEM] Email channel selected."
            )

        elif selected_channel == "SMS":
            self.add_log(
                "[SYSTEM] SMS channel selected."
            )

        elif selected_channel == "Push Notification":
            self.add_log(
                "[SYSTEM] Push Notification selected."
            )

    # ========================================================
    # RECIPIENT FIELD SWITCHING
    # ========================================================

    def update_recipient_field(self, channel):

        # Clear current recipient
        self.recipient_entry.delete(
            0,
            "end"
        )

        if channel == "Email":

            self.recipient_label.configure(
                text="Recipient Email"
            )

            self.recipient_entry.configure(
                placeholder_text="student@example.com"
            )

        elif channel == "SMS":

            self.recipient_label.configure(
                text="Recipient Phone Number"
            )

            self.recipient_entry.configure(
                placeholder_text="+639123456789"
            )

        else:

            self.recipient_label.configure(
                text="Recipient"
            )

            self.recipient_entry.configure(
                placeholder_text="Enter recipient"
            )

    # ========================================================
    # LOG
    # ========================================================

    def add_log(self, message):

        self.log_text.insert(
            "end",
            message + "\n"
        )

        self.log_text.see("end")

    # ========================================================
    # EMAIL
    # ========================================================

    def send_brevo_email(
        self,
        recipient_email,
        message_content
    ):

        if not BREVO_API_KEY:
            return (
                False,
                "[ERROR] BREVO_API_KEY is not configured."
            )

        configuration = sib_api_v3_sdk.Configuration()

        configuration.api_key[
            "api-key"
        ] = BREVO_API_KEY

        api_instance = (
            sib_api_v3_sdk.TransactionalEmailsApi(
                sib_api_v3_sdk.ApiClient(
                    configuration
                )
            )
        )

        safe_message = html.escape(
            message_content
        )

        send_smtp_email = (
            sib_api_v3_sdk.SendSmtpEmail(
                to=[
                    {
                        "email": recipient_email
                    }
                ],
                sender={
                    "name": SENDER_NAME,
                    "email": SENDER_EMAIL
                },
                subject="NDMU Notification System",
                html_content=(
                    "<html>"
                    "<body>"
                    f"<p>{safe_message}</p>"
                    "</body>"
                    "</html>"
                )
            )
        )

        try:

            api_response = (
                api_instance.send_transac_email(
                    send_smtp_email
                )
            )

            message_id = getattr(
                api_response,
                "message_id",
                "N/A"
            )

            return (
                True,
                f"[SUCCESS] Email sent to "
                f"{recipient_email} | ID: {message_id}"
            )

        except ApiException as e:

            reason = getattr(
                e,
                "reason",
                str(e)
            )

            return (
                False,
                f"[ERROR] Email failed: {reason}"
            )

        except Exception as e:

            return (
                False,
                f"[ERROR] Email failed: {e}"
            )

    # ========================================================
    # SMS
    # ========================================================

    def send_brevo_sms(
        self,
        recipient_phone,
        message_content
    ):

        if not BREVO_API_KEY:
            return (
                False,
                "[ERROR] BREVO_API_KEY is not configured."
            )

        url = (
            "https://api.brevo.com/v3/"
            "transactionalSMS/send"
        )

        headers = {
            "accept": "application/json",
            "api-key": BREVO_API_KEY,
            "content-type": "application/json"
        }

        data = {
            "sender": SMS_SENDER,
            "recipient": recipient_phone,
            "content": message_content
        }

        try:

            response = requests.post(
                url,
                headers=headers,
                json=data,
                timeout=30
            )

            if response.status_code in (200, 201):

                try:
                    result = response.json()
                except ValueError:
                    result = {}

                message_id = result.get(
                    "messageId",
                    "N/A"
                )

                return (
                    True,
                    f"[SUCCESS] SMS sent to "
                    f"{recipient_phone} | ID: {message_id}"
                )

            return (
                False,
                f"[ERROR] SMS failed | "
                f"HTTP {response.status_code} | "
                f"{response.text}"
            )

        except requests.exceptions.Timeout:

            return (
                False,
                "[ERROR] SMS request timed out."
            )

        except requests.exceptions.ConnectionError:

            return (
                False,
                "[ERROR] Could not connect to Brevo."
            )

        except requests.exceptions.RequestException as e:

            return (
                False,
                f"[ERROR] SMS request failed: {e}"
            )

        except Exception as e:

            return (
                False,
                f"[ERROR] Unexpected SMS error: {e}"
            )

    # ========================================================
    # EMAIL VALIDATION
    # ========================================================

    def is_valid_email(self, email):

        pattern = (
            r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
        )

        return re.match(
            pattern,
            email
        ) is not None

    # ========================================================
    # PHONE VALIDATION
    # ========================================================

    def is_valid_phone(self, phone):

        pattern = (
            r"^\+?[1-9]\d{7,14}$"
        )

        return re.match(
            pattern,
            phone
        ) is not None

    # ========================================================
    # SEND
    # ========================================================

    def on_send(self):

        channel = self.channel_var.get()

        recipient = (
            self.recipient_entry
            .get()
            .strip()
        )

        message = (
            self.message_entry
            .get("1.0", "end")
            .strip()
        )

        # ----------------------------------------------------
        # API KEY
        # ----------------------------------------------------

        if not BREVO_API_KEY:

            messagebox.showerror(
                "Configuration Error",
                "BREVO_API_KEY is not configured."
            )

            self.add_log(
                "[ERROR] BREVO_API_KEY is not configured."
            )

            return

        # ----------------------------------------------------
        # MESSAGE
        # ----------------------------------------------------

        if not message:

            messagebox.showwarning(
                "Missing Message",
                "Please enter a message."
            )

            self.add_log(
                "[WARNING] Message is empty."
            )

            return

        # ----------------------------------------------------
        # EMAIL
        # ----------------------------------------------------

        if channel == "Email":

            if not recipient:

                messagebox.showwarning(
                    "Missing Email",
                    "Please enter the recipient email."
                )

                self.add_log(
                    "[WARNING] Recipient email is empty."
                )

                return

            if not self.is_valid_email(recipient):

                messagebox.showwarning(
                    "Invalid Email",
                    "Please enter a valid email address."
                )

                self.add_log(
                    "[WARNING] Invalid email address."
                )

                return

            self.send_btn.configure(
                state="disabled",
                text="Sending..."
            )

            self.update()

            success, log_message = (
                self.send_brevo_email(
                    recipient,
                    message
                )
            )

            self.add_log(log_message)

            self.send_btn.configure(
                state="normal",
                text="Send Notification"
            )

        # ----------------------------------------------------
        # SMS
        # ----------------------------------------------------

        elif channel == "SMS":

            if not recipient:

                messagebox.showwarning(
                    "Missing Phone Number",
                    "Please enter the recipient phone number."
                )

                self.add_log(
                    "[WARNING] Phone number is empty."
                )

                return

            if not self.is_valid_phone(recipient):

                messagebox.showwarning(
                    "Invalid Phone Number",
                    "Use international format.\n\n"
                    "Example: +639123456789"
                )

                self.add_log(
                    "[WARNING] Invalid phone number."
                )

                return

            self.send_btn.configure(
                state="disabled",
                text="Sending..."
            )

            self.update()

            success, log_message = (
                self.send_brevo_sms(
                    recipient,
                    message
                )
            )

            self.add_log(log_message)

            self.send_btn.configure(
                state="normal",
                text="Send Notification"
            )

        # ----------------------------------------------------
        # PUSH
        # ----------------------------------------------------

        elif channel == "Push Notification":

            messagebox.showinfo(
                "Not Implemented",
                "Push Notification has not been implemented yet."
            )

            self.add_log(
                "[INFO] Push Notification is not implemented."
            )

    # ========================================================
    # CLEAR LOG
    # ========================================================

    def on_clear(self):

        self.log_text.delete(
            "1.0",
            "end"
        )


# ============================================================
# START PROGRAM
# ============================================================

if __name__ == "__main__":

    app = NotificationApp()
    app.mainloop()
