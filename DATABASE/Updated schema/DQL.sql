-- Task C5
-- Query 1: Monthly energy flow per power plant
SELECT
    oe.heiti                            AS power_plant_source,
    m.tegund_maelingar                  AS measurement_type,
    EXTRACT(YEAR  FROM m.timi)::INT     AS year,
    EXTRACT(MONTH FROM m.timi)::INT     AS month,
    SUM(m.gildi_kwh)                    AS total_kwh
FROM raforka.maelingar m
JOIN raforka.virkjanir  v  ON v.id  = m.virkjun_id
JOIN raforka.orku_eining oe ON oe.id = v.id
WHERE m.timi BETWEEN :from_date AND :to_date
GROUP BY
    oe.heiti,
    m.tegund_maelingar,
    EXTRACT(YEAR  FROM m.timi),
    EXTRACT(MONTH FROM m.timi)
ORDER BY
    oe.heiti ASC,
    month    ASC,
    total_kwh DESC;
