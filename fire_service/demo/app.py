# # =============== for the image===========
# from ultralytics import YOLO
# import cv2


# model = YOLO(r'F:\Fire_Detection_service\runs\detect\train-2\weights\best.pt')

# results = model.predict(
#     r'F:\Fire_Detection_service\fire_service\demo\img\img1.png',
#     conf=0.05,
#     imgsz=640
# )

# # print(model.names)
# # print(results[0].boxes)
# detections=[]
# for box in results[0].boxes:
#     conf=float(box.conf[0])
#     class_id=int(box.cls[0])
#     class_name=model.names[class_id]
#     x1,y1,x2,y2=box.xyxy[0].tolist()
#     detection={
#         'class':class_name,
#         'confidence':round(conf,4),
#         'bbox': {
#             'x1': int(x1),
#             'y1': int(y1),
#             'x2': int(x2),
#             'y2': int(y2)
#         }
#     }
#     detections.append(detection)
# print(f"all data {detections}")
# annotated = results[0].plot()

# cv2.imshow('Fire Detection', annotated)
# cv2.waitKey(0)
# cv2.destroyAllWindows()

# for videp==================
from ultralytics import YOLO
import cv2
import pygame 

vdo_path=r"F:\Fire_Detection_service\fire_service\demo\vdo\video.mp4"

model = YOLO(r'F:\Fire_Detection_service\runs\detect\train-2\weights\best.pt')
cap=cv2.VideoCapture(vdo_path)


alert_playing=False
pygame.mixer.init()
def trigger_fire_alert(class_name,confidence):
    global alert_playing
    if (class_name=='fire' or class_name=='smoke') and confidence > 0.30:
        if not alert_playing:
            
            pygame.mixer.music.load(r"F:\Fire_Detection_service\fire_service\demo\vdo\alert.mp3")
            pygame.mixer.music.play(-1)
            alert_playing=True
    else :
        if alert_playing:
            pygame.mixer.music.stop()
            alert_playing=False
    print(f'DEBUG -> {class_name} | {confidence}')

while True:
    ret , frame =cap.read()
    if not ret:
        break
    results = model.predict(frame, conf=0.25, imgsz=960,verbose=False)

    detections=[]
    for box in results[0].boxes:
        conf=float(box.conf[0])
        class_id=int(box.cls[0])
        class_name=model.names[class_id]
        x1,y1,x2,y2=box.xyxy[0].tolist()
        detection={
            'class':class_name,
            'confidence':round(conf,4),
            'bbox': {
               'x1': int(x1),
               'y1': int(y1),
               'x2': int(x2),
               'y2': int(y2)
        }
    }
        detections.append(detection)
        trigger_fire_alert(detection['class'],detection['confidence'])
    print(f"all data {detections}")
    
    annotated=results[0].plot()
    cv2.imshow("fire detection",annotated)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()