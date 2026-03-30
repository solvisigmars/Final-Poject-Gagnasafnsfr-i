from fastapi import UploadFile, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.db.tables.orku_einingar import OrkuEiningar
from app.models.orku_einingar_model import OrkuEiningarModel
from app.db.tables.notendur_skraning import NotendurSkraning
from app.models.notendur_skraning_model import NotendurSkraningModel
from app.db.tables.orku_maelingar import OrkuMaelingar
from app.models.orku_maelingar_model import OrkuMaelingarModel
from app.db.tables.test_measurement import TestMeasurement
from app.models.parsed_data.test_measurement_data import TestMeasurementData
from app.parsers.parse_test_measurment_csv import parse_test_measurement_csv
from app.utils.validate_file_type import validate_file_type
from datetime import datetime

def get_orku_einingar_data(
    db: Session
):
    rows = db.query(OrkuEiningar).all()

    return [
        OrkuEiningarModel(
            id=row.id,
            heiti=row.heiti,
            tegund=row.tegund,
            tegund_stod=row.tegund_stod,
            eigandi=row.eigandi,
            ar_uppsett=row.ar_uppsett,
            manudir_uppsett=row.manudir_uppsett,
            dagur_uppsett=row.dagur_uppsett,
            X_HNIT=row.X_HNIT,
            Y_HNIT=row.Y_HNIT,
            tengd_stod=row.tengd_stod,
        ) 
        for row in rows
    ]

def get_notendur_skraning_data(
    db: Session
):
    rows = db.query(NotendurSkraning).all()

    return [
        NotendurSkraningModel(
            id=row.id,
            heiti=row.heiti,
            kennitala=row.kennitala,
            eigandi=row.eigandi,
            ar_stofnad=row.ar_stofnad,
            X_HNIT=row.X_HNIT,
            Y_HNIT=row.Y_HNIT,
        ) 
        for row in rows
    ]

def get_orku_maelingar_data(
    from_date: datetime,
    to_date: datetime,
    limit: int,
    offset: int,
    db: Session,
    eining: str | None = None,
    tegund: str | None = None,
):
    query = db.query(OrkuMaelingar).filter(
        OrkuMaelingar.timi >= from_date,
        OrkuMaelingar.timi <= to_date
    )

    if eining:
        query = query.filter(OrkuMaelingar.eining_heiti == eining)
    if tegund:
        query = query.filter(OrkuMaelingar.tegund_maelingar == tegund)

    rows = (
        query
        .order_by(OrkuMaelingar.timi)
        .limit(limit)
        .offset(offset)
        .all()
    )

    return [
        OrkuMaelingarModel(
            id=row.id,
            eining_heiti=row.eining_heiti,
            tegund_maelingar=row.tegund_maelingar,
            sendandi_maelingar=row.sendandi_maelingar,
            timi=row.timi,
            gildi_kwh=row.gildi_kwh,
            notandi_heiti=row.notandi_heiti
        )
        for row in rows
    ]

async def insert_test_measurement_data(
    file: UploadFile,
    db: Session,
    mode: str = "bulk"
):
    validate_file_type(
        file, 
        allowed_extensions=[".csv"]
    )

    raw_data = await file.read()
    raw_text = raw_data.decode()

    parsed_rows: list[TestMeasurementData]
    parsed_rows = parse_test_measurement_csv(raw_text)

    if not parsed_rows:
        raise HTTPException(status_code=400, detail="No valid rows found")

    try:
        if mode == "single":
            for row in parsed_rows:
                db.add(
                    TestMeasurement(
                        timi=row.timi,
                        value=row.value
                    )
                )
            db.commit()

        elif mode == "bulk":
            insert_data = [
                {
                    "timi": row.timi,
                    "value": row.value
                }
                for row in parsed_rows
            ]
            db.bulk_insert_mappings(TestMeasurement, insert_data)
            db.commit()

        elif mode == "fallback":
            for row in parsed_rows:
                try:
                    db.add(
                        TestMeasurement(
                            timi=row.timi,
                            value=row.value
                        )
                    )
                    db.flush()
                except Exception:
                    db.rollback()
                    continue
            db.commit()
        else:
            raise HTTPException(status_code=400, detail="Invalid mode")

        return {
            "status": 200,
            "rows_processed": len(parsed_rows),
            "mode": mode
        }
    
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    

'''
Part 1 - Service 1: Implement get_monthly_energy_flow_data()
Query orku_maelingar and return monthly energy flow per plant and measurement type.
'''
def get_monthly_energy_flow_data(
    from_date: datetime,
    to_date: datetime,
    db: Session
):
    query = '''
        SELECT 
            eining_heiti AS power_plant_source, 
            CAST(EXTRACT(YEAR FROM timi) AS integer) AS year,
            CAST(EXTRACT(MONTH FROM timi)AS integer) as month,
            tegund_maelingar as measurement_type, 
            SUM(gildi_kwh) AS total_kwh
        FROM raforka_legacy.orku_maelingar
        WHERE eining_heiti LIKE 'P%'
        AND timi >= :from_date
        AND timi < :to_date

        GROUP BY eining_heiti, EXTRACT(YEAR FROM timi), EXTRACT(MONTH FROM timi), tegund_maelingar
        ORDER BY eining_heiti, month ASC,total_kwh DESC;
    '''

    result = db.execute(text(query), {
        "from_date": from_date,
        "to_date": to_date
    })
    return result.mappings().all()

'''
Part 1 - Service 2: Implement get_monthly_company_usage_data()
Query orku_maelingar and return monthly energy usage per company per plant.
'''
def  get_monthly_customer_usage_data(
    from_date: datetime,
    to_date: datetime,
    db: Session
):
    query = '''
        SELECT 
            eining_heiti AS power_plants_sorce, 
            CAST(EXTRACT(YEAR FROM timi) AS integer) AS year, 
            CAST(EXTRACT(MONTH FROM timi) AS integer) AS month, 
            notandi_heiti AS customer_name, 
            SUM(gildi_kwh) AS total_kwh
        FROM raforka_legacy.orku_maelingar
        WHERE eining_heiti LIKE 'P%'
        AND notandi_heiti IS NOT NULL
        AND tegund_maelingar = 'Úttekt'
        AND timi >= :from_date
        AND timi < :to_date

        GROUP BY eining_heiti, EXTRACT(YEAR FROM timi), EXTRACT(MONTH FROM timi), customer_name
        ORDER BY eining_heiti, month ASC, customer_name ASC;
    '''

    result = db.execute(text(query), {
        "from_date": from_date,
        "to_date": to_date
    })
    return result.mappings().all()

'''
Part 1 - Service 3: Implement get_monthly_plant_loss_ratios_data()
Query orku_maelingar and return average monthly loss ratios per plant.
'''
def get_monthly_plant_loss_ratios_data(
    from_date: datetime,
    to_date: datetime,
    db: Session
):
    query = '''
        WITH monthly_plant_totals AS (
            SELECT 
                eining_heiti, 
                DATE_PART('year', timi) AS year, 
                DATE_PART('month', timi) AS month,
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
            AND timi >= :from_date
            AND timi < :to_date
            GROUP BY eining_heiti, DATE_PART('year', timi), DATE_PART('month', timi)
    )

    SELECT
        eining_heiti AS powerPlant,
        AVG((framleidslaSum - innmotunSum) / framleidslaSum) AS plant_to_substation_loss_ratio,
        AVG((framleidslaSum - uttektSum) / framleidslaSum) AS total_system_loss_ratio
        FROM monthly_plant_totals
        GROUP BY eining_heiti
        ORDER BY eining_heiti;
    '''

    result = db.execute(text(query), {
        "from_date": from_date,
        "to_date": to_date
    })
    return result.mappings().all()