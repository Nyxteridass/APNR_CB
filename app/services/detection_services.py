import re
from app.database.connection import DBConnectionManager
from app.database.dbmodels import StolenVehicle

#region Comments
# Υπηρεσία που ελέγχει την πινακίδα ως προς την ορθότητα για τον περιορισμό των αχρείαστων queries
# προς τη βάση και μετά φέρνει την "κατάσταση" του οχήματος πάλι προς το UI. Εάν ΔΕΝ εντοπιστεί τέτοια 
# πινακίδα, επιστρέφει status "CLEAN" και default χρώμα πράσινο. Εάν εντοπιστεί, επιστρέφει το status 
# του οχήματος στη βάση μας (STOLEN/WANTED) και το αντίστοιχο χρώμα για να περάσει ως alert στο UI.
#endregion
class DetectionService:
    def __init__(self):
        self.session_factory = DBConnectionManager.get_session

    def process_detected_plate(self, raw_text):
        # "Καθαρισμός" του κειμένου: Αφαιρούμε όλα τα μη-αλφαριθμητικά και μετατρέπουμε σε κεφαλαία
        clean_text = "".join(re.findall(r'[A-Z0-9]', raw_text.upper()))
#region  process_detected_plate() ---Comments 
        # Regex για ελληνικό format (3 γράμματα που συνοδεύονται από 1- 4 αριθμούς , 
        # για να συμπεριλάβουμε και  πινακίδες δικύκλων που έχουν 3 γράμματα αλλά 
        # από 1 έως 3 αριθμούς). Με αλλαγή στο regex μπορούμε να συμπεριλάβουμε και 
        # πινακίδες με 2 γράμματα (π.χ. για παλιά οχήματα) ή να επεκτείνουμε την αναζήτηση 
        # σε πινακίδες άλλων τύπων οχημάτων (πχ φορτηγά).
#endregion       
        pattern = r'^[ABEZHIKMNOPTYX]{3}\d{1,4}$'
        if not re.match(pattern, clean_text):
            return None # Δεν είναι έγκυρη ελληνική πινακίδα

        # Έλεγχος στη βάση
        session = self.session_factory()
        try:
            vehicle = session.query(StolenVehicle).filter_by(plate_number=clean_text).first()
            if vehicle:
                return {
                    "plate": clean_text,
                    "status": vehicle.status.value,
                    
                }
                
            return {"plate": clean_text, "status": "CLEAN"}
        finally:
            session.close()

