from app.database.connection import DBConnectionManager
from app.database.dbmodels import User, UserRole
from app.services.logger import log_access, log_error
from app.utils.hasher import hash_password 
from app.core.session import SessionManager

# Υπηρεσία διαχείρισης χρηστών , με υλοποίηση Role-Based Access Control (RBAC). Χωρίζοντας και αναθέτοντας 
#δυνατότητες ανάλογα με το ρόλο που έχει ο εκάστοτε χρήστης, μπορούμε να διασφαλίσουμε ότι ΜΟΝΟ αυτοί που 
#έχουν κατάλληλα δικαιώματα μπορούν να πραγματοποιήσουν κάποιες ενέργειες - πχ CRUD χρηστών.

class UserManagementService:
    @staticmethod
    def require_admin():
        # 1. Αυστηρός έλεγχος δικαιωμάτων (Authorization Check)
        if SessionManager.get_role() != "ADMINISTRATOR":
            return False, "ACCESS DENIED : Μόνο ο Διαχειριστής μπορεί να εκτελέσει αυτή την ενέργεια."
        return True, ""                     

    @staticmethod
    def get_manageable_users():
        session = DBConnectionManager.get_session()
        try:
            #Επιστρέφουμε όλους τους χρήστες που δεν είναι ADMINISTRATORS.
            users = session.query(User).filter(User.role != UserRole.ADMIN).all()
            return [{"id": u.id, "username": u.username, "role": u.role.value} for u in users]
        finally:
            session.close()

    @staticmethod
    def create_user(new_username: str, new_password: str, role_to_assign: str):
        # Δημιουργία νέου χρήστη με επιλογή Ρόλου από ADMINISTRATOR. Ελέγχουμε αν ο τρέχων χρήστης είναι Admin
        # εάν όχι, τότε αρνούμαστε την εκτέλεση ενέργειας και καταγράφουμε στο log.
        is_admin, message = UserManagementService.require_admin()
        if not is_admin:
            log_error("ACCESS DENIED", "UserManagementService", f"Ο χρήστης {SessionManager.get_current_user()} προσπάθησε να φτιάξει λογαριασμό χωρίς άδεια.")
            return False, message
        
        session = DBConnectionManager.get_session()
        try:
            existing_user = session.query(User).filter_by(username=new_username).first()
            if existing_user:
                return False, f"Το όνομα χρήστη '{new_username}' χρησιμοποιείται ήδη."
            
            
            role_enum = UserRole(role_to_assign.upper())
            
            hashed_pw = hash_password(new_password)
                
            new_user = User(
                username=new_username,
                password=hashed_pw,
                role=role_enum
            )

            session.add(new_user)
            session.commit()

            # Καταγραφή της επιτυχούς ενέργειας
            log_access(SessionManager.get_current_user(), SessionManager.get_role(), f"Επιτυχής δημιουργία λογαριασμού ({role_enum.value}): {new_username}")
            return True, f"Ο λογαριασμός για τον χρήστη '{new_username}' με ρόλο '{role_enum.value}' δημιουργήθηκε με επιτυχία."

        except Exception as e:
            session.rollback()
            # Καταγραφή της αποτυχίας - λεπτομέρειες σφάλματος 
            log_error(type(e).__name__, "UserManagementService", str(e))
            return False, f"Σφάλμα κατά την αποθήκευση στη βάση: Λάθος Ρόλος ή Δεδομένα. ({str(e)})"
        finally:
            session.close()


    @staticmethod
    def delete_user(user_id: str):
        # Διαγραφή χρήστη με βάση το user_id του. 
        is_admin, message = UserManagementService.require_admin()
        if not is_admin:
            log_error("ACCESS DENIED", "UserManagementService", f"Ο χρήστης {SessionManager.get_current_user()} προσπάθησε να διαγράψει χρήστη χωρίς άδεια.")
            return False, message

        session = DBConnectionManager.get_session()
        try:
            user_to_delete = session.query(User).filter_by(id=user_id).first()
            if  user_to_delete:
                session.delete(user_to_delete)
                session.commit()
                log_access(SessionManager.get_current_user(), SessionManager.get_role(), f"USER DELETED, o xρήστης με ID: {user_id} διαγράφηκε!")
                return True, f"Ο χρήστης με ID: {user_id} διαγράφηκε επιτυχώς."
            log_error("FailedDelete", "UserManagementService", f"FAILED DELETE ATTEMPT , o xρήστης με ID: {user_id} δεν βρέθηκε!")
            return False, f"Ο χρήστης με ID: {user_id} δεν βρέθηκε."
        finally:
            session.close()

    @staticmethod
    def update_user(user_id: str, new_password: str, new_role: str):
        # Ενημέρωση στοιχείων χρήστη - Αλλαγή κωδικού και / ή ρόλου. Απαιτείται ομοίως ρόλος Admin για εκτέλεση.
        is_admin, message = UserManagementService.require_admin()
        if not is_admin:
            log_error("ACCESS DENIED", "UserManagementService", f"Ο χρήστης {SessionManager.get_current_user()} προσπάθησε να ενημερώσει χρήστη χωρίς άδεια.")
            return False, message

        session = DBConnectionManager.get_session()
        try:
            user_to_update = session.query(User).filter_by(id=user_id).first()
            if user_to_update:
                if new_password: # Αν δόθηκε νέος κωδικός
                    user_to_update.password = hash_password(new_password)
                
                
                user_to_update.role = UserRole(new_role.upper())
                
                session.commit()
                log_access(SessionManager.get_current_user(), SessionManager.get_role(), f"USER UPDATED, ο χρήστης με ID: {user_id} ενημερώθηκε (Νέος Ρόλος: {user_to_update.role.value})!")
                return True, f"Ο χρήστης με ID: {user_id} ενημερώθηκε επιτυχώς."
            
            log_error("FAILED USER UPDATE", "UserManagementService", f"FAILED UPDATE ATTEMPT, ο χρήστης με ID: {user_id} δεν βρέθηκε!!!")
            return False, f"Ο χρήστης με ID: {user_id} δεν βρέθηκε."
        except Exception as e:
            session.rollback()
            log_error(type(e).__name__, "UserManagementService", str(e))
            return False, f"Σφάλμα κατά την ενημέρωση στη βάση: Λάθος Ρόλος ή Δεδομένα. ({str(e)})"
        finally:
            session.close()


