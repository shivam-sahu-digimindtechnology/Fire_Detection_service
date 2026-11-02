import cv2
from detector.fire_detector import FireSmokeDetector
from core.config import DEFAULT_SOURCE
from services.alert_service import AlertService

def run_fire_detection_service():
    detector = FireSmokeDetector()
    alert_service = AlertService()
    
    # Video source standard config se read kar raha hai
    cap = cv2.VideoCapture(str(DEFAULT_SOURCE))

    while True:
        ret, frame = cap.read()
        if not ret:
            break
            
        annotated_frame, detections = detector.detect(frame)
        
        # Alert Triggering logic
        alert_status = alert_service.process_alerts(detections)
        
        if len(detections) > 0:
            print(f" DETECTIONS: {detections}")
            print(f" ALERT STATUS: {alert_status}")

        cv2.imshow('Fire & Smoke Local Test', annotated_frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    alert_service.process_alerts([]) # Stop siren on exit

if __name__ == "__main__":
    run_fire_detection_service()