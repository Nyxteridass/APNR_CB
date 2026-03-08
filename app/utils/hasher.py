import bcrypt

# Χρήση της βιβλιοθήκης bcrypt για την βέλτιστη αφάλεια κωδικών. 
# η ενσωματωμένη χρήση salt αυξάνει την ασφάλεια.

def hash_password(password: str) -> str:
    # Κάνουμε encode το password σε bytes- απαραίτητο για να λειτουργήσει το bcrypt.
    password_bytes = password.encode('utf-8')
    
    # Δημιουργούμε το salt και το hash
    salt = bcrypt.gensalt()
    hashed_bytes = bcrypt.hashpw(password_bytes, salt)
    
    # Επιστρέφουμε string για τη συναλλαγή- καλύτερη διαχείριση στη ΒΔ μας.
    return hashed_bytes.decode('utf-8')

def verify_password(stored_hash: str, provided_password: str) -> bool:
    # Μετατρέπουμε το provided_password και το stored_hash σε bytes για να γίνει σύγκριση.
    if not stored_hash or not provided_password:
        return False  # Αν κάποιο από τα δύο είναι κενό, δεν μπορεί να ταιριάξει -ΑΠΟΡΡΙΨΗ
    

    provided_password_bytes = provided_password.encode('utf-8')
    stored_hash_bytes = stored_hash.encode('utf-8')
    
    try:
        # Η checkpw ελέγχει αυτόματα το salt και το hash
        return bcrypt.checkpw(provided_password_bytes, stored_hash_bytes)
    except ValueError:
        # Σε περίπτωση που το stored_hash δεν είιναι έγκυρο hash, απορρίπτουμε την προσπάθεια.
        return False