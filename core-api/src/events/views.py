from flask import Blueprint, jsonify

events_blueprint = Blueprint("events", __name__, url_prefix="/events/")

MOCK_EVENTS = [
    {
        "image": ".bike1",
        "description": "View Event Details", 
        "elo": 100.0
    },
    {
        "image": ".bike2",
        "description": "View Event Details", 
        "elo": 200.0
    },
    {
        "image": ".bike3",
        "description": "View Event Details", 
        "elo": 500.0
    },
    {
        "image": ".bike4",
        "description": "View Event Details", 
        "elo": 600.0
    },
    {
        "image": ".bike5",
        "description": "View Event Details", 
        "elo": 800.0
    }
]

@events_blueprint.route('', methods=['GET'])
def get_events():
    return jsonify(MOCK_EVENTS), 200