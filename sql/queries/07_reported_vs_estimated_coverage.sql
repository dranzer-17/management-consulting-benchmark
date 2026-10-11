-- How much of the firm-scale data is reported versus estimated (Set 3)
SELECT f.firm_name, s.type, COUNT(*) AS data_points
FROM fact_firm_scale s JOIN dim_firm f USING (firm_id)
GROUP BY f.firm_name, s.type
ORDER BY f.firm_name, s.type;
