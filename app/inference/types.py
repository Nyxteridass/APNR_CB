from dataclasses import dataclass
from typing import  Tuple

#Dataclass για να περνάμε τα αποτελέσματα της ανίχνευσης καθαρά.

@dataclass
class DetectionResult:
    box: Tuple[int, int, int, int]  # [x, y, w, h]
    confidence: float
    plate_text: str = ""
    status: str = "CLEAN"