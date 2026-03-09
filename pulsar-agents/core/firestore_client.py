import os
import json
from google.cloud import firestore
from google.oauth2 import service_account


def get_db():
    """Get Firestore client using service account from GitHub Secret."""
    creds_json = os.environ.get("FIREBASE_SERVICE_ACCOUNT")
    if not creds_json:
        raise ValueError("FIREBASE_SERVICE_ACCOUNT env var not set")

    creds_dict = json.loads(creds_json)
    credentials = service_account.Credentials.from_service_account_info(
        creds_dict,
        scopes=["https://www.googleapis.com/auth/cloud-platform"]
    )
    return firestore.Client(project="pulsar-bb144", credentials=credentials)


def get_all_users(db):
    """Fetch all users from Firestore."""
    users = []
    docs = db.collection("users").stream()
    for doc in docs:
        data = doc.to_dict()
        data["_docId"] = doc.id
        users.append(data)
    return users


def upsert_document(db, collection: str, doc_id: str, data: dict):
    """Upsert a document into Firestore."""
    ref = db.collection(collection).document(doc_id)
    ref.set(data, merge=True)
