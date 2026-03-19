import logging
from app.utils.pathfinder import LOGS_DIR_PATH

#Εισάγουμε το BASE_DIR και πριν την δημιουργία του logger ελέγχουμε την ύπαρξη 
# του φακέλου με τα logs.Στην περίπτωση που δεν υπάρχει - δημιουργείται εδώ.

LOGS_DIR_PATH.mkdir(exist_ok=True)

def _setup_logger(name: str, log_file: str) -> logging.Logger:
    #Δημιουργούμε ένα logger setup (generic).
    logger = logging.getLogger(name)
    logger.propagate = False
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        
        # Ο formatter της βιβλιοθήκης βάζει το τρέχον timestamp όταν καλείται ο logger
        #  και μετά το μήνυμα που δέχεται στο αντίστοιχο αρχείο 
        formatter = logging.Formatter('%(asctime)s, %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
        
        file_handler = logging.FileHandler(LOGS_DIR_PATH / log_file, encoding='utf-8')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
                
    return logger

# Αρχικοποίηση των 3 loggers όταν φορτώνεται το αρχείο
_det_logger = _setup_logger("detections", "detections.log")
_acc_logger = _setup_logger("access", "access.log")
_err_logger = _setup_logger("errors", "errors.log")

# Συναρτήσεις για τους διάφορους τύπους καταγραφών:

def log_detection(plate: str, status: str, confidence: float, ocr_model: str):
    #region Comments
    # Γράφει στο αρχείο detections.log : timestamp, πινακίδα που ανιχνεύθηκε, status ,
    #  confidence του μοντέλου που χρησιμοποιήθηκε και ποιο μοντέλο OCR έχει χρησιμοποιηθεί
    # στη συγκεκριμένη ανίχνευση για λόγους στατιστικής ανάλυσης.
    #endregion
    # Μορφοποίηση του confidence σε 2 δεκαδικά (π.χ. 0.95)
    _det_logger.info(f"{plate}, {status}, {confidence:.2f}, {ocr_model}")

def log_added_vehicle(plate: str, status: str):
    # Γράφει στο αρχείο access.log , την ΠΡΟΣΘΗΚΗ οχήματος στη βάση.   
    _acc_logger.info(f"{plate}, {status}, ADDED_TO_DB ")

def log_access(username: str, role: str, action: str):
    # Γράφει στο access.log, ΚΑΘΕ ενέργεια που σχετίζεται με Χρήστες / απόπειρες εισόδου στο σύστημα 
    _acc_logger.info(f"{username}, {role}, {action}")

def log_error(error_type: str, file_name: str, details: str = ""):
    #region
    # Γράφει στο errors.log, κάθε σφάλμα που προκύπτει κατά τη λειτουργία του συστήματος.
    # Εκτός από το timestamp  δίνει τον τύπο σφάλματος και το αρχείο που το προκάλεσε και μπορεί 
    # να συμπεριλάβει και λεπτομέρειες.
    #endregion
    msg = f"{error_type}, {file_name}"
    if details:
        msg += f", {details}"
    _err_logger.error(msg)

