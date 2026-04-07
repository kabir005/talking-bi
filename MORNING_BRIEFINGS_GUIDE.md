# Morning Briefings Feature - Complete Guide

## What is Morning Briefings?

Morning Briefings is an automated email reporting system that sends scheduled data insights to stakeholders. It analyzes your datasets and delivers professional reports with KPIs, trends, and anomalies directly to email inboxes.

**Think of it as**: Your personal data analyst that wakes up before you do and sends a comprehensive report to your team.

## Why Use This Feature?

### Business Value:
- **Save Time**: No manual report creation - fully automated
- **Stay Informed**: Get daily/weekly insights without logging in
- **Team Alignment**: Everyone gets the same data at the same time
- **Proactive Monitoring**: Catch anomalies and trends early
- **Executive Ready**: Professional PDF reports suitable for leadership

### Use Cases:
- Daily sales performance reports for management
- Weekly KPI summaries for stakeholders
- Monthly trend analysis for strategic planning
- Real-time anomaly alerts for operations teams
- Automated compliance reporting

## How It Works

### The Flow:
1. **You Configure** → Select dataset, recipients, schedule, and what to include
2. **System Schedules** → Cron-based scheduler runs at specified times
3. **AI Analyzes** → Automatically calculates KPIs, detects trends, finds anomalies
4. **Report Generated** → Creates professional HTML email + PDF attachment
5. **Email Sent** → Delivers to all recipients via SMTP

### Behind the Scenes:
```
User Creates Briefing
    ↓
Scheduler Activates (APScheduler)
    ↓
Load Dataset from Database
    ↓
Analyze Data (pandas + statistics)
    ↓
Generate HTML Email (styled template)
    ↓
Generate PDF Report (ReportLab)
    ↓
Send via SMTP (Gmail/custom)
    ↓
Recipients Receive Email
```

## Email Configuration

Your `.env` file already has email configured:
```
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=yoronaldo779@gmail.com
SMTP_PASS=wjccailbgckqysvm
SMTP_FROM=yoronaldo779@gmail.com
```

**Important**: For Gmail, you need to use an "App Password" not your regular password:
1. Go to Google Account → Security
2. Enable 2-Factor Authentication
3. Generate App Password for "Mail"
4. Use that password in SMTP_PASS

## Features Included

### 1. Key Performance Indicators (KPIs)
- Automatically calculates averages for numeric columns
- Shows top 5 metrics in a clean format
- Displayed as cards in email and PDF

### 2. Trends Analysis
- Compares first vs last values in dataset
- Calculates percentage change
- Identifies increasing/decreasing patterns
- Shows direction and magnitude

### 3. Anomaly Detection
- Uses statistical methods (3-sigma rule)
- Finds outliers in numeric columns
- Highlights data quality issues
- Alerts on unusual patterns

### 4. Professional Formatting
- Gradient header with branding
- Color-coded sections (trends=green, anomalies=red)
- Responsive HTML email
- Print-ready PDF attachment

## How to Use

### Step 1: Create a Briefing
1. Navigate to "Briefings" page
2. Click "Create Briefing"
3. Fill in the form:
   - **Name**: "Daily Sales Report"
   - **Dataset**: Select from dropdown (e.g., insurance data, sales data)
   - **Recipients**: Add email addresses (click Add after each)
   - **Schedule**: Choose preset (Daily at 8 AM, Weekdays, etc.)
   - **Timezone**: Select your timezone
   - **Include**: Check KPIs, Trends, Anomalies as needed
4. Click "Create Briefing"

### Step 2: Test Immediately
- Click the "Send" icon (paper plane) on any briefing
- This sends the report immediately without waiting for schedule
- Check your email inbox for the report

### Step 3: Monitor
- View all scheduled briefings on the page
- See next run time for each briefing
- Delete or modify as needed

## Schedule Options

Available presets:
- **Daily at 8:00 AM** - `0 8 * * *` - Every day at 8 AM
- **Weekdays at 7:00 AM** - `0 7 * * 1-5` - Monday-Friday at 7 AM
- **Weekly on Monday at 9:00 AM** - `0 9 * * 1` - Every Monday at 9 AM
- **Monthly on 1st at 10:00 AM** - `0 10 1 * *` - First day of month at 10 AM
- **Every 6 hours** - `0 */6 * * *` - Four times daily

## What Gets Analyzed

For each dataset, the system automatically:

1. **Calculates Statistics**:
   - Mean, median, standard deviation
   - Min/max values
   - Data completeness

2. **Identifies Trends**:
   - Compares start vs end values
   - Calculates growth rates
   - Detects patterns

3. **Finds Anomalies**:
   - Statistical outliers (3-sigma)
   - Missing data patterns
   - Unusual distributions

4. **Generates Insights**:
   - Executive summary
   - Key takeaways
   - Action items

## Email Report Structure

### Email Contains:
- **Header**: Briefing name + date
- **Executive Summary**: High-level overview
- **Key Metrics**: Top KPIs in card format
- **Trends Section**: Identified patterns
- **Anomalies Section**: Issues requiring attention
- **Footer**: Dataset info + branding

### PDF Attachment:
- Same content as email
- Professional formatting
- Print-ready layout
- Suitable for presentations

## Fixes Applied

✅ **Theme-aware styling** - Uses CSS variables for dark/light mode
✅ **Dynamic dataset loading** - Loads from backend API
✅ **API client migration** - Uses apiClient instead of axios
✅ **Fixed source_path** - Corrected field name in briefing generator
✅ **Email configuration** - Uses .env variables properly
✅ **Error handling** - Shows helpful toast messages

## Testing Checklist

- [ ] Frontend loads without styling issues
- [ ] Dataset dropdown shows all available datasets
- [ ] Can add/remove email recipients
- [ ] Schedule presets load correctly
- [ ] Can create briefing successfully
- [ ] Briefing appears in list with next run time
- [ ] "Send Now" button works and sends email
- [ ] Email arrives with HTML content and PDF attachment
- [ ] PDF opens and displays correctly
- [ ] Can delete briefings

## Troubleshooting

**Dataset dropdown is empty**:
- Check that datasets exist in the database
- Verify backend API is running
- Check browser console for errors

**Email not sending**:
- Verify SMTP credentials in .env
- For Gmail, use App Password not regular password
- Check backend logs for SMTP errors
- Test with "Send Now" button first

**Briefing not scheduled**:
- Check that APScheduler is running
- Verify cron expression is valid
- Check backend logs for scheduler errors

## Technical Stack

- **Scheduler**: APScheduler (Python cron-based)
- **Email**: smtplib (Python standard library)
- **PDF Generation**: ReportLab
- **Analysis**: pandas + numpy
- **Frontend**: React + TypeScript
- **Backend**: FastAPI + SQLAlchemy

## Next Steps

The Morning Briefings feature is now fully functional and connected. You can:
1. Create briefings for any dataset
2. Schedule automated delivery
3. Send test emails immediately
4. Monitor scheduled runs
5. Manage recipients and schedules

All email configuration from your .env file is properly integrated.
