from sqlalchemy.orm import Session
from typing import Dict, Any, Optional

from ..models.user import User as UserModel
from ..models.tractor import Tractor as TractorModel
from ..models.part import Part as PartModel
# Import other models as needed for more stats

class AdminService:
    def ban_user(self, db: Session, user_id: int) -> Optional[UserModel]:
        db_user = db.query(UserModel).filter(UserModel.id == user_id).first()
        if db_user:
            if db_user.is_banned: # Optional: prevent re-banning if already banned
                return db_user
            db_user.is_banned = True
            db_user.is_active = False # Typically banning also deactivates
            db.add(db_user)
            db.commit()
            db.refresh(db_user)
        return db_user

    def unban_user(self, db: Session, user_id: int) -> Optional[UserModel]:
        db_user = db.query(UserModel).filter(UserModel.id == user_id).first()
        if db_user:
            if not db_user.is_banned: # Optional: prevent re-unbanning
                return db_user
            db_user.is_banned = False
            # Decide if unbanning should also re-activate the user.
            # For now, let's assume it does not automatically re-activate; admin can do it separately if needed.
            # db_user.is_active = True
            db.add(db_user)
            db.commit()
            db.refresh(db_user)
        return db_user

    def get_site_statistics(self, db: Session) -> Dict[str, Any]:
        total_users = db.query(UserModel).count()
        active_users = db.query(UserModel).filter(UserModel.is_active == True).count()
        banned_users = db.query(UserModel).filter(UserModel.is_banned == True).count()

        total_tractors = db.query(TractorModel).count()
        # Add more stats as needed, e.g., parts listed, service bookings
        total_parts = db.query(PartModel).count()
        # total_service_bookings = db.query(ServiceBookingModel).count()

        return {
            "total_users": total_users,
            "active_users": active_users,
            "banned_users": banned_users,
            "total_tractors_listed": total_tractors,
            "total_parts_listed": total_parts,
            # "total_service_bookings": total_service_bookings,
            # Potentially add:
            # "users_pending_verification": db.query(UserModel).filter(UserModel.is_verified == False).count(),
        }

admin_service = AdminService()
