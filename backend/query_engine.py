import pandas as pd
import re

def simple_english_query(df, query: str):
    query = query.lower().strip()

    # 1️⃣ First N rows
    if "first" in query:
        nums = re.findall(r"\d+", query)
        if nums:
            n = int(nums[0])
            return df.head(n)

    # 2️⃣ Row range
    if "rows" in query and "to" in query:
        nums = list(map(int, re.findall(r"\d+", query)))
        if len(nums) == 2:
            return df.iloc[nums[0]:nums[1]]

    # 3️⃣ Unique column values
    if "unique" in query:
        for col in df.columns:
            if col.lower() in query:
                return df[col].unique()

    # 4️⃣ Numeric filters (greater / less)
    m = re.findall(r"(.*)greater than ([\d\.]+)", query)
    if m:
        col, val = m[0]
        col = col.strip()
        val = float(val)
        return df[df[col] > val]

    m = re.findall(r"(.*)less than ([\d\.]+)", query)
    if m:
        col, val = m[0]
        col = col.strip()
        val = float(val)
        return df[df[col] < val]

    # 5️⃣ Column + value match (string / numeric)
    for col in df.columns:
        if col.lower() in query:
            val_str = query.replace(col.lower(), "").strip()
            # check if column is numeric
            if pd.api.types.is_numeric_dtype(df[col]):
                try:
                    val_num = float(val_str)
                    return df[df[col] == val_num]
                except:
                    return f"Could not convert '{val_str}' to numeric for column '{col}'"
            else:
                # object / string column
                return df[df[col].astype(str).str.contains(val_str, case=False)]

    return "Query not understood"
