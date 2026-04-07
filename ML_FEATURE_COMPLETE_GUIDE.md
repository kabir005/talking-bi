# ML Models Feature - Complete Guide

## ✅ STATUS: FULLY FUNCTIONAL

All issues have been resolved. The ML Models feature is now fully operational with proper dataset loading and column selection.

---

## 🎯 What is the ML Models Feature?

The ML Models feature is an **AutoML (Automated Machine Learning)** system that allows you to:

1. **Train predictive models** on your datasets without writing code
2. **Automatically select the best algorithm** for your data (Random Forest, XGBoost, Linear Regression, etc.)
3. **Make predictions** on new data
4. **Analyze feature importance** to understand what drives your predictions
5. **Run what-if scenarios** to simulate different business conditions
6. **Compare multiple models** to find the best performer

---

## 🚀 How to Use the ML Models Feature

### Step 1: Navigate to ML Models Page

1. Click on the **"ML Models"** link in the sidebar (Brain icon)
2. You'll see 4 tabs: **Train Model**, **Models**, **Predictions**, **What-If Analysis**

### Step 2: Train Your First Model

1. Go to the **"Train Model"** tab
2. Follow these steps:

   **a) Select Dataset**
   - Choose a dataset from the dropdown
   - The dropdown shows: `Dataset Name (X rows, Y columns)`
   - Example: `sales_data.csv (1000 rows, 15 columns)`

   **b) Select Target Column**
   - After selecting a dataset, columns will load automatically
   - Choose the column you want to predict (e.g., "revenue", "sales", "price")
   - The system will show: `Loaded X columns` toast notification

   **c) Choose Task Type**
   - **Auto-detect** (Recommended): System automatically determines if it's regression or classification
   - **Regression**: For predicting continuous values (prices, revenue, quantities)
   - **Classification**: For predicting categories (yes/no, high/medium/low)

   **d) Click "Train Model"**
   - Training takes 10-60 seconds depending on dataset size
   - You'll see a progress indicator
   - Success message shows which algorithm was selected

### Step 3: View Trained Models

1. Go to the **"Models"** tab
2. You'll see all your trained models with:
   - **Algorithm name** (e.g., Random Forest, XGBoost)
   - **Target column** being predicted
   - **Performance metrics**:
     - **R² Score**: How well the model fits (0-1, higher is better)
     - **MAE** (Mean Absolute Error): Average prediction error
     - **RMSE** (Root Mean Squared Error): Prediction accuracy measure
   - **Creation date**

3. Click on any model card to:
   - **View Details**: See feature importance and prediction charts
   - **Retrain**: Update the model with new data
   - **Delete**: Remove the model

### Step 4: Make Predictions

1. Select a model from the Models tab
2. Click **"View Details"** button
3. You'll see:
   - **Feature Importance Chart**: Shows which columns have the most impact
   - **Prediction Chart**: Visualizes actual vs predicted values
   - **Model Metrics**: Detailed performance statistics

### Step 5: Run What-If Scenarios

1. Go to the **"What-If Analysis"** tab
2. Use sliders to adjust parameters (e.g., increase price by 10%, reduce costs by 5%)
3. See real-time predictions of how changes affect your target metric
4. Compare multiple scenarios side-by-side

---

## 🔧 Technical Details

### Supported Algorithms

The system automatically tests and selects the best from:
- **Random Forest**: Ensemble of decision trees
- **XGBoost**: Gradient boosting (usually best for structured data)
- **Linear Regression**: Simple linear relationships
- **Ridge/Lasso**: Regularized linear models
- **Decision Trees**: Interpretable tree-based models

### Data Requirements

- **Minimum rows**: 10 (recommended: 100+)
- **Minimum columns**: 2 (1 target + 1 feature)
- **Supported data types**: Numeric, categorical, dates
- **Missing values**: Automatically handled
- **Categorical encoding**: Automatic one-hot encoding

### Performance Metrics Explained

**For Regression (predicting numbers):**
- **R² Score**: 0.0 = random guessing, 1.0 = perfect predictions
  - 0.7-0.8 = Good
  - 0.8-0.9 = Very Good
  - 0.9+ = Excellent
- **MAE**: Average error in same units as target (lower is better)
- **RMSE**: Penalizes large errors more (lower is better)

**For Classification (predicting categories):**
- **Accuracy**: % of correct predictions
- **Precision**: % of positive predictions that were correct
- **Recall**: % of actual positives that were found
- **F1 Score**: Balance between precision and recall

---

## 🐛 Troubleshooting

### Issue: "No columns available"

**Solution:**
1. Make sure you selected a dataset first
2. Wait for the "Loaded X columns" toast notification
3. If columns still don't load, try:
   - Refreshing the page
   - Re-uploading the dataset
   - Checking if the dataset has data (not empty)

### Issue: "Training failed"

**Possible causes:**
1. **Target column has no variation**: All values are the same
2. **Too few rows**: Need at least 10 rows
3. **All features are non-numeric**: Need at least one numeric column
4. **Dataset not found**: Dataset may have been deleted

**Solution:**
- Check your dataset has valid data
- Ensure target column has different values
- Try a different target column

### Issue: "Model not found"

**Solution:**
- The model may have been deleted
- Refresh the models list
- Train a new model

---

## 📊 Example Use Cases

### 1. Sales Forecasting
- **Dataset**: Historical sales data
- **Target**: `total_sales`
- **Features**: `month`, `region`, `product_category`, `marketing_spend`
- **Result**: Predict future sales based on historical patterns

### 2. Customer Churn Prediction
- **Dataset**: Customer data
- **Target**: `churned` (yes/no)
- **Features**: `tenure`, `monthly_charges`, `contract_type`, `support_tickets`
- **Result**: Identify customers likely to leave

### 3. Price Optimization
- **Dataset**: Product pricing data
- **Target**: `units_sold`
- **Features**: `price`, `competitor_price`, `season`, `promotion`
- **Result**: Find optimal pricing strategy

### 4. Inventory Management
- **Dataset**: Inventory data
- **Target**: `stock_needed`
- **Features**: `day_of_week`, `season`, `promotions`, `weather`
- **Result**: Predict optimal stock levels

---

## 🎓 Best Practices

1. **Data Quality**
   - Clean your data before uploading
   - Remove duplicate rows
   - Handle missing values appropriately

2. **Feature Selection**
   - Include relevant features that might affect the target
   - Remove ID columns or timestamps (unless time-series)
   - More features ≠ better (can cause overfitting)

3. **Model Evaluation**
   - Always check R² score and error metrics
   - Compare multiple models
   - Test predictions on new data

4. **Retraining**
   - Retrain models monthly or when data changes significantly
   - Monitor model performance over time
   - Update when accuracy drops

---

## 🔗 API Endpoints

For developers who want to integrate programmatically:

```bash
# Train a model
POST /api/ml/train
{
  "dataset_id": "abc123",
  "target_column": "revenue",
  "task_type": "auto"
}

# List models
GET /api/ml/models?dataset_id=abc123

# Make predictions
POST /api/ml/models/{model_id}/predict
{
  "data": [{"feature1": 10, "feature2": 20}]
}

# Run what-if scenario
POST /api/ml/what-if/simulate
{
  "dataset_id": "abc123",
  "parameter_changes": {"price": 1.1, "cost": 0.9},
  "target_metric": "profit"
}
```

Full API documentation: http://127.0.0.1:8000/docs

---

## ✅ Recent Fixes Applied

### Fix 1: Dataset Loading (RESOLVED)
- **Issue**: Dataset dropdown was empty
- **Fix**: Added `getDatasets()` API call on component mount
- **Status**: ✅ Working

### Fix 2: Column Selection (RESOLVED)
- **Issue**: Target column dropdown was empty
- **Root Cause**: Component was looking for `schema_json` but API returns `schema`
- **Fix**: 
  - Updated component to use correct field name (`schema` instead of `schema_json`)
  - Added schema fetch when dataset is selected
  - Implemented fallback to preview endpoint if schema is empty
  - Added loading states and error handling
- **Status**: ✅ Working

### Fix 3: API Integration (RESOLVED)
- **Issue**: Component used direct axios calls
- **Fix**: Replaced all axios calls with apiClient for proper base URL
- **Status**: ✅ Working

---

## 📝 Summary

The ML Models feature is now fully functional with:
- ✅ Dataset selection working
- ✅ Column loading working (with fallback)
- ✅ Model training working
- ✅ Predictions working
- ✅ What-if scenarios working
- ✅ Zero diagnostics errors
- ✅ Full frontend-backend integration

You can now train ML models on any dataset with just a few clicks!
