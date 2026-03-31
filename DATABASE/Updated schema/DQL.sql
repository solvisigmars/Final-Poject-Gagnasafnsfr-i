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
WHERE m.timi >= '2025-01-01 00:00:00'
  AND m.timi <  '2026-01-01 00:00:00'
GROUP BY
    oe.heiti,
    m.tegund_maelingar,
    EXTRACT(YEAR  FROM m.timi),
    EXTRACT(MONTH FROM m.timi)
ORDER BY
    oe.heiti ASC,
    year ASC,
    month ASC,
    total_kwh DESC;


-- Query 2: Monthly energy usage per customer

SELECT
    oe.heiti                        AS power_plant_source,
    EXTRACT(YEAR FROM m.timi)::INT  AS year,
    EXTRACT(MONTH FROM m.timi)::INT AS month,
    c.lysing                        AS customer_name,
    SUM(m.gildi_kwh)                AS total_kwh
FROM raforka.maelingar m
JOIN raforka.virkjanir v
    ON v.id = m.virkjun_id
JOIN raforka.orku_eining oe
    ON oe.id = v.id
JOIN raforka.vidskiptavinir c
    ON c.id = m.vidskiptavinur_id
WHERE m.timi >= '2025-01-01 00:00:00'
  AND m.timi <  '2026-01-01 00:00:00'
  AND m.tegund_maelingar = 'Úttekt'
GROUP BY
    oe.heiti,
    EXTRACT(YEAR FROM m.timi),
    EXTRACT(MONTH FROM m.timi),
    c.lysing
ORDER BY
    oe.heiti ASC,
    year ASC,
    month ASC,
    customer_name ASC;


-- Query 3: Monthly energy loss ratio per power plant

CREATE OR REPLACE VIEW raforka.monthly_plant_totals AS
SELECT
    oe.heiti                        AS power_plant_source,
    EXTRACT(YEAR FROM m.timi)::INT  AS year,
    EXTRACT(MONTH FROM m.timi)::INT AS month,
    SUM(CASE
            WHEN m.tegund_maelingar = 'Framleiðsla' THEN m.gildi_kwh
            ELSE 0
        END) AS framleidsla_sum,
    SUM(CASE
            WHEN m.tegund_maelingar = 'Innmötun' THEN m.gildi_kwh
            ELSE 0
        END) AS innmotun_sum,
    SUM(CASE
            WHEN m.tegund_maelingar = 'Úttekt' THEN m.gildi_kwh
            ELSE 0
        END) AS uttekt_sum
FROM raforka.maelingar m
JOIN raforka.virkjanir v
    ON v.id = m.virkjun_id
JOIN raforka.orku_eining oe
    ON oe.id = v.id
WHERE m.timi >= '2025-01-01 00:00:00'
  AND m.timi <  '2026-01-01 00:00:00'
GROUP BY
    oe.heiti,
    EXTRACT(YEAR FROM m.timi),
    EXTRACT(MONTH FROM m.timi);

SELECT
    power_plant_source,
    AVG((framleidsla_sum - innmotun_sum) / NULLIF(framleidsla_sum, 0)) AS plant_to_substation_loss_ratio,
    AVG((framleidsla_sum - uttekt_sum) / NULLIF(framleidsla_sum, 0))   AS total_system_loss_ratio
FROM raforka.monthly_plant_totals
GROUP BY power_plant_source
ORDER BY power_plant_source;

