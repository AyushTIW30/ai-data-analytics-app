import pandas as pd

def generate_basic_insights(df: pd.DataFrame):
    insights = {}

    # Shape
    insights["rows"] = df.shape[0]
    insights["columns"] = df.shape[1]

    # Column types
    insights["numeric_columns"] = df.select_dtypes(include="number").columns.tolist()
    insights["categorical_columns"] = df.select_dtypes(exclude="number").columns.tolist()

    # Missing values
    insights["missing_values"] = df.isnull().sum().to_dict()

    # Numeric stats
    numeric_summary = {}
    for col in insights["numeric_columns"]:
        numeric_summary[col] = {
            "min": float(df[col].min()),
            "max": float(df[col].max()),
            "mean": float(df[col].mean())
        }

    insights["numeric_summary"] = numeric_summary

    return insights
def generate_text_insights(insights: dict):
    text = []

    text.append(f"The dataset contains {insights['rows']} rows and {insights['columns']} columns.")

    if insights["numeric_columns"]:
        text.append(f"There are {len(insights['numeric_columns'])} numeric columns suitable for analysis.")

    high_missing = [
        col for col, val in insights["missing_values"].items() if val > 0
    ]

    if high_missing:
        text.append(f"Columns with missing values: {', '.join(high_missing)}.")
    else:
        text.append("No missing values detected in the dataset.")

    return text
    