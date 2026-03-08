import os


CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.abspath(os.path.join(CURRENT_DIR, '..','..'))  # Go up one level to the project root
MODEL_DETECTOR_PATH = os.path.join(BASE_DIR,   'models', 'license_plate_detector', 'license-plate-finetune-v1n.onnx')
MODEL_OCR_FOLDER_PATH = os.path.join(BASE_DIR, 'models', 'fast-plate-ocr')
DB_PATH = os.path.join(BASE_DIR, 'db','police_db.sqlite')
RESULTS_FILE_PATH = os.path.join(BASE_DIR,  'logs',  'detections.log')
ACCESS_LOG_FILE_PATH = os.path.join(BASE_DIR, 'logs', 'access.log')
ERROR_LOG_FILE_PATH = os.path.join(BASE_DIR, 'logs', 'errors.log')
LOGS_DIR_PATH = os.path.join(BASE_DIR, 'logs')


# Η κλάση Labyrinth έχει στατικές μεθόδους που επιστρέφουν τα paths για , ΒΔ, μοντέλα , Logs κλπ.
# εάν οι φάκελοι ΔΕΝ υπάρχουν, τότε δημιουργούνται αυτόματα.

class Labyrinth:

    
    @staticmethod
    def get_model_detector() -> str:
        # Επιστρέφει το path του μοντέλου ανίχνευσης πινακίδων.
        target_path = MODEL_DETECTOR_PATH
        if not os.path.exists(target_path):
            raise FileNotFoundError(f"Detector model not found at path: {target_path}")
        return str(target_path)

    @staticmethod
    def get_model_ocr(filename : str) -> str:
        #Επιστρέφει το path ενός μοντέλου OCR - ελέγχοντας την ύπαρξή του.
        target_path = os.path.join(MODEL_OCR_FOLDER_PATH, filename)
        if not os.path.exists(target_path):
            raise FileNotFoundError(f"Model file '{filename}' not found in '{MODEL_OCR_FOLDER_PATH}'")
        return str(target_path)


    @staticmethod
    def get_db_path(db_name="police_db.sqlite")-> str:
        #Επιστρέφει το path της ΒΔ. Σε περίπτωση που ο φάκελος ΔΕΝ υπάρχει , δημιουργείται.
        target_path = DB_PATH
        directory = os.path.dirname(target_path)
    
        
        if not os.path.exists(directory):
            os.makedirs(directory) # Δημιουργεί τον φάκελο 'db' αν λείπει
        
        return str(target_path)

    @staticmethod   
    def get_results_file_path(log_name="detections.log") -> str:
        #Επιστρέφει το path του detections.log
        target_path = RESULTS_FILE_PATH
    
        # Παίρνουμε μόνο τον φάκελο από το πλήρες μονοπάτι (π.χ. BASE_DIR/logs)
        directory = os.path.dirname(target_path)
    
        # Ελέγχουμε αν υπάρχει ο φάκελος. Αν όχι, τον δημιουργούμε.
        if not os.path.exists(directory):
            os.makedirs(directory) # Δημιουργείται ο φάκελος 'logs' αν λείπει
        
        return str(target_path)

    @staticmethod
    def get_access_log_path(log_name="access.log")-> str:
        #Επιστρέφει το path του access.log
        target_path = ACCESS_LOG_FILE_PATH
        # Παίρνουμε μόνο τον φάκελο από το πλήρες μονοπάτι (π.χ. BASE_DIR/logs)
        directory = os.path.dirname(target_path)
    
        # Ελέγχουμε αν υπάρχει ο φάκελος. Αν όχι, τον δημιουργούμε.
        if not os.path.exists(directory):
            os.makedirs(directory) # Δημιουργεί τον φάκελο 'logs' αν λείπει
        
        return str(target_path)
    @staticmethod
    def get_error_log_path(log_name="errors.log")-> str:
        ##Επιστρέφει το path του errors.log
        target_path = ERROR_LOG_FILE_PATH
        directory = os.path.dirname(target_path)
    
        # Ελέγχουμε αν υπάρχει ο φάκελος. Αν όχι, τον δημιουργούμε.
        if not os.path.exists(directory):
            os.makedirs(directory) # Δημιουργεί τον φάκελο 'logs' αν λείπει
        
        return str(target_path)



 
