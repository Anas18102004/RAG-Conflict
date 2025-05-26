import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from models import User, Event, Constraint
from sqlalchemy.orm import Session

MODEL_NAME = 'all-MiniLM-L6-v2'

class FaissIndexManager:
    def __init__(self, dim=384):
        self.model = SentenceTransformer(MODEL_NAME)
        self.index = faiss.IndexFlatL2(dim)
        self.id_map = []  # Maps FAISS index to (type, id)

    def build_index(self, session: Session):
        self.index.reset()
        self.id_map = []
        # Embed events
        events = session.query(Event).all()
        for event in events:
            text = f"Event: {event.title}, {event.start} to {event.end}, Priority: {event.priority}"
            emb = self.model.encode([text])
            self.index.add(np.array(emb, dtype=np.float32))
            self.id_map.append(('event', event.id))
        # Embed constraints
        constraints = session.query(Constraint).all()
        for constraint in constraints:
            text = f"Constraint: Preferred {constraint.preferred_times}, Unavailable {constraint.unavailable_slots}, Capacity: {constraint.capacity}"
            emb = self.model.encode([text])
            self.index.add(np.array(emb, dtype=np.float32))
            self.id_map.append(('constraint', constraint.id))

    def add_document(self, text, doc_type, doc_id):
        emb = self.model.encode([text])
        self.index.add(np.array(emb, dtype=np.float32))
        self.id_map.append((doc_type, doc_id))

    def query(self, query_text, top_k=5):
        emb = self.model.encode([query_text])
        D, I = self.index.search(np.array(emb, dtype=np.float32), top_k)
        results = []
        for idx in I[0]:
            if idx < len(self.id_map):
                results.append(self.id_map[idx])
        return results

faiss_manager = FaissIndexManager() 