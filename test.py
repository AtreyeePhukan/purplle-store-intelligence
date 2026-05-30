import pandas as pd

df = pd.read_csv(
    "resources\Brigade_Bangalore_10_April_26 (1)bc6219c.csv"
)

print(df["order_id"].nunique())
print(df["total_amount"].sum())