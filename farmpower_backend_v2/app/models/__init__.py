# This file imports all the models, making them available
# to SQLAlchemy when Base.metadata.create_all() is called.

# Import all models to ensure they are registered with SQLAlchemy's Base.metadata
from . import user
from . import tractor
from . import field
from . import crop
from . import land_usage_plan
from . import message
from . import notification
from . import part
from . import service_booking
from . import crop_calculator

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
