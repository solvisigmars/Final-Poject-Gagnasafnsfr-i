-- Task A2
-- 1

SELECT eining_heiti AS power_plant_sorce, CAST(EXTRACT(YEAR FROM timi) AS integer) AS year,CAST(EXTRACT(MONTH FROM timi)AS integer) as month,tegund_maelingar as mesurement_type, SUM(gildi_kwh) AS total_kwh
FROM raforka_legacy.orku_maelingar
WHERE eining_heiti LIKE 'P%'
GROUP BY eining_heiti, EXTRACT(YEAR FROM timi), EXTRACT(MONTH FROM timi), tegund_maelingar
ORDER BY eining_heiti, month ASC,total_kwh DESC;

------------------------------------------------------------------------------------------------------
-- 2

SELECT eining_heiti AS power_plants_sorce, CAST(EXTRACT(YEAR FROM timi) AS integer) AS year, CAST(EXTRACT(MONTH FROM timi) AS integer) AS month, notandi_heiti AS customer_name, SUM(gildi_kwh) AS total_kwh
FROM raforka_legacy.orku_maelingar
WHERE eining_heiti LIKE 'P%'
AND notandi_heiti IS NOT NULL
AND tegund_maelingar = 'Úttekt'
GROUP BY eining_heiti, EXTRACT(YEAR FROM timi), EXTRACT(MONTH FROM timi), customer_name
ORDER BY eining_heiti, month ASC, customer_name ASC;

------------------------------------------------------------------------------------------------------
--3

--DROP VIEW raforka_legacy.monthly_plant_totals;
CREATE VIEW raforka_legacy.monthly_plant_totals AS
SELECT eining_heiti, DATE_PART('year', timi) AS year, DATE_PART('month', timi) AS month,
    SUM(
		CASE WHEN tegund_maelingar = 'Framleiðsla' 
		THEN gildi_kwh 
		END
		) AS framleidslaSum,
		
    SUM(
		CASE WHEN tegund_maelingar = 'Innmötun' 
		THEN gildi_kwh 
		END) AS innmotunSum,
		
    SUM(CASE WHEN tegund_maelingar = 'Úttekt' 
		THEN gildi_kwh 
		END) AS uttektSum
		
FROM raforka_legacy.orku_maelingar
WHERE eining_heiti LIKE 'P%'
GROUP BY eining_heiti, DATE_PART('year', timi), DATE_PART('month', timi);

SELECT
    eining_heiti AS powerPlant,
    AVG((framleidslaSum - innmotunSum) / framleidslaSum) AS plant_to_substation_loss_ratio,
    AVG((framleidslaSum - uttektSum) / framleidslaSum) AS total_system_loss_ratio
FROM raforka_legacy.monthly_plant_totals
GROUP BY eining_heiti
ORDER BY eining_heiti;

