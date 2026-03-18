from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.utils.pathfinder import Labyrinth
from .dbmodels import Base

class DBConnectionManager:
    # Παίρνουμε το path της SQLite από το Pathfinder.py
    DB_URL = f"sqlite:///{Labyrinth.get_db_path()}"
    
    engine = create_engine(DB_URL, connect_args={"check_same_thread": False})
    SessionLocal = sessionmaker(bind=engine, expire_on_commit=False, autoflush=False)

    @staticmethod
    def setup_db():
        # Δημιουργούμε τους πίνακες στη βάση μας εάν δεν υπάρχουν.
        Base.metadata.create_all(DBConnectionManager.engine)

    @staticmethod
    def get_session():
        # Επιστρέφω ένα νέο session για να μπορέσουμε να κάνουμε queries στο police_db.sqlite 
        return DBConnectionManager.SessionLocal()

