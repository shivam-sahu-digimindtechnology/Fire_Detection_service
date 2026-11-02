from datetime import datetime, timezone
import cv2
import json
import os
from pathlib import Path
from ultralytics import YOLO
from app.core.config import MODEL_PATH, CONF_THRESHOLD, BASE_DIR
from app.services.s3_service import S3StorageService

class FireSmokeDetector:

    def __init__(self, model_path=None):
        path = str(model_path) if model_path else str(MODEL_PATH)
        self.model = YOLO(path)
        self.s3_service = S3StorageService()
        
        # 💡 Counter to track image savings (Every 5th image rule)
        self.image_capture_counter = 0

    def get_dynamic_local_paths(self):
        """Local path creation: BASE_DIR/fire_detection_data/DD-MM-YYYY/images/"""
        now = datetime.now(timezone.utc)
        date_folder_name = now.strftime("%d-%m-%Y")

        base_path = BASE_DIR / "fire_detection_data" / date_folder_name
        images_path = base_path / "images"

        base_path.mkdir(parents=True, exist_ok=True)
        images_path.mkdir(parents=True, exist_ok=True)

        return base_path, images_path

    def detect(self, frame, current_global_id=0, camera_id="CAM_DEFAULT", camera_name="Building North Wing"):
        results = self.model.predict(
            frame,
            conf=CONF_THRESHOLD,
            imgsz=960,
            verbose=False
        )

        detections = []
        next_id = current_global_id
        annotated_frame = results[0].plot() if results else frame

        if results and len(results) > 0 and len(results[0].boxes) > 0:
            now_utc = datetime.now(timezone.utc)
            date_time_str = now_utc.strftime("%d_%m_%Y_%H_%M_%S")
            iso_timestamp = now_utc.strftime("%Y-%m-%dT%H:%M:%SZ")

            # Dynamic Local Directory Paths
            json_dir, images_dir = self.get_dynamic_local_paths()

            for box in results[0].boxes:
                conf = float(box.conf[0])
                class_id = int(box.cls[0])
                class_name = self.model.names[class_id]
                x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())

                box_width = x2 - x1
                box_height = y2 - y1
                fire_area = box_width * box_height

                if conf >= 0.80 or fire_area > 30000:
                    severity = "HIGH"
                elif conf >= 0.50 or fire_area > 10000:
                    severity = "MEDIUM"
                else:
                    severity = "LOW"

                next_id += 1
                self.image_capture_counter += 1

                snapshot_url = ""
                clip_url = ""

                # 💡 RULE: Har 5th detection par image save aur S3 upload hoga
                if self.image_capture_counter % 5 == 0:
                    snapshot_filename = f"{class_name}_{next_id}_{now_utc.strftime('%Y%m%dT%H%M%SZ')}.jpg"
                    snapshot_filepath = images_dir / snapshot_filename
                    cv2.imwrite(str(snapshot_filepath), annotated_frame)

                    clip_filename = f"clip_{next_id}_{now_utc.strftime('%Y%m%dT%H%M%SZ')}.mp4"
                    clip_filepath = images_dir / clip_filename

                    # ☁️ S3 Upload to `company_doc/fire_detection_data/DD-MM-YYYY/images/`
                    snapshot_url = self.s3_service.upload_file_async(
                        file_path=snapshot_filepath,
                        filename=snapshot_filename,
                        is_image_or_clip=True,
                        content_type="image/jpeg"
                    )

                    clip_url = self.s3_service.upload_file_async(
                        file_path=clip_filepath,
                        filename=clip_filename,
                        is_image_or_clip=True,
                        content_type="video/mp4"
                    )

                # Detection Item Payload
                detection_item = {
                    "id": next_id,
                    "camera_id": str(camera_id),
                    "camera_name": camera_name,
                    "timestamp": iso_timestamp,
                    "class": class_name,
                    "confidence": round(conf, 4),
                    "severity": severity,
                    "bbox": {
                        "x1": x1,
                        "y1": y1,
                        "x2": x2,
                        "y2": y2
                    },
                    "fire_area": fire_area,
                    "snapshot_url": snapshot_url,
                    "clip_url": clip_url,
                    "alarm_sent": True,
                    "status": "ACTIVE"
                }

                # 📄 Save JSON File locally & Upload to S3 (`company_doc/fire_detection_data/DD-MM-YYYY/`)
                json_filename = f"FireDetection_{date_time_str}_{next_id}.json"
                json_filepath = json_dir / json_filename
                
                with open(json_filepath, 'w') as f:
                    json.dump(detection_item, f, indent=2)

                self.s3_service.upload_file_async(
                    file_path=json_filepath,
                    filename=json_filename,
                    is_image_or_clip=False,
                    content_type="application/json"
                )

                detections.append(detection_item)

        return annotated_frame, detections, next_id