from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict

import models
import schemas
from database import get_db
from auth import get_current_user

router = APIRouter(prefix="/api/bills", tags=["bills"])

@router.get("", response_model=List[schemas.BillResponse])
def get_bills(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    return (
        db.query(models.BillRecord)
        .filter(models.BillRecord.owner_id == current_user.id)
        .order_by(models.BillRecord.created_at.desc())
        .all()
    )


@router.post("/itemized", response_model=schemas.ItemizedBillResponse)
def create_itemized_bill(
    bill: schemas.ItemizedBillCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    if not bill.items:
        raise HTTPException(status_code=400, detail="Bill cannot be empty")

    subtotal = sum(item.price for item in bill.items)
    tip_multiplier = 1 + (bill.tip_percentage / 100)
    grand_total = round(subtotal * tip_multiplier, 2)

    # Calculate each person's share
    debtors_shares: Dict[str, float] = {}
    for item in bill.items:
        if not item.consumers:
            continue
        share_per_consumer = item.price / len(item.consumers)
        share_with_tip = share_per_consumer * tip_multiplier
        for consumer in item.consumers:
            consumer_name = consumer.strip()
            if consumer_name not in debtors_shares:
                debtors_shares[consumer_name] = 0.0
            debtors_shares[consumer_name] += share_with_tip

    # Round final amounts
    for consumer in debtors_shares:
        debtors_shares[consumer] = round(debtors_shares[consumer], 2)

    # Save bill to DB
    db_bill = models.BillRecord(
        title=bill.title,
        total_amount=grand_total,
        tip_percentage=bill.tip_percentage,
        owner_id=current_user.id
    )
    db.add(db_bill)
    db.commit()
    db.refresh(db_bill)

    # Save items to DB
    for item in bill.items:
        db_item = models.ItemRecord(
            name=item.name,
            price=item.price,
            consumers=", ".join(item.consumers),
            bill_id=db_bill.id
        )
        db.add(db_item)
    db.commit()

    return {
        "bill_id": db_bill.id,
        "title": db_bill.title,
        "grand_total": grand_total,
        "shares": debtors_shares
    }


@router.delete("/{bill_id}")
def delete_bill(
    bill_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    db_bill = (
        db.query(models.BillRecord)
        .filter(
            models.BillRecord.id == bill_id,
            models.BillRecord.owner_id == current_user.id
        )
        .first()
    )
    if not db_bill:
        raise HTTPException(status_code=404, detail="Bill not found or unauthorized")
    db.delete(db_bill)
    db.commit()
    return {"message": "Deleted successfully"}