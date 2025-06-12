# This file imports all the models, making them available
# to SQLAlchemy when Base.metadata.create_all() is called.

from .user import User
from .tractor import Tractor
from .field import Field
from .land_usage_plan import LandUsagePlan
from .crop import Crop
from .service_booking import ServiceBooking
from .part import Part
from .notification import Notification
from .message import Message
from .crop_calculator import CropCalculation

__all__ = [
    "User",
    "Tractor",
    "Field",
    "LandUsagePlan",
    "Crop",
    "ServiceBooking",
    "Part",
    "Notification",
    "Message",
    "CropCalculation",
]
