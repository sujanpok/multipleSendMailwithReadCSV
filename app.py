import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import threading
import logging
from credentials import load_sender_credentials, save_sender_credentials
from main import send_emails
import webbrowser
import re 

class MailSenderApp:
    def __init__(self, root):
        self.root = root
        self.root.withdraw()  # Hide the main window initially
        self.root.title("MailSenderApp")

        # Load sender credentials
        self.sender_email, self.sender_password = load_sender_credentials()
        self.recipients_list = []

        self.setup_logging()

        # Open setup pop-up if credentials are not set
        if not self.sender_email or not self.sender_password:
            self.open_setup_popup()
        else:
            self.create_main_gui_elements()

    def setup_logging(self):
        logging.basicConfig(filename='email_log.txt', level=logging.INFO,
                            format='%(asctime)s - %(levelname)s - %(message)s')

    def create_main_gui_elements(self):
        # Main app section
        self.root.deiconify()  # Show the main window
        self.setup_menu()

        # Configure grid for responsiveness
        self.root.grid_columnconfigure(0, weight=1, uniform="equal")
        self.root.grid_columnconfigure(1, weight=3, uniform="equal")
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_rowconfigure(1, weight=3)
        self.root.grid_rowconfigure(2, weight=1)
        self.root.grid_rowconfigure(3, weight=2)
        self.root.grid_rowconfigure(4, weight=1)
        self.root.grid_rowconfigure(6, weight=1)

        # Loading indicator
        self.loading_label = ttk.Label(self.root, text="", foreground='red', width=20)
        self.loading_label.grid(row=0, column=1, padx=10, pady=10, sticky='ew', columnspan=2)
        
        # Main GUI elements for sending emails
        ttk.Label(self.root, text="Subject:").grid(row=1, column=0, padx=10, pady=20, sticky='w')
        self.subject_entry = ttk.Entry(self.root, width=30)
        self.subject_entry.grid(row=1, column=1, padx=10, pady=5, sticky='ew')

        ttk.Label(self.root, text="Message:").grid(row=2, column=0, padx=10, pady=5, sticky='nw')
        self.message_text = tk.Text(self.root, width=70, height=15)
        self.message_text.grid(row=2, column=1, padx=10, pady=5, sticky='ew')
        
        # Individual email input section
        ttk.Label(self.root, text="Email:").grid(row=3, column=0, padx=10, pady=5, sticky='nw')
        self.individual_email_frame = ttk.Frame(self.root)
        self.individual_email_frame.grid(row=3, column=1, padx=10, pady=20, sticky='w')

        self.individual_email_entry = ttk.Entry(self.individual_email_frame, width=50)
        self.individual_email_entry.grid(row=0, column=0, padx=5, pady=5, sticky='ew')
        ttk.Button(self.individual_email_frame, text="Add Email", command=self.add_individual_email).grid(row=0, column=1, padx=10, pady=5)
        
        ttk.Label(self.root, text="Email List:").grid(row=4, column=0, padx=10, pady=5, sticky='nw')
        self.email_listbox = tk.Listbox(self.root, width=60, height=5)
        self.email_listbox.grid(row=4, column=1, padx=10, pady=5, sticky='ew')
        ttk.Button(self.root, text="Delete Selected Email", command=self.delete_selected_email).grid(row=6, column=1, padx=100, pady=10, sticky='ew')

        # Send emails button
        ttk.Button(self.root, text="Send Emails", command=self.send_emails).grid(row=7, column=1, padx=50, pady=50, sticky='ew')

    def setup_menu(self):
        # Menu Bar
        menu_bar = tk.Menu(self.root)
        self.root.config(menu=menu_bar)

        # Setup menu
        setup_menu = tk.Menu(menu_bar, tearoff=0)
        setup_menu.add_command(label="Email Credentials", command=self.open_setup_popup)
        menu_bar.add_cascade(label="Setup", menu=setup_menu)
        
        # # Setup Tool
        # setup_tool = tk.Menu(menu_bar, tearoff=0)
        # setup_tool.add_command(label="Bulk Send Mail From CSV", command=self.load_recipients)
        # menu_bar.add_cascade(label="Tool", menu=setup_tool)

        # Help menu
        help_menu = tk.Menu(menu_bar, tearoff=0)
        help_menu.add_command(label="About", command=self.show_about_info)
        menu_bar.add_cascade(label="Help", menu=help_menu)

    def open_setup_popup(self):
        # If setup window already exists, bring it to the front
        if hasattr(self, 'setup_window') and self.setup_window.winfo_exists():
            self.setup_window.lift()
            return

        # Create a new window for setting up email and password
        self.setup_window = tk.Toplevel(self.root)
        self.setup_window.title("Setup Email Credentials")
        self.setup_window.geometry("500x200")  # Set a larger size for the pop-up

        ttk.Label(self.setup_window, text="Enter sender email:").grid(row=0, column=0, padx=10, pady=10, sticky='w')
        self.email_entry = ttk.Entry(self.setup_window, width=40)
        self.email_entry.grid(row=0, column=1, padx=10, pady=10)

        ttk.Label(self.setup_window, text="Enter Google App Password:").grid(row=1, column=0, padx=10, pady=10, sticky='w')
        self.password_entry = ttk.Entry(self.setup_window, show='*', width=40)
        self.password_entry.grid(row=1, column=1, padx=10, pady=10)
        
        # Link to get Google App Password
        link_button = ttk.Button(self.setup_window, text="Get Google App Password", command=lambda: open_link(None))
        
        link_button.grid(row=3, column=1, padx=10, pady=10, sticky='e')

        def open_link(event):
            # Opens the URL in the default web browser
            webbrowser.open("https://knowledge.workspace.google.com/kb/how-to-create-app-passwords-000009237?hl=en")
            
        # Buttons
        ttk.Button(self.setup_window, text="Save Credentials", command=self.save_sender_credentials).grid(row=2, column=1, padx=10, pady=10, sticky='e')
        ttk.Button(self.setup_window, text="Skip", command=self.skip_setup).grid(row=2, column=0, padx=10, pady=10, sticky='w')

        # Load credentials to populate the fields
        self.populate_credentials()

    def skip_setup(self):
        # Destroy the setup window and proceed to the main GUI
        self.setup_window.destroy()
        self.create_main_gui_elements()

    def populate_credentials(self):
        # Populate email and password fields if they exist
        if self.sender_email and self.sender_password:
            self.email_entry.insert(0, self.sender_email)
            self.password_entry.insert(0, self.sender_password)

    def save_sender_credentials(self):
        self.sender_email = self.email_entry.get().strip()
        self.sender_password = self.password_entry.get().strip()

        if not self.sender_email or not self.sender_password:
            messagebox.showerror("Input Error", "Email and password cannot be empty.")
            return self.open_setup_popup()
        if self.sender_email:
            email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_regex, self.sender_email):
                messagebox.showerror("Invalid Email", f"'{self.sender_email}' is not a valid email address.")
                return self.open_setup_popup()
            
        # Save credentials to file
        save_sender_credentials(self.sender_email, self.sender_password)
        logging.info("Sender email credentials saved successfully.")
        messagebox.showinfo("Success", "Credentials saved successfully!")
        self.setup_window.destroy()
        self.create_main_gui_elements()

    def add_individual_email(self):
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        email = self.individual_email_entry.get().strip()
        if email:
            if re.match(email_regex, email):
                self.recipients_list.insert(0, email)
                self.email_listbox.insert(0, email)
                self.individual_email_entry.delete(0, tk.END)
                logging.info(f"Added individual email: {email}")
            else:
                messagebox.showerror("Invalid Email", f"'{email}' is not a valid email address.")
                logging.error(f"Invalid email address attempted to add: {email}")

    def delete_selected_email(self):
        selected_index = self.email_listbox.curselection()
        if selected_index:
            index = selected_index[0]
            email = self.recipients_list.pop(index)
            self.email_listbox.delete(index)
            logging.info(f"Deleted individual email: {email}")

    def send_emails(self):
        # Check if credentials are set up before proceeding
        if not self.sender_email or not self.sender_password:
            messagebox.showerror("Credential Error", "Please set up email credentials before sending emails.")
            return

        subject = self.subject_entry.get().strip()
        message = self.message_text.get("1.0", "end-1c").strip()
        email   = self.individual_email_entry.get().strip()
        recipients = self.recipients_list
        recipients.append(email)

        if not subject or not message or not recipients:
            messagebox.showerror("Input Error", "Subject, message and email cannot be empty.")
            return

        self.loading_label.config(text="Sending emails... Please wait.")
        self.root.update_idletasks()

        threading.Thread(target=self._send_emails_in_background, args=(recipients, subject, message)).start()

    def _send_emails_in_background(self, recipients, subject, message):
        result = send_emails(self.sender_email, self.sender_password, recipients, subject, message)
        self.loading_label.config(text=result)

    def show_about_info(self):
        messagebox.showinfo("About", "Email Sender App\nVersion 1.0")

if __name__ == "__main__":
    root = tk.Tk()
    app = MailSenderApp(root)
    root.mainloop()
