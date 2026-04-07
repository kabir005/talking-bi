"""
Email Service
SMTP-based email sending for briefings.
"""

import os
import smtplib
import logging
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

logger = logging.getLogger(__name__)


async def send_briefing_email(
    recipients: list[str],
    subject: str,
    html_body: str,
    pdf_attachment: bytes,
    pdf_filename: str
):
    """Send briefing email with PDF attachment."""
    try:
        smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
        smtp_port = int(os.getenv("SMTP_PORT", "587"))
        smtp_user = os.getenv("SMTP_USER")
        smtp_pass = os.getenv("SMTP_PASS")
        smtp_from = os.getenv("SMTP_FROM", smtp_user)
        
        if not smtp_user or not smtp_pass:
            logger.warning("SMTP credentials not configured - email not sent")
            return False
        
        msg = MIMEMultipart()
        msg["From"] = smtp_from
        msg["To"] = ", ".join(recipients)
        msg["Subject"] = subject
        
        # HTML body
        msg.attach(MIMEText(html_body, "html"))
        
        # PDF attachment
        pdf_part = MIMEApplication(pdf_attachment, _subtype="pdf")
        pdf_part.add_header("Content-Disposition", "attachment", filename=pdf_filename)
        msg.attach(pdf_part)
        
        # Send
        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_pass)
            server.send_message(msg)
        
        logger.info(f"Email sent successfully to {len(recipients)} recipients")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send email: {e}")
        raise


def generate_html_email(
    briefing_name: str,
    dataset_name: str,
    summary: str,
    kpis: list[dict],
    trends: list[str],
    anomalies: list[str]
) -> str:
    """Generate HTML email body."""
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; text-align: center; }}
            .content {{ padding: 20px; }}
            .section {{ margin-bottom: 30px; }}
            .kpi {{ display: inline-block; background: #f0f4ff; padding: 15px; margin: 10px; border-radius: 8px; min-width: 150px; }}
            .kpi-value {{ font-size: 24px; font-weight: bold; color: #667eea; }}
            .kpi-label {{ font-size: 12px; color: #666; text-transform: uppercase; }}
            .trend {{ padding: 10px; background: #f9fafb; border-left: 3px solid #10b981; margin: 5px 0; }}
            .anomaly {{ padding: 10px; background: #fef2f2; border-left: 3px solid #ef4444; margin: 5px 0; }}
            .footer {{ text-align: center; padding: 20px; color: #666; font-size: 12px; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>{briefing_name}</h1>
            <p>{datetime.now().strftime("%B %d, %Y")}</p>
        </div>
        
        <div class="content">
            <div class="section">
                <h2>Executive Summary</h2>
                <p>{summary}</p>
            </div>
            
            <div class="section">
                <h2>Key Metrics</h2>
                <div>
                    {"".join([f'<div class="kpi"><div class="kpi-value">{kpi["value"]}</div><div class="kpi-label">{kpi["label"]}</div></div>' for kpi in kpis])}
                </div>
            </div>
            
            <div class="section">
                <h2>Trends</h2>
                {"".join([f'<div class="trend">{trend}</div>' for trend in trends])}
            </div>
            
            <div class="section">
                <h2>Anomalies</h2>
                {"".join([f'<div class="anomaly">{anomaly}</div>' for anomaly in anomalies]) if anomalies else '<p>No anomalies detected.</p>'}
            </div>
        </div>
        
        <div class="footer">
            <p>This is an automated briefing from Talking BI</p>
            <p>Dataset: {dataset_name}</p>
        </div>
    </body>
    </html>
    """
    return html
