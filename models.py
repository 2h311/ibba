from pydantic import BaseModel


class IbbaProfileFields(BaseModel):
    url: str = "Profile URL"
    image_link: str = "Profile Image Link"
    name: str = "Profile Name"
    is_cbi: str = "Profile is CBI"
    member_date: str = "Profile Member Date"
    email: str = "Profile Email"
    phone: str = "Profile Phone"
    city: str = "Profile City"
    address: str = "Profile Address"
    website: str = "Profile Website"
    speciality: str = "Profile Speciality"
