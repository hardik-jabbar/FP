# This file makes 'schemas' a Python package
from .user import (
    UserBase,
    UserCreate,
    UserUpdate,
    UserSchema,
    Token,
    TokenData,
    OTPRequest,
    OTPVerify,
    UserRole # Re-export UserRole if it's commonly used with schemas
)
from .tractor import TractorSchema, TractorCreate, TractorUpdate, TractorBase
from .land_usage_plan import (
    LandUsagePlanBase,
    LandUsagePlanCreate,
    LandUsagePlanUpdate,
    LandUsagePlanSchema,
)
from .field import (
    FieldBase,
    FieldCreate,
    FieldUpdate,
    FieldSchema,
)
from .crop import (
    CropBase,
    CropCreate,
    CropUpdate,
    CropSchema,
    ProfitCalculationResult,
    MinimalFieldSchema # If it's defined in crop.py and needs to be available
)
from .service_booking import ( # Import service booking schemas
    ServiceBookingBase,
    ServiceBookingCreate,
    ServiceBookingUpdate,
    ServiceBookingSchema,
    MinimalTractorSchema,
    ServiceStatus
)
from .part import ( # Import part schemas
    PartBase,
    PartCreate,
    PartUpdate,
    PartSchema,
)
from .notification import ( # Import notification schemas
    NotificationBase,
    NotificationCreateInternal,
    NotificationSchema,
    NotificationType
)
from .message import ( # Import message schemas
    MessageBase,
    MessageCreate,
    MessageSchema,
    ConversationSchema
)
