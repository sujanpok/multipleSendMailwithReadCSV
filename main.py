import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Define the logging setup function in the same file
def setup_logging():
    logging.basicConfig(
        filename='email_log.txt',  # Log file name
        level=logging.INFO,  # Log level
        format='%(asctime)s - %(levelname)s - %(message)s'  # Log format
    )

# Call setup_logging to configure logging
setup_logging()

def send_emails(sender_email, sender_password, recipients, subject, message):
    print(sender_email)
    print(sender_password)
    print(subject)
    print(recipients)
    print(message)
    try:
        # Connect to the SMTP server
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            
            try:
                # Attempt to log in
                server.login(sender_email, sender_password)
            except smtplib.SMTPAuthenticationError:
                error_msg = "Authentication failed. Please check your email and password."
                logging.error(error_msg)
                return error_msg
            except smtplib.SMTPException as smtp_error:
                error_msg = f"SMTP error during login: {smtp_error}"
                logging.error(error_msg)
                return error_msg

            # Send emails to recipients
            for recipient_email in recipients:
                try:
                    msg = MIMEMultipart()
                    msg['From'] = sender_email
                    msg['To'] = recipient_email
                    msg['Subject'] = subject
                    msg.attach(MIMEText(message, 'plain'))

                    server.sendmail(sender_email, recipient_email, msg.as_string())
                    logging.info(f"Email sent to {recipient_email}")
                except smtplib.SMTPRecipientsRefused:
                    logging.error(f"Recipient refused: {recipient_email}")
                except smtplib.SMTPException as smtp_error:
                    logging.error(f"Error sending email to {recipient_email}: {smtp_error}")
        
        return "Emails sent successfully!"
    
    except smtplib.SMTPConnectError:
        error_msg = "Failed to connect to the SMTP server. Please check your network connection."
        logging.error(error_msg)
        return error_msg
    except smtplib.SMTPServerDisconnected:
        error_msg = "Server unexpectedly disconnected. Please try again later."
        logging.error(error_msg)
        return error_msg
    except Exception as e:
        error_msg = f"An unexpected error occurred: {e}"
        logging.error(error_msg)
        return error_msg
