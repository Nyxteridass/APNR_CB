import time
import threading
from gpiozero import TonalBuzzer
from gpiozero.tones import Tone
#region Comments
#Κλάση που περιέχει μεθόδους για την αναπαραγωγή ήχων από το passive buzzer module. 
# Γίνεται χρήση threading για να μην μπλοκάρει το κύριο πρόγραμμα κατά την αναπαραγωγή ήχων.
#endregion
class SoundGenerator:
    _instance = None 

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(SoundGenerator, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, pin=17):
        if self._initialized:
            return 
            
        self.ok = True
        self._lock = threading.Lock()  
        
        try:
            self.buzzer = TonalBuzzer(pin)
        except Exception as e:
            print(f"[Sound Error] Buzzer Init Error: {e}")
            self.ok = False
            
        self._initialized = True

    def _run_in_thread(self, task, action_name="Audio"):
        # Τρέχουμε τον ήχο σε ξεχωριστό thread.
        def wrapper():
            # Δοκιμάζει να πάρει την κλειδαριά
            if self._lock.acquire(blocking=False):
                try:
                    task()  
                except Exception as e:
                    print(f"[Sound Error] Σφάλμα κατά την αναπαραγωγή {action_name}: {e}")
                finally:
                    self._lock.release()  
            else:
                # Αν βομβαρδιστεί με πολλές αναγνωρίσεις, απλά αγνοεί τις έξτρα
                pass 
                
        threading.Thread(target=wrapper, daemon=True).start()
    
    def play_scan_beep(self):
        #Ήχος σκαναρίσματος.
        if not self.ok: return
        
        def _task():
            
            self.buzzer.play(Tone(frequency=600))
            time.sleep(0.15) 
            self.buzzer.stop()
            
        self._run_in_thread(_task, "Scan Beep (CLEAN)")
  
    def play_alert_beep(self):
        # Ήχος συναγερμού για "STOLEN/WANTED" οχήματα.
        if not self.ok: return
        
        def _task():
            for _ in range(3):
                self.buzzer.play(Tone(frequency=500))
                time.sleep(0.3) 
                self.buzzer.stop()
                time.sleep(0.1)
                
        self._run_in_thread(_task, "Alert Beep (STOLEN/WANTED)")
    
    def play_welcome_intro(self):
        # Ήχος έναρξης εφαρμογής μετά το επιτυχημένο login του χρήστη. Σκοπός είναι 
        # να επιβεβαιωθεί η σωστή λειτουργία του passive buzzer module.
        if not self.ok: return
        
        def _task():
            self.buzzer.play(Tone(frequency=600))
            time.sleep(2.0)
            self.buzzer.stop()
            
        self._run_in_thread(_task, "Welcome Intro")


