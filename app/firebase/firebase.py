import os
import firebase_admin
from firebase_admin import credentials, firestore

# Current folder ka path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# JSON file ka path
KEY_PATH = os.path.join(
    BASE_DIR,
    "keys",
    "kings-hostel-management-firebase-adminsdk-fbsvc-8d09315f89.json"
)

# Firebase initialize
if not firebase_admin._apps:
    cred = credentials.Certificate(KEY_PATH)
    firebase_admin.initialize_app(cred)

# Firestore Database
db = firestore.client()

print("✅ Firebase Connected Successfully")