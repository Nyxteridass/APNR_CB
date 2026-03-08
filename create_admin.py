from app.database.connection import DBConnectionManager
from app.database.dbmodels import User, UserRole  
from app.utils.hasher import hash_password 

#Κλάση για την αρχικοποίηση της ΒΔ και τη δημιουργία ενός χρήστη ADMINISTRATOR με username:"admin" 
#και password:"iee2019240". Η κλάση ελέγχει αν ο χρήστης υπάρχει ήδη και αν όχι, τον δημιουργεί με το ρόλο ADMIN.


def create_admin_user():
    print("Αρχικοποίηση σύνδεσης με τη βάση δεδομένων...")
    DBConnectionManager.setup_db()
    session = DBConnectionManager.get_session()

    new_username = "admin"
    new_password = "iee2019240"

    try:
        existing_user = session.query(User).filter_by(username=new_username).first()
        if existing_user:
            print(f"ERROR:  Ο χρήστης '{new_username}' υπάρχει ήδη στη βάση.")
            return

        hashed_pw = hash_password(new_password)
        
        new_admin = User(
            username=new_username,
            password=hashed_pw,
            role=UserRole.ADMIN
        )
        
        session.add(new_admin)
        session.commit()
        
        print(f"SUCCESS ! Ο χρήστης '{new_username}' δημιουργήθηκε.") 

    except Exception as e:
        session.rollback()
        print(f"ERROR : Σφάλμα κατά τη δημιουργία του χρήστη: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    create_admin_user()
