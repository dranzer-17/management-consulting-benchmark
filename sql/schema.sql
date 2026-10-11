-- SQLite schema for the benchmarking database. Built by src/build_database.py

CREATE TABLE dim_firm (
    firm_id   INTEGER PRIMARY KEY,
    firm_name TEXT NOT NULL UNIQUE
);

-- H-1B LCA filings (Sets 1 and 4)
CREATE TABLE fact_lca (
    case_number    TEXT PRIMARY KEY,
    firm_id        INTEGER NOT NULL REFERENCES dim_firm(firm_id),
    fiscal_year    INTEGER NOT NULL,
    case_status    TEXT,
    certified      INTEGER NOT NULL,      -- 1 if status starts with CERTIFIED
    job_title      TEXT,
    soc_code       TEXT,
    soc_title      TEXT,
    is_technical   INTEGER NOT NULL,      -- 1 if SOC major group 15
    worksite_state TEXT,
    worksite_city  TEXT,
    positions      INTEGER,
    wage_annual    REAL                   -- annualized offered wage, USD
);

-- Federal prime contract awards (Set 2)
CREATE TABLE fact_award (
    award_id     TEXT,
    firm_id      INTEGER NOT NULL REFERENCES dim_firm(firm_id),
    fiscal_year  INTEGER,
    agency       TEXT,
    sub_agency   TEXT,
    award_usd    REAL,
    naics_desc   TEXT,
    psc_desc     TEXT,
    PRIMARY KEY (firm_id, award_id)
);

-- Sourced firm-level scale points (Set 3)
CREATE TABLE fact_firm_scale (
    firm_id     INTEGER NOT NULL REFERENCES dim_firm(firm_id),
    year        INTEGER NOT NULL,
    metric      TEXT NOT NULL,
    value       REAL NOT NULL,
    unit        TEXT,
    type        TEXT CHECK (type IN ('reported', 'estimated')),
    confidence  TEXT CHECK (confidence IN ('high', 'medium', 'low')),
    source_url  TEXT,
    note        TEXT,
    PRIMARY KEY (firm_id, year, metric)
);
