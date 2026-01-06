import re
import pandas as pd

def simple_english_query(df, query: str):
    query = query.lower().strip()
    df_filtered = df.copy()

    # Split multiple conditions by 'and'
    conditions = [q.strip() for q in re.split(r"\band\b", query)]

    for cond in conditions:
        # 1. first N rows
        if "first" in cond:
            n = int(re.findall(r"\d+", cond)[0])
            df_filtered = df_filtered.head(n)
            continue

        # 2. Row range
        if "rows" in cond and "to" in cond:
            nums = list(map(int, re.findall(r"\d+", cond)))
            df_filtered = df_filtered.iloc[nums[0]:nums[1]]
            continue

        # 3. Unique column values
        if "unique" in cond:
            for col in df.columns:
                if col.lower() in cond:
                    df_filtered = pd.DataFrame(df_filtered[col].unique(), columns=[col])
            continue

        # 4. Numeric filters
        m = re.findall(r"(.*)greater than (\d+\.?\d*)", cond)
        if m:
            col, val = m[0]
            col = col.strip()
            val = float(val)
            if col in df_filtered.columns:
                df_filtered = df_filtered[df_filtered[col] > val]
            continue

        m = re.findall(r"(.*)less than (\d+\.?\d*)", cond)
        if m:
            col, val = m[0]
            col = col.strip()
            val = float(val)
            if col in df_filtered.columns:
                df_filtered = df_filtered[df_filtered[col] < val]
            continue

        # 5. Column + value match
        matched = False
        for col in df.columns:
            if col.lower() in cond:
                val = cond.replace(col.lower(), "").strip()
                df_filtered = df_filtered[df_filtered[col].astype(str).str.contains(val, case=False)]
                matched = True
                break

        if not matched:
            return "Query not understood"

    return df_filtered
