# Task C5
from fastapi import APIRouter, Depends, UploadFile, File, Form
from app.db.session import get_orkuflaedi_session
from sqlalchemy.orm import Session
from app.services.service import (
    get_monthly_energy_flow_data,
    get_monthly_customer_usage_data,
    get_monthly_plant_loss_ratios_data
)

from app.utils.validate_date_range import validate_date_range_helper
from datetime import datetime

router = APIRouter()
db_name = "OrkuFlaediIsland"

# -------------------------------------------------------------------
# Endpoint 1
@router.get("/get-monthly-energy-flow")
def get_monthly_energy_flow(
    from_date: datetime | None = None,
    to_date: datetime | None = None,
    db: Session = Depends(get_orkuflaedi_session)
):
    print(f"Calling [GET] /{db_name}/get-monthly-energy-flow")

    from_date, to_date = validate_date_range_helper(
        from_date,
        to_date,
        datetime(2025, 1, 1, 0, 0),
        datetime(2026, 1, 1, 0, 0)
    )

    results = get_monthly_energy_flow_data(from_date, to_date, db)
    return results

# -------------------------------------------------------------------
# Endpoint 2
@router.get("/get-monthly-customer-usage")
def get_monthly_customer_usage(
    from_date: datetime | None = None,
    to_date: datetime | None = None,
    db: Session = Depends(get_orkuflaedi_session)
):
    from_date, to_date = validate_date_range_helper(
        from_date,
        to_date,
        datetime(2025, 1, 1, 0, 0),
        datetime(2026, 1, 1, 0, 0)
    )

    results = get_monthly_customer_usage_data(from_date, to_date, db)
    return results
    
# -------------------------------------------------------------------
# Endpoint 3
@router.get("/get-monthly-plant-þloss-ratios")
def get_monthly_plant_loss_ratios(
    from_date: datetime | None = None,
    to_date: datetime | None = None,
    db: Session = Depends(get_orkuflaedi_session)
):
    from_date, to_date = validate_date_range_helper(
        from_date,
        to_date,
        datetime(2025, 1, 1, 0, 0),
        datetime(2026, 1, 1, 0, 0)
    )
    results = get_monthly_plant_loss_ratios_data(from_date, to_date, db)
    return results
