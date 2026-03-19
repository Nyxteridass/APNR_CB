from app.repos.users_repo import UsersRepository
from app.utils.hasher import verify_password
from app.core.session import SessionManager

# Υπηρεσία που χειρίζεται το authentication των χρηστών.

class AuthService:
    @staticmethod
    def login(username, password):
        user = UsersRepository.get_user_by_username(username)
        
        # Εδώ το user['password_hash'] περιέχει το user.password από τη βάση
        if user and verify_password(user['password'], password):
            SessionManager.set_user(user['username'], user['role'])
            return True
        return False

    @staticmethod
    def logout():
        SessionManager.clear()

