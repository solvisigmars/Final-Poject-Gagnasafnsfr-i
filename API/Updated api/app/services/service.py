# Task C5
from fastapi import UploadFile, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.models.parsed_data.test_measurement_data import TestMeasurementData
from app.parsers.parse_test_measurment_csv import parse_test_measurement_csv
from app.utils.validate_file_type import validate_file_type
from datetime import datetime

# -------------------------------------------------------------------
# Service 1
def get_monthly_energy_flow_data(
    from_date: datetime,
    to_date: datetime,
    db: Session
):
    query = '''
        SELECT
          oe.heiti                            AS power_plant_source,
          m.tegund_maelingar                  AS measurement_type,
          EXTRACT(YEAR  FROM m.timi)::INT     AS year,
          EXTRACT(MONTH FROM m.timi)::INT     AS month,
          SUM(m.gildi_kwh)                    AS total_kwh
        FROM raforka.maelingar m
        JOIN raforka.virkjanir  v  ON v.id  = m.virkjun_id
        JOIN raforka.orku_eining oe ON oe.id = v.id
        WHERE m.timi >= :from_date
          AND m.timi <  :to_date
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
            '''

    result = db.execute(text(query), {
        "from_date": from_date,
        "to_date": to_date
    })
    return result.mappings().all()

# -------------------------------------------------------------------
# Service 2
def  get_monthly_customer_usage_data(
    from_date: datetime,
    to_date: datetime,
    db: Session
):
    query = '''
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
        WHERE m.timi >= :from_date
          AND m.timi <  :to_date
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
    '''

    result = db.execute(text(query), {
        "from_date": from_date,
        "to_date": to_date
    })
    return result.mappings().all()

# -------------------------------------------------------------------
# Service 3
def get_monthly_plant_loss_ratios_data(
    from_date: datetime,
    to_date: datetime,
    db: Session
):
    query = '''
    WITH monthly_plant_totals AS (
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
    WHERE m.timi >= :from_date
      AND m.timi <  :to_date
    GROUP BY
        oe.heiti,
        EXTRACT(YEAR FROM m.timi),
        EXTRACT(MONTH FROM m.timi)
    )

    SELECT
        power_plant_source,
        AVG((framleidsla_sum - innmotun_sum) / NULLIF(framleidsla_sum, 0)) AS plant_to_substation_loss_ratio,
        AVG((framleidsla_sum - uttekt_sum) / NULLIF(framleidsla_sum, 0))   AS total_system_loss_ratio
    FROM monthly_plant_totals
    GROUP BY power_plant_source
    ORDER BY power_plant_source;
    '''

    result = db.execute(text(query), {
        "from_date": from_date,
        "to_date": to_date
    })
    return result.mappings().all()