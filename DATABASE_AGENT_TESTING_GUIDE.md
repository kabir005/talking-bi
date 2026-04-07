# Database Agent Testing Guide

## What is Database Agent?

The Database Agent is a natural language interface to live databases. It translates plain English questions into SQL queries, executes them securely (read-only), and returns results as datasets that can be visualized.

**Key Features:**
- Natural language to SQL translation using AI
- Read-only security (no DELETE, UPDATE, DROP, etc.)
- Automatic table validation (prevents hallucinated table names)
- Smart retry mechanism if LLM generates invalid queries
- Creates datasets from query results for dashboard creation

## How to Test

### Step 1: Start the Backend
```bash
cd talking-bi/backend
python main.py
```

### Step 2: Start the Frontend
```bash
cd talking-bi/frontend
npm run dev
```

### Step 3: Create a Database Connection

1. Navigate to the Database Agent page
2. Click "New Connection"
3. For testing with the existing SQLite database:
   - Name: "Local SQLite"
   - Type: SQLite
   - Database Path: `./data/talking.db`
4. Click "Test Connection" - should show success
5. Click "Save Connection"

### Step 4: Test Queries

The database has these main tables:
- `datasets` - Uploaded datasets metadata
- `dashboards` - Dashboard configurations
- `ml_models` - Trained ML models
- `users` - User accounts
- `dataset_0d96ebff_3884_4b4c_b57b_27afd81e941f` - Insurance data (age, bmi, charges, etc.)
- `dataset_94301004_8e4d_44d4_8cc4_3ef1083a10fe` - Sales data (Ship, Mode, Segment, Sales, Profit, etc.)

#### Valid Test Queries:

1. **Basic queries:**
   - "Show me all datasets"
   - "Show me the first 10 rows from datasets"
   - "List all dashboards"

2. **Insurance data queries:**
   - "Show me all data from dataset_0d96ebff_3884_4b4c_b57b_27afd81e941f"
   - "What is the average age in dataset_0d96ebff_3884_4b4c_b57b_27afd81e941f?"
   - "Show me records where smoker is true"

3. **Sales data queries:**
   - "Show me all sales data from dataset_94301004_8e4d_44d4_8cc4_3ef1083a10fe"
   - "What is the total profit in dataset_94301004_8e4d_44d4_8cc4_3ef1083a10fe?"

#### Invalid Queries (Should Show Helpful Errors):

These will trigger validation and show available tables:
- "Show me all customers" ❌ (customers table doesn't exist)
- "List all orders" ❌ (orders table doesn't exist)
- "Show me products" ❌ (products table doesn't exist)

Expected error: "Cannot answer this query. The question references tables that don't exist (customers). Available tables are: datasets, dashboards, ml_models, users, ..."

## What Happens Behind the Scenes

1. **User enters natural language query** → Frontend sends to backend
2. **Backend fetches database schema** → Gets all tables and columns
3. **LLM translates to SQL** → Groq API converts NL to SQL
4. **Validation layer checks:**
   - Only SELECT statements allowed
   - No dangerous keywords (DROP, DELETE, etc.)
   - All referenced tables exist in schema
   - If validation fails, retries once with stricter prompt
5. **Execute query** → Runs SQL against database
6. **Save as dataset** → Results saved as CSV and dataset record
7. **Return results** → Shows preview and allows dashboard creation

## Recent Fixes

✅ **Table validation** - Prevents LLM from hallucinating non-existent tables
✅ **Auto-retry mechanism** - Retries with stricter prompt if validation fails
✅ **Better error messages** - Shows available tables when query references invalid ones
✅ **Theme-aware styling** - Uses CSS variables for proper dark/light mode
✅ **Dynamic example queries** - Shows clickable examples based on actual schema
✅ **Improved LLM prompt** - Explicitly lists available tables multiple times

## Troubleshooting

**Error: "no such table: customers"**
- This means the LLM generated a query for a table that doesn't exist
- The new validation layer should catch this and show available tables
- Try rephrasing your query to use the actual table names shown in the UI

**Error: "Connection refused"**
- Database server is not running (for PostgreSQL/MySQL)
- For SQLite, check that the database file path is correct

**Error: "Only SELECT queries are allowed"**
- Security feature - only read operations are permitted
- Cannot use DELETE, UPDATE, INSERT, DROP, etc.
