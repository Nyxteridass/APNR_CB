import tkinter as tk
from app.ui.gui_login import LoginWindow
from app.ui.gui_main import MainWindow
from app.core.container import Container


def launch_main_app():
    # Η συνάρτηση που καλείται μετά από επιτυχημένο login και ξεκινάει το κύριο παράθυρο.
    root = tk.Tk()    
    # Αρχικοποίηση Container (Inference + Services)
    # Εδώ φορτώνονται τα μοντέλα ONNX και η σύνδεση με τη ΒΔ
    try:
        app_container = Container()
    except Exception as e:
        from tkinter import messagebox
        messagebox.showerror("Initialization Error", f"Αποτυχία εκκίνησης συστήματος: {e}")
        return

    # Εκκίνηση MainWindow
    # Περνάμε το container ώστε το UI να έχει πρόσβαση στο AI και τη Βάση
    app = MainWindow(root, "APNR - Edge Computing / RPi 3B+ Christos Besiris", app_container)
   
    root.mainloop()

if __name__ == "__main__":
    # Το πρόγραμμα ξεκινάει πάντα από το Login
    # Το LoginWindow θα καλέσει τη launch_main_app μόνο αν τα credentials είναι σωστά
    LoginWindow(on_success=launch_main_app)

