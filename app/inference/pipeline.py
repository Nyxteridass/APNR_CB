import cv2
import numpy as np
import os
import app.core.config1 as config
from app.utils.helpers import letterbox, clamp
from app.utils.pathfinder import Labyrinth
from app.services.logger import log_error
from fast_plate_ocr import LicensePlateRecognizer

class InferencePipeline:
    def __init__(self, ocr_model_name):
        #Αρχικοποίηση του μοντέλου ανίχνευσης πινακίδων
        try:
            model_path = Labyrinth.get_model_detector()
            self.net = cv2.dnn.readNetFromONNX(model_path)
            self.net.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV)
            self.net.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)
        except Exception as e:
            file_name = os.path.basename(__file__) 
            error_type = type(e).__name__
        
            log_error(error_type, file_name, str(e))
            self.net = None

        try:
            self.recognizer = LicensePlateRecognizer(ocr_model_name)
        except Exception as e:
            file_name = os.path.basename(__file__) 
            error_type = type(e).__name__
        
            log_error(error_type, file_name, str(e))
            self.recognizer = None
    
    
    def load_ocr(self, model_name):
        try:
            self.recognizer = LicensePlateRecognizer(model_name)
        except Exception as e:
            file_name = os.path.basename(__file__) 
            error_type = type(e).__name__
        
            log_error(error_type, file_name, str(e))
            self.recognizer = None
    
    
    
    def detect_and_ocr(self, frame_bgr):
        if self.net is None or frame_bgr is None:
            return []

        # 1. Letterbox & Inference
        img_lb, r, (pad_x, pad_y) = letterbox(frame_bgr, (config.MODEL_INP, config.MODEL_INP))
        blob = cv2.dnn.blobFromImage(img_lb, 1 / 255.0, (config.MODEL_INP, config.MODEL_INP), swapRB=True, crop=False)
        self.net.setInput(blob)
        outputs = self.net.forward()

        out = np.squeeze(outputs)

        # Ασφαλής Διαχείριση Output και προετοιμασία για NMS. 
        # Εδώ διασφαλίζουμε ότι το output έχει τη σωστή μορφή, ανεξάρτητα από το αν το μοντέλο επέστρεψε 1D ή 2D array,
        #  ή αν τα δεδομένα είναι σε xywh format ή normalized.
        if out.ndim == 2:
            if out.shape[0] < out.shape[1] and out.shape[0] in (5, 6, 7, 8, 85, 84):
                out = out.T
        elif out.ndim == 1:
            return []
        else:
            out = out.reshape(-1, out.shape[-1])

        if out.shape[1] < 5:
            return []

        boxes = []
        confs = []

        sample = out[:min(50, out.shape[0]), :4]
        max_xywh = float(np.max(sample)) if sample.size else 0.0
        normalized_xywh = max_xywh <= 2.0

        for i in range(out.shape[0]):
            x, y, w, h = out[i, 0], out[i, 1], out[i, 2], out[i, 3]

            if out.shape[1] == 5:
                conf = float(out[i, 4])
            else:
                obj = float(out[i, 4])
                cls_probs = out[i, 5:]
                conf = obj * float(np.max(cls_probs)) if cls_probs.size > 0 else obj

            if conf < config.CONF_THRESHOLD:
                continue

            if normalized_xywh:
                x *= config.MODEL_INP
                y *= config.MODEL_INP
                w *= config.MODEL_INP
                h *= config.MODEL_INP

            left = (x - 0.5 * w - pad_x) / r
            top = (y - 0.5 * h - pad_y) / r
            right = (x + 0.5 * w - pad_x) / r
            bottom = (y + 0.5 * h - pad_y) / r

            x0 = int(clamp(left, 0, config.FRAME_WIDTH - 1))
            y0 = int(clamp(top, 0, config.FRAME_HEIGHT - 1))
            x1 = int(clamp(right, 0, config.FRAME_WIDTH - 1))
            y1 = int(clamp(bottom, 0, config.FRAME_HEIGHT - 1))

            bw = max(1, x1 - x0)
            bh = max(1, y1 - y0)

            boxes.append([x0, y0, bw, bh])
            confs.append(conf)

        if not boxes:
            return []

        # NMS
        idxs = cv2.dnn.NMSBoxes(boxes, confs, config.CONF_THRESHOLD, config.NMS_THRESHOLD)
        if len(idxs) == 0:
            return []

        results = []
        for it in idxs:
            k = int(it[0]) if isinstance(it, (list, tuple, np.ndarray)) else int(it)
            bx = boxes[k]
            conf = confs[k]

            # OCR Logic - Προσπαθούμε να αναγνωρίσουμε την πινακίδα μέσα στο ανιχνευμένο πλαίσιο. 
            # Εάν το απευθείας ROI δεν δουλέψει (π.χ. λόγω μεγέθους ή μορφής), αποθηκεύουμε προσωρινά την εικόνα και προσπαθούμε ξανά,
            #  για να αυξήσουμε τις πιθανότητες επιτυχίας.
            roi = frame_bgr[bx[1]:bx[1] + bx[3], bx[0]:bx[0] + bx[2]]
            raw_text = ""
            
            if roi is not None and roi.size != 0 and self.recognizer is not None:
                try:
                    raw_text = self.recognizer.run(roi)
                except Exception:
                    try:
                        import tempfile
                        fd, tmp_path = tempfile.mkstemp(suffix=".jpg")
                        os.close(fd)
                        cv2.imwrite(tmp_path, roi)
                        raw_text = self.recognizer.run(tmp_path)
                        os.remove(tmp_path)
                    except:
                        raw_text = ""

            if isinstance(raw_text, list):
                raw_text = raw_text[0] if len(raw_text) > 0 else ""
            raw_text = (raw_text or "")
            if not isinstance(raw_text, str):
                raw_text = str(raw_text)
            raw_text = raw_text.strip()

            results.append({
                'box': bx,
                'text': raw_text.upper(),
                'confidence': float(conf)
            })

        return results
