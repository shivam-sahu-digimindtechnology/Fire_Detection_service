import cv2
import threading
import time
from app.detector.fire_detector import FireSmokeDetector
from app.core.config import DEFAULT_SOURCE, CONF_THRESHOLD
from app.services.alert_service import AlertService

class StreamManager:
    def __init__(self, source=None, camera_id="CAM_DEFAULT", camera_name="Building North Wing"):
        self.source = str(source) if source else str(DEFAULT_SOURCE)
        self.camera_id = camera_id
        self.camera_name = camera_name
        
        self.cap = None
        self.is_running = False
        self.detector = FireSmokeDetector()
        self.alert_service = AlertService()
        
        self.current_annotated_frame = None
        self.latest_detections = []
        self.latest_alert_status = {}
        self.detection_history = []

        self.global_detection_counter = 0

        # Continuous Verification Logic
        self.consecutive_threat_count = 0
        self.REQUIRED_CONSECUTIVE_FRAMES = 1 
        self.CONFIDENCE_THRESHOLD = CONF_THRESHOLD

        self.thread = None
        self.lock = threading.Lock()

    def start(self, source_url=None, camera_id=None, camera_name=None):
        if self.is_running:
            return True

        if source_url is not None:
            self.source = str(source_url)
            
        if camera_id:
            self.camera_id = camera_id
        if camera_name:
            self.camera_name = camera_name

        if str(self.source).isdigit():
            self.source = int(self.source)

        self.cap = cv2.VideoCapture(self.source)
        if not self.cap.isOpened():
            print(f"Error: Camera/Video source open nahi hua: {self.source}")
            return False

        self.is_running = True
        self.thread = threading.Thread(target=self._capture_loop, daemon=True)
        self.thread.start()
        print(f"Camera/Video Started: {self.source}")
        return True

    def _capture_loop(self):
        frame_count = 0
        SKIP_FRAMES = 2  

        while self.is_running:
            if self.cap is None or not self.cap.isOpened():
                break

            ret, frame = self.cap.read()
            if not ret:
                if isinstance(self.source, str) and not str(self.source).startswith("rtsp://"):
                    self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                    continue
                else:
                    time.sleep(0.05)
                    continue

            frame_count += 1
            if frame_count % SKIP_FRAMES == 0:
                annotated_frame, raw_detections, updated_counter = self.detector.detect(
                    frame, 
                    current_global_id=self.global_detection_counter,
                    camera_id=self.camera_id,
                    camera_name=self.camera_name
                )

                valid_threats = [
                    d for d in raw_detections 
                    if d['class'] in ['fire', 'smoke'] and d['confidence'] >= self.CONFIDENCE_THRESHOLD
                ]

                if len(valid_threats) > 0:
                    self.consecutive_threat_count += 1
                else:
                    self.consecutive_threat_count = 0

                if self.consecutive_threat_count >= self.REQUIRED_CONSECUTIVE_FRAMES:
                    verified_detections = valid_threats
                    self.global_detection_counter = updated_counter
                else:
                    verified_detections = []

                alert_status = self.alert_service.process_alerts(verified_detections)

                with self.lock:
                    self.current_annotated_frame = annotated_frame
                    self.latest_detections = verified_detections
                    self.latest_alert_status = alert_status

                    if len(verified_detections) > 0:
                        print(f"VERIFIED FIRE DETECTED -> {verified_detections}")
                        for item in verified_detections:
                            self.detection_history.append(item.copy())

            else:
                with self.lock:
                    if self.current_annotated_frame is None:
                        self.current_annotated_frame = frame

            time.sleep(0.01)

    def get_jpeg_frame(self):
        with self.lock:
            if self.current_annotated_frame is None:
                return None
            ret, jpeg = cv2.imencode('.jpg', self.current_annotated_frame)
            return jpeg.tobytes() if ret else None

    def get_all_data(self):
        with self.lock:
            return (
                list(self.latest_detections),
                dict(self.latest_alert_status),
                list(self.detection_history)
            )

    def stop(self):
        self.is_running = False
        if self.cap and self.cap.isOpened():
            self.cap.release()
        self.cap = None
        self.current_annotated_frame = None
        self.latest_detections = []
        self.detection_history = []
        self.consecutive_threat_count = 0
        self.alert_service.process_alerts([])