-- Liquidity trough + riskiest-10% flag in plain SQL (window functions: Snowflake, BigQuery, Postgres, DuckDB, SQLite 3.25+).
-- Same definition as engine.ltr_table(): last 6 months up to :asof, lowest end-of-day balance / average daily balance,
-- scored only with 12+ months of history, riskiest 10% = lowest ratios. Checked equal to the Python in tests.
WITH hist AS (
  SELECT account_id, month, min_balance, avg_daily_balance,
         ROW_NUMBER() OVER (PARTITION BY account_id ORDER BY month DESC) AS rn,
         COUNT(*)     OVER (PARTITION BY account_id)                    AS n_months
  FROM monthly_summary
  WHERE month <= :asof
),
trough AS (
  SELECT account_id,
         MIN(min_balance)       AS min_balance,
         AVG(avg_daily_balance) AS avg_balance,
         CASE WHEN AVG(avg_daily_balance) > 0 THEN MIN(min_balance) / AVG(avg_daily_balance) ELSE -1.0 END AS ltr,
         MAX(n_months)          AS n_months
  FROM hist
  WHERE rn <= 6
  GROUP BY account_id
)
SELECT account_id, min_balance, avg_balance, ltr, n_months,
       CASE WHEN n_months >= 12 THEN CUME_DIST() OVER (PARTITION BY n_months >= 12 ORDER BY ltr) END AS ltr_pct_rank,
       (n_months >= 12 AND CUME_DIST() OVER (PARTITION BY n_months >= 12 ORDER BY ltr) <= 0.10)       AS riskiest_10
FROM trough
ORDER BY account_id;
