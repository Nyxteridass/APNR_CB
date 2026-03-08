# APNR System  

Ένα σύστημα Αυτόματης Αναγνώρισης Πινακίδων (Automatic Plate Number Recognition), σχεδιασμένο και βελτιστοποιημένο για συστήματα Edge Computing, με κύριο στόχο την ομαλή λειτουργία σε **Raspberry Pi 3B+**. 

Το σύστημα ενσωματώνει ελέγχους ασφαλείας, Role-Based Access Control (RBAC), και ελέγχει τις πινακίδες έναντι μιας τοπικής βάσης δεδομένων σε πραγματικό χρόνο για ανεύρεση κλεμμένων (Stolen) ή αναζητούμενων (Wanted) οχημάτων.

## Αρχιτεκτονική Λογισμικού (Software Architecture)
Η εφαρμογή ακολουθεί αυστηρά τις αρχές του **Separation of Concerns (SoC)** και του **Dependency Injection**, χρησιμοποιώντας μια Layered/Modular αρχιτεκτονική:

1. **Core Layer:** Αναλαμβάνει τις ρυθμίσεις (`config1.py`), τη διαχείριση της συνεδρίας του χρήστη (`session.py`) και λειτουργεί ως Dependency Injector μέσω του `container.py`.
2. **Database & Repositories Layer:** Διαχειρίζεται την SQLite (`connection.py`), ορίζει τα SQLAlchemy ORM Models (`dbmodels.py`) και τα Repositories απομονώνουν τα SQL Queries από το υπόλοιπο πρόγραμμα.
3. **Services Layer:** Περιέχει όλη την επιχειρησιακή λογική (Business Logic). Το `AuthService` αναλαμβάνει τις συνδέσεις, το `DetectionService` τη λογική της αναγνώρισης και το `UserManagementService` τους κανόνες εξουσιοδότησης (π.χ. *Μόνο οι Admins μπορούν να φτιάξουν χρήστες*).
4. **Inference (AI) Layer:** Ένα pipeline (`pipeline.py`) που "δένει" το OpenCV DNN (Object Detection) με το `fast-plate-ocr` (Text Recognition).
5. **UI Layer:** Γραμμένο σε `tkinter`. Αποτελείται από δύο views: Το Login και το MainWindow. Το UI αγνοεί εντελώς τη βάση δεδομένων και "μιλάει" μόνο με τα Services/Container.

## Τρόπος Λειτουργίας & Μετάβαση Κλάσεων (Flow Control)

### 1. Εκκίνηση και Αυθεντικοποίηση
* Η εκτέλεση ξεκινά από το `main.py`. Αρχικά φορτώνεται αποκλειστικά το `LoginWindow`.
* Όταν ο χρήστης βάλει τα στοιχεία του, η φόρμα επικοινωνεί με το `AuthService`.
* Το `AuthService` καλεί το `UsersRepository` για να φέρει τον χρήστη από τη βάση και, χρησιμοποιώντας το `hasher.py`, κάνει verify τον `bcrypt` κωδικό.
* Αν η είσοδος επιτύχει:
  * Γίνεται `set_user()` στο `SessionManager` (αποθήκευση του ρόλου: Admin, Supervisor, User).
  * Αναπαράγεται ήχος μέσω του `SoundGenerator`.
  * Εκτελείται η `launch_main_app()`: Εδώ αρχικοποιείται το **`Container`** (καταναλώνει μνήμη, φορτώνει AI μοντέλα, κάνει establish DB Connection) και "παραδίδεται" στο `MainWindow`.

### 2. Ροή Αναγνώρισης (Detection Flow)
Μόλις ο χρήστης πατήσει το **"START CAMERA"**:
* Η εφαρμογή ανοίγει παράθυρο για την επιλογή του OCR μοντέλου και ρυθμίζει το AI Pipeline.
* Ξεκινούν δύο ανεξάρτητα **Daemon Threads**:
  1. `capture_thread`: Απλά τραβάει (grabs) διαρκώς frames από την κάμερα ώστε να αδειάζει το buffer (`cv2.CAP_PROP_BUFFERSIZE = 1`), λύνοντας το πρόβλημα του lag στο Raspberry Pi.
  2. `detect_thread`: Τρέχει ανά `DETECT_EVERY_N_FRAMES`. Παίρνει το τελευταίο frame και καλεί την `InferencePipeline.detect_and_ocr()`.
* **InferencePipeline:** Το frame υφίσταται `letterbox()` scaling. Περνάει από το ONNX μοντέλο. Εφαρμόζεται Non-Maximum Suppression (NMS). Κάθε Bounding Box κόβεται (ROI) και στέλνεται στον recognizer (fast-plate-ocr).
* Οι πινακίδες που βρέθηκαν παραδίδονται πίσω στο Thread. Το thread στέλνει την πινακίδα στο `DetectionService.process_detected_plate()`.
* **Business Logic:** Το Service ελέγχει με Regex αν η πινακίδα έχει ελληνικό format. Αν ναι, ερωτά την SQLite μέσω του `DatabaseManager`.
* Το Service επιστρέφει το status ("CLEAN", "STOLEN", "WANTED").
* Ανάλογα με το status, η `MainWindow` ενημερώνει το UI Status Bar, καλεί τον `SoundGenerator` (για το αντίστοιχο beep) και γράφει στο `detections.log` μέσω του `logger.py`.

### 3. Edge Computing Βελτιστοποιήσεις
* Χρήση CPU Backend του OpenCV (`DNN_TARGET_CPU`) και περιορισμός Threads: `cv2.setNumThreads(2)`.
* Η χρήση Threading για Audio, Video και Inference εξασφαλίζει ότι το UI (`mainloop`) δεν παγώνει ποτέ.
* Η κλειδαριά (`threading.Lock`) στο Audio με `blocking=False` διασφαλίζει ότι αν εκτελείται ήδη ένας ήχος συναγερμού, δε δημιουργείται συμφόρηση/queue στα ηχεία του Pi.

## Διαχείριση Σφαλμάτων & Logging
Όλο το σύστημα τυλίγεται γύρω από δομές `try...except`. 
Κάθε σφάλμα στέλνεται στο `logger.log_error()`, το οποίο με τη σειρά του γράφει στο `logs/errors.log` (Μαζί με το Timestamp, τον τύπο του Error και το Αρχείο που το προκάλεσε). Υπάρχει πλήρες Audit Trail (ποιος μπήκε, ποιος πρόσθεσε όχημα) στο `logs/access.log`.









## 🛡️ License & Open Source Compliance

This application is licensed under the **GNU Affero General Public License v3 (AGPL-3.0)**. 

### Why AGPL v3?
We believe in the freedom of software. Unlike the standard GPL, the **AGPL v3** is designed specifically for network-interacted software (SaaS). It ensures that:
* **Remote Interaction:** If this application is modified and run on a server for public use, the modified source code **must** be made available to those users.
* **Copyleft:** Any derivative works must also be licensed under the AGPL v3.
* **Transparency:** Users interacting with this software over a network have the right to receive a copy of the source code.

### Personal/Private Use
While this repository is currently **Private**, the inclusion of this license ensures that any future deployment or distribution remains compliant with open-source standards.

---
*For more details, see the [LICENSE](LICENSE) file in the root directory.*
