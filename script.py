import requests, os, sys, datetime
import pandas as pd
url = "https://iss.moex.com/iss/engines/stock/markets/shares/boards/TQBR/securities.json"
params = {"securities.columns": "SECID,SECNAME,ISIN,SECTYPE,LISTLEVEL",
    "marketdata.columns": "SECID,BID,OFFER"}
data = requests.get(url, params=params, headers={"Accept": "application/json"}).json()
df = (pd.merge(
        pd.DataFrame(data["securities"]["data"], columns=data["securities"]["columns"]),
        pd.DataFrame(data["marketdata"]["data"], columns=data["marketdata"]["columns"]),
        on="SECID")
    .dropna(subset=["BID", "OFFER"]).assign(
        BID=lambda x: pd.to_numeric(x["BID"], errors="coerce"),
        OFFER=lambda x: pd.to_numeric(x["OFFER"], errors="coerce"),
        PRICE=lambda x: (x["BID"] + x["OFFER"]) / 2)
    .drop(columns=["BID", "OFFER"])
    .rename(columns={"SECTYPE":"TYPE","SECID":"TICKER","SECNAME":"NAME","LISTLEVEL":"LL"}))
df["TYPE"] = df["TYPE"].astype(str).replace({"1": "АО", "2": "АП"})
cols = ["LL"] + [c for c in df.columns if c not in ["LL", "ISIN"]] + ["ISIN"]
df = df[cols]
df = df.sort_values(by=["LL", "TICKER"], ascending=[True, True])
with open("quotes.md", "w", encoding="utf-8") as f:
    f.write(df.to_markdown(index=False))
print("✅ Файл успешно сохранён: quotes.md")
