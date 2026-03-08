from app.database.connection import DBConnectionManager
from app.database.dbmodels import User
from app.services.logger import log_access, log_error

# Repository για την ανάκτηση των στοιχείων των χρηστών από τη βάση μας. 
# Χρησιμοποιείται για τον έλεγχο ταυτότητας κατά το login.

class UsersRepository:
    @staticmethod
    def get_user_by_username(username):
        session = DBConnectionManager.get_session() 
        try:
            user = session.query(User).filter_by(username=username).first()
            if user:
                actual_role = user.role.value
                log_access(username, actual_role, "Successful Login Attempt")
                return {
                    "username": user.username,
                    "password": user.password,
                    "role": actual_role 
                }
            exception = f"User '{username}' not found in database."
            log_access(username, "UNKNOWN", f"Failed Login Attempt - {exception}")
            log_error("UserNotFound", "UsersRepository", exception)
            return None
        finally:
            session.close()
