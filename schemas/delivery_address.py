from pydantic import BaseModel
from typing import Optional

class DeliveryAddress(BaseModel):
    first_name: Optional[str] = None
    last_name: str
    street_address: str
    apartment: Optional[str] = None
    town_city: str
    state: str
    pin_code: str
    phone: str
    country_region: Optional[str] = "India"
    save_info: Optional[bool] = False
