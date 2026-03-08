
from app.database.dbmodels import StolenVehicle , VehicleStatus
from app.database.connection import DBConnectionManager
import os
from app.services.logger import log_error

class DatabaseManager:
    def __init__(self):
        # Κλήση της setup_db => Αρχικοποίηση της βάσης εάν δεν υπάρχει ήδη.
        DBConnectionManager.setup_db()

    def check_plate(self, text):
        # Ελέγχουμε πρώτα αν το κείμενο της πινακίδας που αναγνωρίστηκε είναι έγκυρο.
        clean_text = ''.join(e for e in text if e.isalnum()).upper()
        if not clean_text:
            return None, "CLEAN", "#ecf0f1" # Default γκρι

        session = DBConnectionManager.get_session()
        # Ψάχνουμε στη βάση εάν το όχημα είναι καταχωρημένο ως STOLEN, ή WANTED. Εάν όχι, θεωρούμε ότι είναι CLEAN.
        vehicle = session.query(StolenVehicle).filter_by(plate_number=clean_text).first()
        session.close()

        if vehicle:
            # Δίνουμε χρώμα ανάλογα με το status του οχήματος στη βάση για να περάσει ως alert στο UI παρακάτω
            colors = {
                VehicleStatus.STOLEN: "#c0392b", # Κόκκινο
                VehicleStatus.WANTED: "#d35400", # Πορτοκαλί
                VehicleStatus.CLEAN: "#27ae60"   # Πράσινο
            }
            # Το vehicle.status είναι  Enum object, οπότε το χρησιμοποιούμε ως key
            color = colors.get(vehicle.status, "#ecf0f1")
            return clean_text, vehicle.status.value, color
        
        return clean_text, "CLEAN", "#27ae60"

    def add_stolen_vehicle(self, plate, status_string):
        # Προσθήκη οχήματος που είναι STOLEN/WANTED στη βάση μας. 
        session = DBConnectionManager.get_session()
        try:
            # Διασφάλιση εγκυρότητας του status του οχήματος. Στο combobox του UI ΔΕΝ έχουμε άλλη επιλογή,
            # βεβαιωνόμαστε ότι σε περίπτωση σφάλματος, δε θα "χτυπήσει" η βάση ή δε θα κρασάρει η εφαρμογή.
            
            status_enum = VehicleStatus(status_string.upper())
            
            vehicle = StolenVehicle(
                plate_number=plate.upper(), 
                status=status_enum
            )
            
            session.merge(vehicle)
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            file_name = os.path.basename(__file__) 
            error_type = type(e).__name__       
            log_error(error_type, file_name, str(e))
            raise e
            

        finally:
            session.close()


    
