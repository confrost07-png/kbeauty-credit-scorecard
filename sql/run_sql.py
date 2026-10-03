"""processed CSV를 SQLite 메모리 DB에 적재하고 scorecard_check.sql을 실행한다. (프로젝트 루트에서 실행)"""
import sqlite3
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "data" / "processed"
con = sqlite3.connect(":memory:")
pd.read_csv(P / "comparison_data.csv", encoding="utf-8-sig").to_sql("comparison", con, index=False)
pd.read_csv(P / "scorecard.csv", encoding="utf-8-sig").to_sql("scorecard", con, index=False)
sql = (ROOT / "sql" / "scorecard_check.sql").read_text(encoding="utf-8")
for i, stmt in enumerate(s for s in sql.split(";") if "SELECT" in s.upper()):
    print(f"\n[Query {i + 1}]")
    print(pd.read_sql(stmt, con).to_string(index=False))
