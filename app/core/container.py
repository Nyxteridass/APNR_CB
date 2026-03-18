from app.inference.pipeline import InferencePipeline
from app.services.detection_services import DetectionService 
from app.core import config1

class Container:
    def __init__(self):
        # 1. Αρχικοποίηση του AI Pipeline
        model_name = config1.FAST_OCR_MODELS[0] 
        self.pipeline = InferencePipeline(model_name)
        
        # 2. Αρχικοποίηση του Service της βάσης
        self.detection_service = DetectionService()
