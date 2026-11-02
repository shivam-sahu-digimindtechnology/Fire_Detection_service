import pygame
from app.core.config import ALERT_AUDIO_PATH

class AlertService:
    def __init__(self):
        pygame.mixer.init()
        self.is_playing = False
        try:
            pygame.mixer.music.load(str(ALERT_AUDIO_PATH))
        except Exception as e:
            print(f" Warning: Audio load failed: {e}")

    def process_alerts(self, detections, conf_threshold=0.30):
       
        threats = [
            d for d in detections 
            if d['class'] in ['fire', 'smoke'] and d['confidence'] >= conf_threshold
        ]

        has_alert = len(threats) > 0

        
        if has_alert:
            if not self.is_playing:
                try:
                    pygame.mixer.music.play(-1) 
                    self.is_playing = True
                except Exception as e:
                    print(f"Audio error: {e}")
        else:
            if self.is_playing:
                pygame.mixer.music.stop()
                self.is_playing = False

        
        highest_threat = max(threats, key=lambda x: x['confidence']) if threats else None

        return {
            "alert_triggered": has_alert,
            "alarm_active": self.is_playing,
            "threat_count": len(threats),
            "top_threat": highest_threat['class'] if highest_threat else "none",
            "max_confidence": highest_threat['confidence'] if highest_threat else 0.0,
            "message": "CRITICAL: Fire or Smoke Detected!" if has_alert else "Status Normal"
        }