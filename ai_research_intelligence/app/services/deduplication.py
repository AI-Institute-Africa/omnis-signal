import logging
import hashlib
from typing import Optional, List
from difflib import SequenceMatcher
from app.models import ResearchItem
from app.services.vector_store import VectorStoreService

logger = logging.getLogger(__name__)

class DeduplicationService:
    """Service for detecting and handling duplicate items using URL, title, and vector similarity."""
    
    def __init__(self):
        self.vector_store = VectorStoreService()
        
    def calculate_url_hash(self, url: str) -> str:
        """Calculate hash of URL for uniqueness."""
        return hashlib.sha256(url.encode()).hexdigest()
    
    def calculate_content_hash(self, title: str, abstract: str) -> str:
        """Calculate hash of content."""
        content = f"{title}||{abstract or ''}".lower().strip()
        return hashlib.sha256(content.encode()).hexdigest()
    
    def is_duplicate(self, new_item: ResearchItem, existing_items: List[ResearchItem]) -> Optional[ResearchItem]:
        """Check if item is a duplicate of any existing item using standard heuristics."""
        for existing in existing_items:
            # URL similarity (most reliable)
            if self._url_similarity(new_item.url, existing.url) > 0.95:
                logger.info(f"Duplicate detected via URL: {new_item.url}")
                return existing
            
            # Title + Abstract similarity
            if self._content_similarity(new_item.title, new_item.abstract, existing.title, existing.abstract) > 0.90:
                logger.info(f"Duplicate detected via content: {new_item.title}")
                return existing
        
        return None
    
    def _url_similarity(self, url1: str, url2: str) -> float:
        """Calculate URL similarity (0-1)."""
        u1 = url1.lower().strip('/').split('?')[0]
        u2 = url2.lower().strip('/').split('?')[0]
        
        if u1 == u2:
            return 1.0
        
        return SequenceMatcher(None, u1, u2).ratio()
    
    def _content_similarity(self, title1: str, abstract1: str, title2: str, abstract2: str) -> float:
        """Calculate content similarity (0-1)."""
        title_sim = SequenceMatcher(None, title1.lower(), title2.lower()).ratio()
        
        abstract_sim = 0.0
        if abstract1 and abstract2:
            abstract_sim = SequenceMatcher(
                None,
                abstract1.lower()[:200],
                abstract2.lower()[:200]
            ).ratio()
        
        return title_sim * 0.7 + abstract_sim * 0.3
    
    async def detect_and_mark_duplicates(self, item: ResearchItem, db_session) -> bool:
        """Detect duplicates using database query and Qdrant semantic vector similarity."""
        try:
            # 1. Direct database check (heuristic URL and title matching)
            similar_db = db_session.query(ResearchItem).filter(
                ResearchItem.id != item.id,
                ResearchItem.duplicate_of.is_(None)
            ).order_by(ResearchItem.created_at.desc()).limit(50).all()
            
            duplicate_parent = self.is_duplicate(item, similar_db)
            if duplicate_parent:
                item.duplicate_of = duplicate_parent.id
                db_session.commit()
                logger.info(f"Item {item.id} marked as duplicate of {duplicate_parent.id} via heuristics")
                return True
                
            # 2. Qdrant vector semantic search check
            text_to_embed = f"{item.title}. {item.abstract or ''}"
            vector = self.vector_store.generate_embedding(text_to_embed)
            
            # Search Qdrant for semantic similarity (>0.88 cosine similarity)
            matches = self.vector_store.search_similar(query_vector=vector, limit=2, threshold=0.88)
            # Exclude self
            matches = [m for m in matches if m["id"] != item.id]
            
            if matches:
                parent_id = matches[0]["id"]
                # Verify parent still exists in Postgres
                parent_exists = db_session.query(ResearchItem).filter_by(id=parent_id).first()
                if parent_exists:
                    item.duplicate_of = parent_id
                    db_session.commit()
                    logger.info(f"Item {item.id} marked as duplicate of {parent_id} via Qdrant semantic check")
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error in DeduplicationService: {e}")
            return False
    
    def get_deduplication_status(self, db_session) -> dict:
        """Get deduplication statistics."""
        total = db_session.query(ResearchItem).count()
        duplicates = db_session.query(ResearchItem).filter(
            ResearchItem.duplicate_of.isnot(None)
        ).count()
        
        return {
            "total_items": total,
            "duplicate_items": duplicates,
            "unique_items": total - duplicates,
            "duplicate_percentage": (duplicates / total * 100) if total > 0 else 0
        }
