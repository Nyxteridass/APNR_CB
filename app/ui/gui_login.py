import tkinter as tk
from tkinter import messagebox
from app.utils.sound import SoundGenerator
from app.services.services import AuthService

class LoginWindow:
    def __init__(self, on_success):
        #Δημιουργία του login window
        self.root = tk.Tk()
        self.root.title("APNR System - Login")
        self.root.geometry("350x250")
        self.root.resizable(False, False)
        self.on_success = on_success

        tk.Label(self.root, text="ΣΥΣΤΗΜΑ APNR", font=("Arial", 14, "bold")).pack(pady=20)
        
        tk.Label(self.root, text="Username:").pack()
        self.ent_user = tk.Entry(self.root, width=25)
        self.ent_user.pack(pady=5)

        tk.Label(self.root, text="Password:").pack()
        self.ent_pass = tk.Entry(self.root, show="*", width=25)
        self.ent_pass.pack(pady=5)

        tk.Button(self.root, text="LOGIN", bg="#27ae60", fg="white", width=15,
                  command=self.handle_login).pack(pady=20)
        
        self.root.mainloop()

    def handle_login(self):
        user = self.ent_user.get()
        pw = self.ent_pass.get()
        
        # Καλούμε το Service που ελέγχει τη βάση
        if AuthService.login(user, pw):
            self.root.destroy()
            
            _sg= SoundGenerator()
            
            _sg.play_welcome_intro()
            self.on_success() # Αυτό θα ανοίξει το gui_main
        else:
            messagebox.showerror("Error", "Invalid credentials")
