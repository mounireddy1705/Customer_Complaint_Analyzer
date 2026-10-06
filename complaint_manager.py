import json
import os
from datetime import datetime
from uuid import uuid4


DATA_FILE = os.path.join("data", "complaints.json")


def load_complaints():
    """Load all complaints from the JSON file."""

    if not os.path.exists(DATA_FILE):
        return []

    try:
        with open(DATA_FILE, "r", encoding="utf-8") as file:
            return json.load(file)

    except (json.JSONDecodeError, OSError):
        return []


def save_complaints(complaints):
    """Save all complaints to the JSON file."""

    os.makedirs("data", exist_ok=True)

    with open(DATA_FILE, "w", encoding="utf-8") as file:
        json.dump(complaints, file, indent=4)


def create_complaint(customer_name, subject, complaint_text, department):
    """Create and save a new complaint."""

    now = datetime.now()

    complaint = {
        "id": str(uuid4())[:8].upper(),
        "customer_name": customer_name,
        "subject": subject,
        "complaint": complaint_text,
        "department": department,
        "created_at": now.strftime("%Y-%m-%d %H:%M:%S"),
        "status": "New",
        "analysis": {},
        "thread": [
            {
                "sender": "Customer",
                "message": complaint_text,
                "timestamp": now.strftime("%Y-%m-%d %H:%M:%S")
            }
        ]
    }

    complaints = load_complaints()
    complaints.append(complaint)
    save_complaints(complaints)

    return complaint


def get_complaint(complaint_id):
    """Find one complaint by its ID."""

    complaints = load_complaints()

    for complaint in complaints:
        if complaint["id"] == complaint_id:
            return complaint

    return None


def update_complaint(complaint_id, updates):
    """Update a complaint."""

    complaints = load_complaints()

    for complaint in complaints:
        if complaint["id"] == complaint_id:
            complaint.update(updates)
            save_complaints(complaints)
            return complaint

    return None


def add_thread_message(complaint_id, sender, message):
    """Add a message to a complaint thread."""

    complaints = load_complaints()

    for complaint in complaints:
        if complaint["id"] == complaint_id:

            complaint["thread"].append(
                {
                    "sender": sender,
                    "message": message,
                    "timestamp": datetime.now().strftime(
                        "%Y-%m-%d %H:%M:%S"
                    )
                }
            )

            save_complaints(complaints)
            return complaint

    return None