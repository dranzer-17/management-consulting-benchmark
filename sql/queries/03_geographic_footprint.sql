-- Distinct worksite states/cities and top-5 state share of positions (Set 1)
SELECT f.firm_name,
       COUNT(DISTINCT l.worksite_state) AS states,
       COUNT(DISTINCT l.worksite_city)  AS cities,
       ROUND(100.0 * SUM(CASE WHEN l.worksite_state IN ('CA','NY','TX','IL','MA') THEN l.positions ELSE 0 END) / SUM(l.positions), 1) AS pct_positions_in_ca_ny_tx_il_ma
FROM fact_lca l JOIN dim_firm f USING (firm_id)
WHERE l.certified = 1
GROUP BY f.firm_name;
