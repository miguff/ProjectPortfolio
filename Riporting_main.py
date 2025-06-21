from Riporting import StockRiports_main
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import osenv
import os
import smtplib

def main():
    StockRiports_main()
    SendEmail("Monthly Riports")


def SendEmail(Subject: str):
    smtp_server = 'smtp.gmail.com'
    smtp_port = 587
    smtp_username = os.environ['GMAIL_USERNAME']
    smtp_password = os.environ['GMAIL_PASSWORD'] 
    from_email = os.environ['GMAIL_USERNAME']
    to_email = os.environ['TO_USERNAME']
    subject = Subject

    # Create message container
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = from_email
    msg['To'] = to_email


    path = "Images/"
    riportnames = ["PieChart.jpg", "SumBar.jpg"]
    for i in riportnames:
        pngfilepath = os.path.join(path, i)
        fp = open(pngfilepath, 'rb')
        img = MIMEImage(fp.read())
        img.add_header('Content-Disposition', f'attachment; filename={i}')
        fp.close()
        msg.attach(img)

    # Send the message via SMTP server
    server = smtplib.SMTP(smtp_server, smtp_port)
    server.starttls()
    server.login(smtp_username, smtp_password)
    server.sendmail(from_email, to_email, msg.as_string())
    server.quit()
    print("Email sent Successfully!")


if __name__ == "__main__":
    main()