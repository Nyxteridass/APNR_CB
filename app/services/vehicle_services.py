from app.database.database import DatabaseManager
from app.services.logger import log_added_vehicle

class VehicleService:
    @staticmethod
    def add_stolen_vehicle(plate: str, status: str) -> tuple[bool, str]:
        # Υπηρεσία που αναλαμβάνει την προσθήκη ενός νέου οχήματος στη ΒΔ ως "STOLEN/WANTED"
        try:
            db_manager = DatabaseManager()
            db_manager.add_stolen_vehicle(plate, status)
            log_added_vehicle(plate, status)
            return True, f"Το όχημα με πινακίδα {plate} προστέθηκε επιτυχώς!"
        except Exception as e:
            return False, f"Σφάλμα κατά την προσθήκη του οχήματος: {str(e)}"