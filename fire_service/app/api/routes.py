from fastapi import APIRouter, Query, HTTPException
from fastapi.responses import StreamingResponse
from app.core.stream_manager import StreamManager

router = APIRouter()
stream_engine = StreamManager()

@router.get('/api/v1/status')
def status():
    return {"running": stream_engine.is_running, "active_source": str(stream_engine.source)}

@router.post('/api/v1/start')
def start_detection(source: str = Query(None, description="Path to video or '0' for Webcam")):
    success = stream_engine.start(source_url=source)
    if not success:
        raise HTTPException(status_code=400, detail="Camera open nahi hua.")
    return {"running": True, "source_used": str(stream_engine.source)}

@router.post('/api/v1/stop')
def stop_detection():
    stream_engine.stop()
    return {"running": False, "message": "Stopped"}

def generate_mjpeg_stream():
    while stream_engine.is_running:
        frame_bytes = stream_engine.get_jpeg_frame()
        if frame_bytes:
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
        else:
            import time
            time.sleep(0.02)

@router.get('/api/v1/stream')
def video_stream():
    if not stream_engine.is_running:
        stream_engine.start()
    return StreamingResponse(generate_mjpeg_stream(), media_type='multipart/x-mixed-replace; boundary=frame')

@router.get('/api/v1/detections')
def get_detections():
    
    if not stream_engine.is_running:
        return {
            "service_active": False,
            "current_detections_count": 0,
            "total_history_records": 0,
            "alert_status": {
                "alert_triggered": False,
                "alarm_active": False,
                "message": "Service Off"
            },
            "current_detections": [],
            "detection_history": []
        }

    current_detections, alert_info, history = stream_engine.get_all_data()

    return {
        "service_active": True,
        "source": str(stream_engine.source), # used for camera id future
        "current_detections_count": len(current_detections),
        "total_history_records": len(history),
        "alert_status": alert_info,
        "current_detections": current_detections,
        "detection_history": history # 👈 Ab refresh karne par bhi pura data milega
    }