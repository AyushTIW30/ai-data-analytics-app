import pandas as pd

def get_chart_suggestions(df: pd.DataFrame):
    """
    Returns list of charts to display for each column
    """
    charts = []

    for col in df.columns:
        if pd.api.types.is_numeric_dtype(df[col]):
            charts.append({"column": col, "type": "histogram"})
        elif pd.api.types.is_datetime64_any_dtype(df[col]):
            charts.append({"column": col, "type": "line"})
        elif df[col].dtype == "object" and df[col].nunique() < 20:
            # small categorical → bar + pie
            charts.append({"column": col, "type": "bar"})
            charts.append({"column": col, "type": "pie"})

    return charts
