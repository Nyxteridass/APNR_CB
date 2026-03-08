import time
import cv2

#Βοηθητικές μέθοδοι

def now_ts():
    # Δημιουργία timestamp
    return time.strftime('%Y-%m-%d %H:%M:%S')


def clamp(v, lo, hi):
    # Περιορισμός τιμής v στο διάστημα [lo, hi]
    return max(lo, min(hi, v))


def letterbox(image, new_shape=(320, 320), color=(114, 114, 114)):
    # Προσαρμογή μεγέθους της εικόνας /  φορμάρισμα της εικόνας με padding
    h, w = image.shape[:2]
    new_w, new_h = new_shape

    r = min(new_w / w, new_h / h)
    nw, nh = int(round(w * r)), int(round(h * r))

    img_resized = cv2.resize(image, (nw, nh), interpolation=cv2.INTER_LINEAR)

    dw = new_w - nw
    dh = new_h - nh
    left = dw // 2
    right = dw - left
    top = dh // 2
    bottom = dh - top

    img_lb = cv2.copyMakeBorder(img_resized, top, bottom, left, right,
                                cv2.BORDER_CONSTANT, value=color)
    return img_lb, r, (left, top)


def preprocess_for_ocr(roi_bgr):
    # Προ-επεξεργασία του Region of Interest (ROI) για τη χρήση του OCR.
    if roi_bgr is None or roi_bgr.size == 0:
        return None
    gray = cv2.cvtColor(roi_bgr, cv2.COLOR_BGR2GRAY)
    gray = cv2.resize(gray, None, fx=2.5, fy=2.5, interpolation=cv2.INTER_CUBIC)
    gray = cv2.bilateralFilter(gray, 7, 50, 50)
    gray = cv2.equalizeHist(gray)
    _, th = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return th

