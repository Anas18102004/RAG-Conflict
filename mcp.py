from models import Event, User, Constraint
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import List, Dict

def detect_conflicts(session: Session) -> List[Dict]:
    events = session.query(Event).all()
    conflicts = []
    for i, e1 in enumerate(events):
        for e2 in events[i+1:]:
            if set([u.id for u in e1.participants]) & set([u.id for u in e2.participants]):
                if (e1.start < e2.end and e2.start < e1.end):
                    conflicts.append({
                        "events": [e1.title, e2.title],
                        "participants": list(set([u.name for u in e1.participants]) & set([u.name for u in e2.participants])),
                        "explanation": f"Overlap between {e1.title} and {e2.title} for participants {set([u.name for u in e1.participants]) & set([u.name for u in e2.participants])}"
                    })
    return conflicts

def mcp_resolve(session: Session, participants: List[str], desired_start: datetime, desired_end: datetime) -> Dict:
    # Get users and their constraints
    users = session.query(User).filter(User.name.in_(participants)).all()
    constraints = {u.name: session.query(Constraint).filter(Constraint.user_id == u.id).first() for u in users}
    # Check for hard conflicts
    events = session.query(Event).all()
    hard_conflicts = []
    for event in events:
        if set([u.name for u in event.participants]) & set(participants):
            if (event.start < desired_end and desired_start < event.end):
                hard_conflicts.append(event)
    preferred = []
    fallback = []
    if not hard_conflicts:
        preferred.append({"start": desired_start.isoformat(), "end": desired_end.isoformat(), "participants": participants})
    else:
        # Propose fallback: find next available slot for all participants
        for offset in range(1, 8):
            alt_start = desired_start + timedelta(days=offset)
            alt_end = desired_end + timedelta(days=offset)
            conflict = False
            for event in events:
                if set([u.name for u in event.participants]) & set(participants):
                    if (event.start < alt_end and alt_start < event.end):
                        conflict = True
                        break
            if not conflict:
                fallback.append({"start": alt_start.isoformat(), "end": alt_end.isoformat(), "participants": participants})
                break
    return {"preferred": preferred, "fallback": fallback, "hard_conflicts": [e.title for e in hard_conflicts]} 