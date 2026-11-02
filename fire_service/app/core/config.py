import os
from pathlib import Path
from dotenv import load_dotenv
import os
load_dotenv()
BASE_DIR = Path(__file__).resolve().parent.parent.parent

MODEL_PATH = BASE_DIR / "models" / "best_1.pt"
DEFAULT_SOURCE =0
#  BASE_DIR / "source" / "video.mp4"
ALERT_AUDIO_PATH = BASE_DIR / "source" / "alert.mp3"

# 💡 Auto-create Snapshots Directory
SNAPSHOT_DIR = BASE_DIR / "snapshots"
SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)

# 💡 Auto-create Clips Directory (Video Evidence)
CLIP_DIR = BASE_DIR / "clips"
CLIP_DIR.mkdir(parents=True, exist_ok=True)

CONF_THRESHOLD = 0.50

#  load the key and path for s3 storage
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')  # Get the AWS access key ID from environment variables
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')  # Get
S3_BUCKET_NAME= os.getenv('S3_BUCKET_NAME')  # Get the S3 bucket name from environment variables
S3_FOLDER=  os.getenv('S3_FOLDER')  # Get the S3 folder name from environment variables
S3_URL = os.getenv('S3_URL')  # Get the S3 URL from environment variables