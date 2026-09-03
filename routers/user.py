from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database.connection import get_db
from schemas.delivery_address import DeliveryAddress
from services.user_service import update_delivery_address

router = APIRouter(prefix="/users", tags=["Users & Delivery"])

@router.put("/{user_id}/delivery-address")
def set_delivery_address(user_id: int, address_data: DeliveryAddress, db: Session = Depends(get_db)):
    updated_user = update_delivery_address(db, user_id, address_data)
    return {
        "message": "Delivery address updated successfully",
        "user": {
            "id": updated_user.id,
            "first_name": updated_user.first_name,
            "last_name": updated_user.last_name,
            "street_address": updated_user.street_address,
            "apartment": updated_user.apartment,
            "town_city": updated_user.town_city,
            "state": updated_user.state,
            "pin_code": updated_user.pin_code,
            "phone": updated_user.phone
        }
    }
