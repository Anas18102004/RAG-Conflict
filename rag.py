from faiss_index import faiss_manager
from models import Event, Constraint
from sqlalchemy.orm import Session

def retrieve_context(session: Session, query: str, top_k=5):
    results = faiss_manager.query(query, top_k=top_k)
    context = []
    for doc_type, doc_id in results:
        if doc_type == 'event':
            event = session.query(Event).filter(Event.id == doc_id).first()
            if event:
                context.append(f"Event: {event.title}, {event.start} to {event.end}, Priority: {event.priority}, Participants: {[u.name for u in event.participants]}")
        elif doc_type == 'constraint':
            constraint = session.query(Constraint).filter(Constraint.id == doc_id).first()
            if constraint:
                context.append(f"Constraint: Preferred {constraint.preferred_times}, Unavailable {constraint.unavailable_slots}, Capacity: {constraint.capacity}")
    return '\n'.join(context) 