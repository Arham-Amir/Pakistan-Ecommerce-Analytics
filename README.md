# Pakistan E-Commerce Analytics Dashboard

An interactive business intelligence dashboard built using Python, Pandas, Plotly and Streamlit to analyze Pakistan's largest e-commerce dataset.

## Project Overview

This project explores e-commerce transactions to identify sales patterns, product performance, customer behavior, payment preferences and order statuses.

## Key Features

- Interactive business overview with KPI cards
- Monthly product value trends
- Category performance analysis
- Top 10 product analysis
- Order status analysis
- Payment method comparison
- Executive business insights
- Interactive date, category and payment filters
- Filtered dataset export

## Technologies Used

- Python
- Pandas
- NumPy
- Plotly
- Streamlit

## Dataset

Dataset: Pakistan's Largest E-Commerce Dataset

Source: Kaggle

The dataset covers transactions from July 2016 to August 2018.

## Installation and Setup

1. Clone this repository.
2. Create a virtual environment.
3. Install the required libraries.
4. Place the cleaned CSV dataset in the project folder.
5. Run the Streamlit application.

```bash
git clone YOUR_REPOSITORY_URL
cd Pakistan-Ecommerce-Dashboard

python -m venv venv
```

Activate the environment on Windows:

```powershell
.\venv\Scripts\Activate.ps1
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the dashboard:

```bash
python -m streamlit run app.py
```

## Important Note

Recorded Product Value is calculated as Price × Quantity. It should not be interpreted as verified collected revenue or profit because product cost and confirmed payment collection data are not available.

## Author

Arham Amir

GitHub: https://github.com/Arham-Amir