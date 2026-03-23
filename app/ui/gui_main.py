import tkinter as tk
from tkinter import scrolledtext, ttk, messagebox
import cv2
import PIL.Image, PIL.ImageTk
import threading
import time
import os
from app.services.logger import log_error, log_detection
from app.utils.pathfinder import Labyrinth
from app.core.session import SessionManager
import app.core.config1 as config
from app.services.user_services import UserManagementService
from app.services.services import AuthService
from app.services.vehicle_services import VehicleService 
from app.utils.sound import SoundGenerator as sound

class MainWindow:
    def __init__(self, root, title, container):
        self.root = root
        self.root.title(title)
        self.root.geometry("1000x750")        
        self.root.protocol("WM_DELETE_WINDOW", self.on_exit)
        self.container = container
        self.pipeline = container.pipeline
        self.detection_service = container.detection_service
        self.sound_gen = sound()
        self.is_running = False
        self.cap = None
        self.lock = threading.Lock()
        self.latest_frame = None
        self.latest_results = []
        self.last_ocr_time = 0
        self.frame_count = 0
        
        self._setup_ui()

    def _setup_ui(self):
        # "Στήσιμο" του UI.

        # Αριστερό πάνελ - σετάρισμα
        self.left_frame = tk.Frame(self.root, width=250, bg="#2c3e50")
        self.left_frame.pack(side=tk.LEFT, fill=tk.Y)
        self.left_frame.pack_propagate(False)

        tk.Label(self.left_frame, text="APNR System"+"\n"+"\n"+"Edge Computing Node"+
                "\n"+"on Raspberry Pi 3B+",
                 font=("Helvetica", 14, "bold"),
                 bg="#2c3e50", fg="#ecf0f1").pack(pady=25)
                 
        
        btn_style = {"font": ("Arial", 11), "pady": 5, "padx": 10}

        self.btn_start = tk.Button(self.left_frame, text="START CAMERA", bg="#27ae60", fg="white",
                                   command=self.start_camera, **btn_style)
        self.btn_start.pack(pady=10, fill=tk.X, padx=15)

        self.btn_stop = tk.Button(self.left_frame, text="STOP", bg="#c0392b", fg="white",
                                  command=self.stop_camera, state=tk.DISABLED, **btn_style)
        self.btn_stop.pack(pady=5, fill=tk.X, padx=15)

        tk.Frame(self.left_frame, height=2, bg="grey").pack(fill=tk.X, pady=20, padx=10)

        self.btn_add = tk.Button(self.left_frame, text="Add Vehicle", bg="#2980b9", fg="white",
                                 command=self.add_vehicle, **btn_style)
        self.btn_add.pack(pady=5, fill=tk.X, padx=15)

        self.btn_log = tk.Button(self.left_frame, text="View Logs", bg="#8e44ad", fg="white",
                                 command=self.show_logs, **btn_style)
        self.btn_log.pack(pady=5, fill=tk.X, padx=15)

        self.btn_users = tk.Button(self.left_frame, text="Manage Users", bg="#e67e22", fg="white",
                                   command=self.open_user_management, **btn_style)
        self.btn_users.pack(pady=5, fill=tk.X, padx=15)
                
        tk.Label(self.left_frame, text="Διεθνές Πανεπιστήμιο της Ελλάδος" + "\n" + "Σχολή Μηχανικών" +
                "\n" + "\n" + "Τμήμα Μηχανικών Πληροφορικής " + "\n" + "& Ηλεκτρονικών Συστημάτων",
                 font=("Helvetica", 10, "bold"),
                 bg="#2c3e50", fg="#ecf0f1").pack(pady=20)
                 
        tk.Label(self.left_frame, text="Created by: "+"\n" +"Μπεσίρης Χρήστος (iee2019240)"+"\n"+"\n"+
                "Επιβλέπων:"+"\n"+"Δρ. Διαμαντάρας Κωνσταντίνος"+"\n"+"Καθηγητής",
                 font=("Helvetica", 8, "bold"),
                 bg="#2c3e50", fg="#ecf0f1").pack(pady=20)
        
        self.btn_exit = tk.Button(self.left_frame, text="EXIT", bg="#34495e", fg="white",
                                  command=self.on_exit, **btn_style)
        self.btn_exit.pack(side=tk.BOTTOM, pady=20, fill=tk.X, padx=15)

        # Σετάρισμα του κεντρικού πάνελ - frame ροής βίντεο
        self.video_frame = tk.Frame(self.root, bg="black")
        self.video_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.lbl_video = tk.Label(self.video_frame, bg="black", text="System Offline",
                                  fg="#7f8c8d", font=("Arial", 18))
        self.lbl_video.pack(expand=True)

        # Εφαρμογή "Status Bar" στο κάτω μέρος της διεπαφής - για να δίνουμε ΟΠΤΙΚΟ feedback στον χρήστη
        self.status_var = tk.StringVar(value="Waiting for start...")
        self.lbl_status = tk.Label(self.root, textvariable=self.status_var, bd=1, relief=tk.SUNKEN,
                                   anchor=tk.W, font=("Arial", 12, "bold"),
                                   bg="#ecf0f1", padx=10, pady=5)
        self.lbl_status.pack(side=tk.BOTTOM, fill=tk.X)

    def choose_fastocr_model(self):
        # Παράθυρο επιλογής μοντέλου για το OCR από τον χρήστη.
        win = tk.Toplevel(self.root)
        win.title("Select OCR model")
        win.resizable(False, False)
        win.transient(self.root)

        tk.Label(win, text="Choose fast-plate-ocr model:", font=("Arial", 11, "bold")).pack(padx=12, pady=(12, 6))

        var = tk.StringVar(value=config.FAST_OCR_MODELS[0])
        combo = ttk.Combobox(win, values=config.FAST_OCR_MODELS, textvariable=var, state="readonly", width=42)
        combo.pack(padx=12, pady=6, fill=tk.X)
        combo.current(0)

        result = {"model": None}

        def ok():
            result["model"] = var.get().strip()
            win.destroy()

        def cancel():
            result["model"] = None
            win.destroy()

        btns = tk.Frame(win)
        btns.pack(padx=12, pady=(8, 12), fill=tk.X)
        tk.Button(btns, text="OK", command=ok, width=10).pack(side=tk.LEFT)
        tk.Button(btns, text="Cancel", command=cancel, width=10).pack(side=tk.RIGHT)

        win.grab_set()
        win.wait_window()
        return result["model"]

    def start_camera(self):
        # Button έναρξης ροής από την κάμερα. Με την έναρξη - προτρέπεται ο 
        # χρήστης να επιλέξει μοντέλο OCR
        if self.is_running:
            return

        chosen = self.choose_fastocr_model()
        if not chosen:
            return
        self.current_ocr_model = chosen

        if hasattr(self.pipeline, 'load_ocr'):
            self.pipeline.load_ocr(chosen)

        try:
            self.cap = cv2.VideoCapture(config.CAMERA_ID)
            self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, config.FRAME_WIDTH)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, config.FRAME_HEIGHT)

            self.is_running = True
            self.btn_start.config(state=tk.DISABLED)
            self.btn_stop.config(state=tk.NORMAL)
            self.lbl_video.config(text="")
            self.status_var.set("Scanning...")

#region Comments
            # SOS !!! Πολύ σημαντικό - διαχείριση threads γιατί χωρίς 
            # διάκριση - ο έλεγχος από το OCR "παγώνει" την εκτέλεση 
            # του υπόλοιπου κώδικα. 
#endregion
            threading.Thread(target=self.capture_thread, daemon=True).start()
            threading.Thread(target=self.detect_thread, daemon=True).start()
            self.update_gui_frame()

        except Exception as e:
            file_name = os.path.basename(__file__) 
            error_type = type(e).__name__
            log_error(error_type, file_name, str(e))
            messagebox.showerror("Camera Error", str(e))

    def stop_camera(self):
        #Διακοπή ροής της κάμερας (feed) 
        self.is_running = False
        if self.cap:
            try:
                self.cap.release()
            except: pass

        with self.lock:
            self.latest_frame = None
            self.latest_results = []

        self.btn_start.config(state=tk.NORMAL)
        self.btn_stop.config(state=tk.DISABLED)
        self.lbl_video.config(image='', text="System Offline", bg="black")
        self.status_var.set("Waiting...")
        self.lbl_status.config(bg="#ecf0f1", fg="black")

    def capture_thread(self):
        # Ορισμός και κλείδωμα του capture_thread
        while self.is_running and self.cap:
            try:
                self.cap.grab()
                ret, frame = self.cap.retrieve()
            except:
                ret, frame = self.cap.read()

            if not ret:
                continue

            with self.lock:
                self.latest_frame = frame
            time.sleep(0.001)

    def detect_thread(self):
        # Ορισμός και "κλείδωμα " του detect_thread
        
        while self.is_running:
            try:
                with self.lock:
                    frame = None if self.latest_frame is None else self.latest_frame.copy()

                if frame is None:
                    time.sleep(0.01)
                    continue

                self.frame_count += 1
                if (self.frame_count % config.DETECT_EVERY_N_FRAMES) != 0:
                    time.sleep(0.001)
                    continue

                current_time = time.time()
#region Comments
        #-------------------------------------------------------------#
        # SOS !!! - Πέρασμα του ελέγχου στο inference.pipeline.py
#endregion
                results = self.pipeline.detect_and_ocr(frame)

                with self.lock:
                    # Καθαρίζει το box αν δεν βρει πινακίδα
                    self.latest_results = results[:config.MAX_DETECTIONS_DRAW] if results else []
                
                if results and (current_time - self.last_ocr_time) >= config.OCR_INTERVAL_SEC:
                    for res in results:
                        plate = res['text']
                        conf = res.get('confidence', 0.0)
                        if not plate: 
                            continue
#region Comments
            #---------------------------------------------------------
            # SOS ! Περνάμε τον έλεγχο στο detection_service για να τρέξει τον έλεγχο της βάσης με τη σειρά του
#endregion
                        db_info = self.detection_service.process_detected_plate(plate)
                       
                        if db_info:
                            self.update_ui_status_safe(db_info)
                            if db_info['status'] != "CLEAN":
                                #Εάν η πινακίδα ΔΕΝ είναι "CLEAN" τότε στέλνουμε ALERT - ΗΧΗΤΙΚΟ FEEDBACK
                                self.sound_gen.play_alert_beep()
                            else:
                                # Αλλιώς το buzzer αναπαράγει μόνο ένα "scan_beep" για ΗΧΗΤΙΚΟ FEEDBACK
                                self.sound_gen.play_scan_beep()                               
                            log_detection(
                                plate=db_info['plate'], 
                                status=db_info['status'], 
                                confidence=conf, 
                                ocr_model=getattr(self, 'current_ocr_model', 'Unknown')
                            )
                                
                    self.last_ocr_time = time.time()                   
            except Exception as e:
                print(f"\n[ΣΦΑΛΜΑ ΣΤΟ DETECT THREAD]: {e}")
                log_error("DetectThreadError", "gui_main.py", str(e))
                with self.lock:
                    self.latest_results = []
                time.sleep(1)

    def update_gui_frame(self):
        #UI Updater μέθοδος για 'ανανέωση' του frame (cap)
        if not self.is_running:
            return

        with self.lock:
            frame = None if self.latest_frame is None else self.latest_frame.copy()
            results = list(self.latest_results)

        if frame is not None:
            for res in results:
                x, y, w, h = res['box']
                plate_text = res.get('text', '')
                conf = res.get('confidence', 0.0)

                display_text = f"{plate_text} ({conf:.2f})" if plate_text else f"Conf: {conf:.2f}"

                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.putText(frame, display_text, (x, max(0, y - 10)), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

            img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img_tk = PIL.ImageTk.PhotoImage(image=PIL.Image.fromarray(img))
            self.lbl_video.img_tk = img_tk
            self.lbl_video.configure(image=img_tk)

        ms = int(1000 / config.GUI_FPS)
        self.root.after(ms, self.update_gui_frame)

    def update_ui_status_safe(self, db_info):
        # UI Updater για το "Status Bar" - αναλαμβάνει την ΟΠΤΙΚΗ ΑΝΑΔΡΑΣΗ - του χρήστη!
        status_text = f"PLATE: {db_info['plate']} | STATUS: {db_info['status']}"
        color = "#27ae60" # Default Green
        
        if db_info['status'] == "STOLEN": color = "#c0392b"
        elif db_info['status'] == "WANTED": color = "#d35400"
        
        self.root.after(0, lambda: self.status_var.set(status_text))
        self.root.after(0, lambda: self.lbl_status.config(bg=color, fg="white"))
 
    def add_vehicle(self):
        # Άνοιγμα παραθύρου εισαγωγής νέας πινακίδας οχήματος στη βάση 
        add_win = tk.Toplevel(self.root)
        add_win.title("Προσθήκη Οχήματος")
        add_win.geometry("300x250")
        add_win.resizable(False, False)
        add_win.transient(self.root) 
        add_win.grab_set()           

        tk.Label(add_win, text="Αριθμός Πινακίδας (π.χ. ABC1234):", font=("Arial", 10)).pack(pady=(20, 5))
        ent_plate = tk.Entry(add_win, width=20, font=("Arial", 12), justify="center")
        ent_plate.pack()

        tk.Label(add_win, text="Κατάσταση Οχήματος:", font=("Arial", 10)).pack(pady=(15, 5))
        cmb_status = ttk.Combobox(add_win, values=["STOLEN", "WANTED"], state="readonly", font=("Arial", 11), width=18)
        cmb_status.current(0) 
        cmb_status.pack()
        
        btn_save = tk.Button(add_win, text="Αποθήκευση", bg="#c0392b", fg="white", font=("Arial", 10, "bold"), width=15)
#region Comments
# -----------------------------------------------------
#   SOS !!!  Δημιουργία functions για να τρέξουν ΑΣΥΓΧΡΟΝΑ  σε δικό τους thread (lib threading) ώστε η αποθήκευση
#           των δεδομένων που έχει εισάγει ο χρήστης σαν νέο "STOLEN/WANTED" όχημα , να γίνει χωρίς να "κολλάει" η 
#           υπόλοιπη διεπαφή.
#endregion
        def _bg_task(plate, status):
            try:
                success, msg = VehicleService.add_stolen_vehicle(plate, status)
                self.root.after(0, lambda: _on_result(success, msg))
            except Exception as e:
                self.root.after(0, lambda: _on_result(False, f"Σφάλμα Βάσης: {str(e)}"))

        def _on_result(success, msg):
            if success:
                messagebox.showinfo("Επιτυχία", msg, parent=add_win)
                add_win.grab_release() 
                add_win.destroy()
            else:
                messagebox.showerror("Σφάλμα", msg, parent=add_win)
                btn_save.config(state=tk.NORMAL, text="Αποθήκευση")

        def on_save():
            plate = ent_plate.get().strip().upper()
            status = cmb_status.get().strip()

            if not plate:
                messagebox.showwarning("Προσοχή", "Το πεδίο της πινακίδας δεν μπορεί να είναι κενό!", parent=add_win)
                return

            btn_save.config(state=tk.DISABLED, text="Παρακαλώ περιμένετε...")
            
            # Εκκίνηση του thread αποθήκευσης 
            threading.Thread(target=_bg_task, args=(plate, status), daemon=True).start()

        btn_save.config(command=on_save)
        btn_save.pack(pady=25)   
        
    def show_logs(self):
        # Εμφάνιση του detection.log στο UI σε νέο παράθυρο.
        win = tk.Toplevel(self.root)
        win.title("Detection History")
        txt = scrolledtext.ScrolledText(win, width=70, height=20)
        txt.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        logs_path = Labyrinth.get_results_file_path('detections.log')

        try:
            with open(logs_path, "r") as f:
                data = f.read().strip()
            txt.insert(tk.INSERT, data if data else "No logs yet.")
        except:
            txt.insert(tk.INSERT, "No logs found.")
        txt.bind("<Key>", lambda e: "break")
        txt.yview(tk.END)

    def on_exit(self):
        # Exit button - για το ομαλό κλείσιμο της εφαρμογής.
        if messagebox.askokcancel("Exit", "Quit system?"):
            AuthService.logout()
            self.stop_camera()
            self.root.destroy()
            os._exit(0)

    def open_user_management(self):
        #region Comments
        # Διαχείριση χρηστών - User Management
        # Ελεγχος πρώτα με βάση το RBAC - το policy είναι ΜΟΝΟ user.role.ADMINISTRATOR Μπορεί να το χειριστεί!
        # ΔΕΝ έχουμε τα Policies σε ξεχωριστό αρχείο policy.py λόγω μεγέθους εφαρμογής- ΚΑΝΟΝΙΚΑ ΠΡΕΠΕΙ.
        # Εδώ το χειριζόμαστε "μπακαλίστικα" - απλουστευμένα - ακατάλληλο για Enterprize class εφαρμογή!
        #endregion
        if SessionManager.get_role() != "ADMINISTRATOR":
            messagebox.showerror("Access Denied", "Μόνο ο ΔΙΑΧΕΙΡΙΣΤΗΣ έχει πρόσβαση.", parent=self.root)
            return

        win = tk.Toplevel(self.root)
        win.title("Manage Users")
        win.geometry("550x450")
        win.transient(self.root)
        win.grab_set()

        tabs = ttk.Notebook(win)
        tabs.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Πρώτο tab : CREATE
        tab_create = tk.Frame(tabs)
        tabs.add(tab_create, text="Create User")

        tk.Label(tab_create, text="Username:").pack(pady=(20, 5))
        new_username_input = tk.Entry(tab_create, width=30)
        new_username_input.pack()

        tk.Label(tab_create, text="Password:").pack(pady=5)
        new_paswd_input = tk.Entry(tab_create, width=30, show="*")
        new_paswd_input.pack()

        tk.Label(tab_create, text="Role:").pack(pady=5)
        combobox_role = ttk.Combobox(tab_create, values=["supervisor", "user"], state="readonly")
        combobox_role.current(0)
        combobox_role.pack()

        def save_user():
            # Αποθήκευση νέου χρήστη
            u = new_username_input.get().strip()
            p = new_paswd_input.get().strip()
            r = combobox_role.get().strip() 
            
            if not u or not p:
                messagebox.showwarning("Warning", "Τα πεδία δεν μπορεί να είναι κενά!", parent=win)
                return
                
            success, message = UserManagementService.create_user(u, p, r)
            if success:
                messagebox.showinfo("Success", message, parent=win)
                new_username_input.delete(0, tk.END)
                new_paswd_input.delete(0, tk.END)
                load_users()
            else:
                messagebox.showerror("Error", message, parent=win)
                
        tk.Button(tab_create, text="Save User", bg="#27ae60", fg="white", command=save_user).pack(pady=25)

        # Δεύτερο tab : MANAGE
        tab_manage = tk.Frame(tabs)
        tabs.add(tab_manage, text="Manage Users")

        columns = ("id", "username", "role")
        tree = ttk.Treeview(tab_manage, columns=columns, show="headings", height=10)
        tree.heading("id", text="ID")
        tree.heading("username", text="Username")
        tree.heading("role", text="Role")
        tree.column("id", width=50, anchor=tk.CENTER)
        tree.column("username", width=200, anchor=tk.W)
        tree.column("role", width=150, anchor=tk.CENTER)
        tree.pack(pady=10, fill=tk.BOTH, expand=True)

        def load_users():
            # Φόρτωση των χρηστών της ΒΔ μας - ΟΧΙ ADMINS!! το χειριζόμαστε από το user_services.py
            for item in tree.get_children():
                tree.delete(item)
            users = UserManagementService.get_manageable_users()
            for u in users:
                tree.insert("", tk.END, values=(u['id'], u['username'], u['role']))

        def delete_user():
            # Διαγραφή χρήστη από τη βάση μας
            selected = tree.selection()
            if not selected: return
            item = tree.item(selected[0])
            uid, uname = item['values'][0], item['values'][1]
            
            if messagebox.askyesno("Confirm", f"Διαγραφή του χρήστη: {uname};", parent=win):
                success, message = UserManagementService.delete_user(uid)
                if success:
                    messagebox.showinfo("Success", f"Ο χρήστης {uname} διαγράφηκε.", parent=win)
                    load_users()
                else:
                    messagebox.showerror("Error", message, parent=win)

        def update_user():
            # Ενημέρωση στοιχείων χρήστη 
            selected = tree.selection()
            if not selected: return
            item = tree.item(selected[0])
            uid, uname, urole = item['values'][0], item['values'][1], item['values'][2]

            upd_win = tk.Toplevel(win)
            upd_win.title(f"Update: {uname}")
            upd_win.geometry("300x250")
            upd_win.transient(win)
            upd_win.grab_set()

            tk.Label(upd_win, text="New Password\n(αφήστε κενό για διατήρηση παλιού):").pack(pady=10)
            user_new_paswd = tk.Entry(upd_win, width=25, show="*")
            user_new_paswd.pack()

            tk.Label(upd_win, text="Change Role:").pack(pady=10)
            user_new_role = ttk.Combobox(upd_win, values=["USER", "SUPERVISOR"], state="readonly")
            user_new_role.set(urole)
            user_new_role.pack()

            def save_update():
                # Αποθήκευση ενημερωμένων στοιχείων
                new_p = user_new_paswd.get().strip()
                new_r = user_new_role.get().strip()
                
                if messagebox.askyesno("Confirm", f"Ενημέρωση του χρήστη: {uname};", parent=win):
                    success, message = UserManagementService.update_user(uid, new_p, new_r)
                    if success:
                        messagebox.showinfo("Success", f"Ο χρήστης {uname} ενημερώθηκε.", parent=win)
                        upd_win.destroy()
                        load_users()
                    else:
                        messagebox.showerror("Error", message, parent=win)

            tk.Button(upd_win, text="Save Update", bg="#2980b9", fg="white", command=save_update).pack(pady=20)

        btn_frame = tk.Frame(tab_manage)
        btn_frame.pack(pady=5)
        tk.Button(btn_frame, text="Edit", bg="#f39c12", fg="white", command=update_user).pack(side=tk.LEFT, padx=10)
        tk.Button(btn_frame, text="Delete", bg="#c0392b", fg="white", command=delete_user).pack(side=tk.LEFT, padx=10)

        load_users()
