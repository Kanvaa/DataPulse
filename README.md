# ⚡ DataPulse

**DataPulse** is a clean, modern, and production-ready data cleaning and analytics reporting application. It automates common processing tasks on tabular CSV files (like cleaning date formats, normalising category names, handling empty/null fields, and removing duplicates), flags pricing/quantity anomalies, and provides a stunning, themeable Streamlit dashboard for business reporting.

### 🔗 Live Demo
👉 **[Open Live Web Dashboard](https://datapulse-kanvaa.surge.sh)** *(Hosted free on Surge.sh)*

---

## 🚀 Key Features

1. **Intelligent Data Cleaning**:
   - Standardises and handles mixed date formatting (e.g. standardises into `YYYY-MM-DD`).
   - Automatically drops duplicate rows.
   - Cleans categorical casing (imputes missing text, trims spaces, formats to Title Case).
   - Imputes missing quantities and prices using statistical medians.
2. **Business Anomaly Detection**:
   - Flags non-positive quantities or prices (<= 0).
   - Flags statistical price outliers automatically using the **1.5 * IQR (Interquartile Range)** algorithm.
3. **Interactive Analytics Dashboard**:
   - Features dynamic business metric cards (Revenue, Units Sold, Average Price).
   - Renders interactive charts powered by Plotly (Revenue trend timeline, Category contribution).
   - Clean, custom CSS styling supporting both **Light Mode** and **Dark Mode**.
4. **Flexible Report Export**:
   - Download cleaned and anomaly-flagged data back as a CSV.
   - Download a comprehensive, multi-sheet Excel report containing Cleaned Data, Anomalies, and Business Aggregate summary sheets.

---

## 📂 Project Structure

```text
DataPulse/
│
├── cleaner.py          # Data cleaning logic & string casing formatting
├── reporter.py         # Summary statistics, IQR anomaly detection, and Excel workbook generator
├── app.py              # Streamlit dashboard layout, components, custom CSS theme
├── requirements.txt    # Pinned production library dependencies
├── sample_data.csv     # Messy sales dataset for demonstration purposes
└── README.md           # Getting started, usage, and project layout
```

---

## 🛠️ Installation & Getting Started

### Prerequisites
- Python 3.10 or newer

### 1. Clone or Move to the Project Directory
Navigate into the `DataPulse` directory:
```bash
cd DataPulse
```

### 2. Create and Activate Virtual Environment
On Windows (PowerShell):
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```
On macOS/Linux:
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the Streamlit Dashboard
```bash
streamlit run app.py
```
After executing, Streamlit will print the local network URL (typically `http://localhost:8501`). Open this URL in your web browser.

---

## 💡 How to Use / Demo Workflow

1. Click on **`💡 Load Sample CSV Dataset (Demo)`** to load the pre-configured messy data.
2. Click **`🚀 Run Data Cleaning & Report Pipeline`** to start cleaning, aggregating, and analyzing.
3. Under the **`⚡ Upload & Clean`** tab, inspect the cleaned row statistics and download output files (CSV or Excel).
4. Navigate to **`📊 Analytics Dashboard`** to view key business metrics (Revenue, Units Sold) and interactive Plotly timelines/charts.
5. Review the anomaly logs under **`⚠️ Anomaly Log`** to see what outlier and zero-value records were identified.
