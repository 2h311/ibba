from pydantic import BaseModel


class IbbaProfileFields(BaseModel):
    url: str = "Broker URL"
    image_link: str = "Broker Image Link"
    name: str = "Broker Name"
    is_cbi: str = "Broker is CBI"
    member_date: str = "Broker Member Date"
    email: str = "Broker Email"
    phone: str = "Broker Phone"
    city: str = "Broker City"
    address: str = "Broker Address"
    website: str = "Broker Website"
    speciality: str = "Broker Speciality"
