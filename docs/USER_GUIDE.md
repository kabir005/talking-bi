# Talking BI - User Guide

**Version:** 1.0.0  
**Last Updated:** March 22, 2026

---

## Table of Contents

1. [Introduction](#introduction)
2. [Getting Started](#getting-started)
3. [Uploading Data](#uploading-data)
4. [Creating Dashboards](#creating-dashboards)
5. [Using Natural Language Commands](#using-natural-language-commands)
6. [Drill-Down Analysis](#drill-down-analysis)
7. [Filtering Data](#filtering-data)
8. [Machine Learning](#machine-learning)
9. [What-If Simulation](#what-if-simulation)
10. [Root Cause Analysis](#root-cause-analysis)
11. [Exporting Reports](#exporting-reports)
12. [Tips & Best Practices](#tips--best-practices)

---

## Introduction

Talking BI is an AI-powered Business Intelligence platform that helps you analyze data, create dashboards, and gain insights using natural language. It's completely free and runs locally on your machine.

### Key Features

- **Automatic Data Cleaning** - Upload messy data, get clean results
- **11 Chart Types** - Line, Bar, Area, Pie, Scatter, Heatmap, and more
- **Natural Language Commands** - Just type what you want
- **Machine Learning** - Automatic predictions and forecasting
- **Root Cause Analysis** - Understand why metrics change
- **What-If Simulation** - Explore scenarios
- **Multi-Agent AI** - 11 intelligent agents working together

---

## Getting Started

### First Time Setup

1. **Start the Backend**
   ```bash
   cd talking-bi/backend
   python main.py
   ```

2. **Start the Frontend**
   ```bash
   cd talking-bi/frontend
   npm run dev
   ```

3. **Open Your Browser**
   - Navigate to `http://localhost:5173`
   - You should see the Talking BI interface

### Interface Overview

- **Top Bar** - Theme toggle, user menu
- **Sidebar** - Navigation (Datasets, Dashboards, Reports)
- **Main Area** - Your dashboards and visualizations
- **Command Bar** - Natural language input
- **Filter Bar** - Global filters
- **Memory Panel** - Past queries and suggestions

---

## Uploading Data

### Supported Formats

- **CSV** - Comma-separated values
- **Excel** - .xlsx, .xls files
- **JSON** - Structured JSON data
- **Web Scraping** - Extract data from websites
- **REST API** - Connect to external APIs

### Upload from File

1. Click **"Upload Data"** button
2. Drag and drop your file or click to browse
3. Wait for automatic cleaning
4. Review the cleaning report
5. Click **"Create Dashboard"**

### Upload from URL

1. Click **"Scrape from URL"**
2. Enter the website URL
3. The system will extract tables automatically
4. Review extracted data
5. Click **"Create Dashboard"**

### Connect to API

1. Click **"Connect to API"**
2. Enter API endpoint URL
3. Add headers if needed (e.g., Authorization)
4. Specify data path (e.g., `data.results`)
5. Click **"Connect & Import"**

### Data Cleaning

Talking BI automatically:
- Fills missing values (median for numbers, mode for categories)
- Removes duplicate rows
- Fixes data types (dates, numbers, booleans)
- Detects outliers (flags but doesn't remove)
- Identifies ID columns

You'll see a cleaning report showing:
- Actions taken
- Rows affected
- Outliers detected
- Recommendations

---

## Creating Dashboards

### Automatic Dashboard Generation

1. After uploading data, click **"Generate Dashboard"**
2. Choose a preset:
   - **Executive** - High-level KPIs and key charts
   - **Operational** - Detailed metrics and comprehensive charts
   - **Trend** - Time-series focused analysis
   - **Comparison** - Period-over-period comparison
3. The system will automatically:
   - Analyze your data
   - Select appropriate chart types
   - Create KPI cards
   - Generate insights

### Dashboard Presets

**Executive Preset**
- 4 KPI cards at the top
- 3-4 key charts
- Focus on high-level metrics
- Best for: C-level executives, board presentations

**Operational Preset**
- Multiple KPI cards
- 10-12 comprehensive charts
- Detailed breakdowns
- Best for: Operations teams, detailed analysis

**Trend Preset**
- Time-series charts
- Trend lines
- Moving averages
- Best for: Tracking changes over time

**Comparison Preset**
- Side-by-side charts
- Period comparisons
- Variance analysis
- Best for: Comparing time periods or segments

### Customizing Dashboards

- **Drag & Drop** - Rearrange tiles
- **Resize** - Adjust tile sizes
- **Edit Chart** - Click tile to edit
- **Add Filters** - Use filter bar
- **Change Preset** - Switch between presets

---

## Using Natural Language Commands

### Command Types

**Date Filtering**
```
show only last 6 months
show data from 2024
filter to Q4 2024
```

**Highlighting**
```
highlight best region
emphasize top performers
focus on highest revenue
```

**Outlier Management**
```
remove outliers
exclude anomalies
filter out extreme values
```

**Chart Type Changes**
```
switch to bar chart
change to line chart
make it a pie chart
```

**Axis Modifications**
```
add Revenue to Y axis
remove Date from X axis
swap axes
```

**Comparisons**
```
compare with Q3
show vs last year
compare regions
```

**Predictions**
```
predict next 3 months
forecast next quarter
project next year
```

**Root Cause Analysis**
```
why did sales drop?
explain revenue decline
what caused the spike?
```

**What-If Scenarios**
```
what if budget increases 20%?
simulate 10% price increase
what if we double marketing spend?
```

### Using Commands

1. Type your command in the command bar
2. Press Enter or click "Execute"
3. The system will:
   - Parse your command
   - Apply changes
   - Show results
   - Update dashboard

### Command Suggestions

- Click the sparkle icon (✨) to see suggestions
- Suggestions are context-aware
- Based on your data and past queries

---

## Drill-Down Analysis

### What is Drill-Down?

Drill-down lets you explore data at different levels of detail. For example:
- Year → Quarter → Month → Week → Day
- Country → State → City
- Category → Subcategory → Product

### How to Drill-Down

1. **Click on a chart element** (bar, pie slice, data point)
2. **Select drill-down column** from the menu
3. **View filtered results** in the drill-down panel
4. **Navigate breadcrumbs** to go back up

### Drill-Down Features

- **Breadcrumb Navigation** - See your path and go back
- **Smart Suggestions** - System suggests next best column
- **Summary Statistics** - See totals, averages, etc.
- **Sample Data** - Preview filtered rows

### Time-Based Drill-Down

For date columns, you can drill down through time:
1. Start with yearly view
2. Drill to quarters
3. Drill to months
4. Drill to weeks
5. Drill to days

---

## Filtering Data

### Adding Filters

1. Click **"Add Filter"** in the filter bar
2. Select column to filter
3. Choose operator:
   - **Equals** - Exact match
   - **Contains** - Partial match (text)
   - **Greater than** - Numeric comparison
   - **Less than** - Numeric comparison
   - **Between** - Range (numeric or date)
   - **In** - Multiple values
4. Enter value(s)
5. Click **"Apply"**

### Filter Types

**String Filters**
- Equals: `Region equals "North"`
- Contains: `Product contains "Pro"`

**Number Filters**
- Equals: `Revenue equals 10000`
- Greater than: `Sales > 5000`
- Less than: `Quantity < 100`
- Between: `Price between 10 and 50`

**Date Filters**
- Equals: `Date equals 2024-01-01`
- After: `Date > 2024-01-01`
- Before: `Date < 2024-12-31`
- Between: `Date between 2024-01-01 and 2024-12-31`

### Filter Suggestions

- Click on a column to see suggested values
- System shows most common values
- Shows value counts and percentages

### Combining Filters

- Multiple filters are combined with AND logic
- All conditions must be true
- Use "Clear all" to remove all filters

---

## Machine Learning

### Auto ML

Talking BI automatically:
1. Detects if your data is suitable for ML
2. Identifies the target variable
3. Trains multiple models
4. Selects the best model
5. Shows feature importance

### Training a Model

1. Click **"Train ML Model"** button
2. Select target column (what to predict)
3. Choose task type:
   - **Auto** - System decides
   - **Regression** - Predict numbers
   - **Classification** - Predict categories
4. Click **"Train"**
5. Wait for training (usually 30-60 seconds)

### Model Results

You'll see:
- **Model Type** - Algorithm used
- **Accuracy Metrics** - R², MAE, RMSE
- **Feature Importance** - Which features matter most
- **Predictions** - Actual vs predicted chart

### Making Predictions

1. Go to trained model
2. Click **"Make Prediction"**
3. Enter values for features
4. Click **"Predict"**
5. See predicted value

### Forecasting

1. Select a time-series model
2. Click **"Forecast"**
3. Choose number of periods (days, weeks, months)
4. See forecast chart with confidence intervals

---

## What-If Simulation

### Running Simulations

1. Click **"What-If Simulator"**
2. Select parameters to change
3. Use sliders to adjust values
4. See real-time impact on target metric
5. Compare baseline vs scenario

### Sensitivity Analysis

1. Click **"Sensitivity Analysis"**
2. System varies each parameter
3. Shows which parameters have most impact
4. Ranked by sensitivity

### Scenario Comparison

1. Create multiple scenarios
2. Compare side-by-side
3. See best and worst cases
4. Export comparison report

### Optimization

1. Click **"Optimize"**
2. Choose objective (maximize or minimize)
3. Set constraints
4. System finds optimal values

---

## Root Cause Analysis

### When to Use

Use root cause analysis when:
- A metric suddenly drops or spikes
- You want to understand why something happened
- You need to explain changes to stakeholders

### Running Root Cause Analysis

1. Type: `why did [metric] drop?`
2. Or click **"Root Cause Analysis"**
3. Select metric to analyze
4. Choose time period
5. Click **"Analyze"**

### Understanding Results

You'll see:
- **Summary** - What happened and why
- **Causal Chain** - Step-by-step explanation
- **Confidence Scores** - How certain we are
- **Evidence** - Statistical proof
- **Recommendations** - What to do about it

### Knowledge Graph

- Visual representation of relationships
- Nodes = variables
- Edges = correlations
- Click nodes to explore
- Zoom and pan to navigate

---

## Exporting Reports

### Export Formats

- **PDF** - Professional report with charts
- **PowerPoint** - Editable presentation
- **JSON** - Dashboard configuration
- **PNG** - Individual charts
- **CSV** - Raw data

### Exporting PDF Report

1. Click **"Export"** menu
2. Select **"PDF Report"**
3. Choose what to include:
   - Executive summary
   - All charts
   - Insights
   - Recommendations
4. Click **"Generate PDF"**
5. Download when ready

### Exporting PowerPoint

1. Click **"Export"** menu
2. Select **"PowerPoint"**
3. System creates:
   - Title slide
   - KPI slide
   - One slide per chart
   - Recommendations slide
4. Download .pptx file

### Exporting Dashboard

1. Click **"Export"** menu
2. Select **"Dashboard JSON"**
3. Save configuration file
4. Import later to restore dashboard

### Exporting Charts

1. Click on a chart
2. Click **"Export as PNG"**
3. Choose size and DPI
4. Download image

---

## Tips & Best Practices

### Data Preparation

✅ **Do:**
- Use consistent column names
- Include date columns for time-series
- Keep data in tabular format
- Remove unnecessary columns before upload

❌ **Don't:**
- Mix data types in same column
- Use merged cells (Excel)
- Include summary rows in data
- Use special characters in column names

### Dashboard Design

✅ **Do:**
- Start with Executive preset for overview
- Use Operational preset for detailed analysis
- Keep KPIs at the top
- Use appropriate chart types

❌ **Don't:**
- Overcrowd with too many charts
- Use pie charts for many categories
- Mix unrelated metrics
- Ignore the cleaning report

### Natural Language Commands

✅ **Do:**
- Be specific: "show last 6 months" not "show recent"
- Use proper column names
- Try command suggestions
- Check results after each command

❌ **Don't:**
- Use vague terms
- Combine too many commands at once
- Ignore error messages
- Forget to apply changes

### Machine Learning

✅ **Do:**
- Have at least 100 rows of data
- Include relevant features
- Check feature importance
- Validate predictions

❌ **Don't:**
- Use ML for small datasets (<50 rows)
- Include ID columns as features
- Ignore low accuracy warnings
- Over-rely on predictions

### Performance

✅ **Do:**
- Filter large datasets before analysis
- Use drill-down for detailed views
- Clear filters when done
- Close unused dashboards

❌ **Don't:**
- Load datasets with millions of rows
- Keep all filters active
- Create too many dashboards
- Run multiple ML trainings simultaneously

---

## Keyboard Shortcuts

- **Ctrl/Cmd + K** - Focus command bar
- **Ctrl/Cmd + F** - Open filter bar
- **Ctrl/Cmd + D** - Duplicate dashboard
- **Ctrl/Cmd + E** - Export menu
- **Ctrl/Cmd + R** - Refresh dashboard
- **Esc** - Close modals/panels

---

## Troubleshooting

### Data Upload Issues

**Problem:** File won't upload  
**Solution:** Check file format (CSV, Excel, JSON only)

**Problem:** Too many errors in cleaning  
**Solution:** Review data quality, fix major issues manually

**Problem:** Wrong data types detected  
**Solution:** Rename columns to include type hints (e.g., `date_created`, `amount_usd`)

### Dashboard Issues

**Problem:** No charts generated  
**Solution:** Ensure data has numeric columns

**Problem:** Charts show no data  
**Solution:** Check filters, clear and try again

**Problem:** Dashboard is slow  
**Solution:** Reduce number of charts or filter data

### ML Issues

**Problem:** Model training fails  
**Solution:** Check data quality, need at least 50 rows

**Problem:** Low accuracy  
**Solution:** Add more relevant features or get more data

**Problem:** Predictions seem wrong  
**Solution:** Check feature importance, remove irrelevant features

---

## Getting Help

- **Documentation:** Check this guide
- **Command Suggestions:** Click sparkle icon
- **Memory Panel:** See past successful queries
- **Error Messages:** Read carefully, they're helpful
- **Support:** Contact your administrator

---

## Glossary

- **Agent** - AI component that performs specific tasks
- **Drill-Down** - Exploring data at different detail levels
- **Feature** - Input variable for machine learning
- **KPI** - Key Performance Indicator
- **Preset** - Pre-configured dashboard layout
- **Root Cause** - Underlying reason for a change
- **What-If** - Scenario simulation
- **Confidence Score** - How certain the AI is (0-100%)

---

**Version:** 1.0.0  
**Last Updated:** March 22, 2026  
**Platform:** Talking BI - Agentic AI Business Intelligence

