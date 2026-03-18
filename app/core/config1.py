import cv2
# =================================
# CONFIGURATION FILE για το RPi 3B+
# =================================
CAMERA_ID = 0

# Capture video size - ιδιαίτερα σημαντικό για την απόδοση σε Pi 3B+
FRAME_WIDTH = 640 #320
FRAME_HEIGHT = 480 #240

# Display refresh (UI) and detection cadence (CPU) - ιδιαίτερα σημαντικό για την απόδοση σε Pi 3B+
GUI_FPS = 15
DETECT_EVERY_N_FRAMES = 3
OCR_INTERVAL_SEC = 0.45
MAX_DETECTIONS_DRAW = 3

# Greek plate whitelist / χαρακτήρες που επιτρέπονται στις Ελληνικές πινακίδες
GREEK_CHARS = "ABEZHIKMNOPTYX"
DIGITS = "0123456789"

CONF_THRESHOLD = 0.45
NMS_THRESHOLD = 0.50
MODEL_INP = 320

FAST_OCR_MODELS = [
    "cct-xs-relu-v1-global-model",
    "cct-xs-v1-global-model",
    "cct-s-relu-v1-global-model",
    "cct-s-v1-global-model",
    "european-plates-mobile-vit-v2-model",
]
try:
    cv2.setNumThreads(2)
except:
    pass

