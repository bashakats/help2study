import firebase_admin
from firebase_admin import firestore
from firebase_admin import credentials
import threading
from typing import List

credential = credentials.Certificate("LocalFiles/h2s_key.json")
admin = firebase_admin.initialize_app(credential)
fs_db = firestore.client()

# Create an Event for notifying main thread.
callback_done = threading.Event()


# Create a callback on_snapshot function to capture changes
def on_snap_shot(doc_snapshot, changes, read_time):
    for doc in doc_snapshot:
        payment_request = doc.to_dict()
        print(f"Received document snapshot: {payment_request}")
        # Handling payment
        # ...
        donation = {"donator": "Sharif", "amount": 100}

        # get users donations
        user = (
            fs_db.collection("users")
            .document("7ZdsBiu0g6Qj3ZuQrleh48Ehrd83")
            .get()
            .to_dict()
        )
        # try:
        donations: List = user["donations"]
        donations.append(donation)
        fs_db.collection("users").document("7ZdsBiu0g6Qj3ZuQrleh48Ehrd83").set(
            {"donations": donations}, merge=True
        )
        print(str(donations))
        # except:
        #     pass


# donations = []
#
# donations.append(donation)
#

callback_done.set()

doc_ref = fs_db.collection("donations")


# Watch the document
def watch_document():
    doc_watch = doc_ref.on_snapshot(on_snap_shot)
    while True:  # This will keep the script running indefinitely
        try:
            callback_done.wait()
        except Exception as e:
            print(f"An error occurred: {e}")
            continue


# Start the watcher
watch_document()


def get_donation(donation_id: str):
    user = (
        fs_db.collection("users")
        .document("7ZdsBiu0g6Qj3ZuQrleh48Ehrd83")
        .get()
        .to_dict()
    )
