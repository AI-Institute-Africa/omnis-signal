import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import json
import openai
from app.config import settings
from app.db import SessionLocal
from app.models import (
    ResearchItem, ItemEnrichment, Startup, AIModel, Patent, 
    Grant, RegulationPolicy, GPUMarketIndex, ResearchCategory, ContentType
)
from app.services.vector_store import VectorStoreService
from app.services.deduplication import DeduplicationService
import litellm

logger = logging.getLogger(__name__)

class MultiAgentCoordinator:
    """Coordinator that directs the actions of individual agents in the platform."""
    
    def __init__(self):
        self.vector_store = VectorStoreService()
        self.dedup_service = DeduplicationService()
        self.openai_client = openai.OpenAI(api_key=settings.OPENAI_API_KEY) if settings.OPENAI_API_KEY else None

    async def _call_llm(self, prompt: str, max_tokens: int = 500) -> str:
        """Helper to invoke LLM based on configured provider."""
        try:
            if settings.DEFAULT_LLM_PROVIDER == "openai" and self.openai_client:
                response = self.openai_client.chat.completions.create(
                    model=settings.OPENAI_MODEL,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=max_tokens,
                    temperature=0.7,
                )
                return response.choices[0].message.content.strip()
            elif settings.DEFAULT_LLM_PROVIDER == "anthropic" and settings.ANTHROPIC_API_KEY:
                # Use LiteLLM or anthropic client if available
                response = litellm.completion(
                    model=f"anthropic/{settings.ANTHROPIC_MODEL}",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=max_tokens,
                    temperature=0.7
                )
                return response.choices[0].message.content.strip()
            else:
                # Fallback to local heuristic or dummy output
                return ""
        except Exception as e:
            logger.error(f"Agent LLM call failed: {e}")
            return ""


class ResearcherAgent(MultiAgentCoordinator):
    """Agent responsible for raw content crawling, parsing, and ingestion metadata extraction."""
    
    def __init__(self):
        super().__init__()
        
    async def ingest_item(self, db_session, item_data: Dict[str, Any]) -> Optional[ResearchItem]:
        """Ingests crawled raw data, parses it, checks for duplicates, and creates database records."""
        try:
            url_hash = self.dedup_service.calculate_url_hash(item_data['url'])
            
            # Check direct URL duplicate first
            existing = db_session.query(ResearchItem).filter_by(url_hash=url_hash).first()
            if existing:
                logger.debug(f"Direct URL duplicate found for {item_data['url']}")
                return None
                
            # Create tentative ResearchItem
            item = ResearchItem(
                title=item_data['title'],
                url=item_data['url'],
                url_hash=url_hash,
                abstract=item_data.get('abstract', ''),
                authors=item_data.get('authors', []),
                published_date=item_data.get('published_date', datetime.utcnow()),
                categories=item_data.get('categories', []),
                content_type=item_data.get('content_type', ContentType.RESEARCH_PAPER),
                source_id=item_data.get('source_id'),
                source_url=item_data['url'],
                extra_metadata=item_data.get('metadata', {})
            )
            
            # Map primary category
            if item.categories:
                # Map first matching enum or default to LLM
                for cat in item.categories:
                    try:
                        item.primary_category = ResearchCategory(cat.lower())
                        break
                    except ValueError:
                        continue
            if not item.primary_category:
                item.primary_category = ResearchCategory.LLM
                
            db_session.add(item)
            db_session.commit()
            
            # Run semantic deduplication using Qdrant vector database
            # We generate embedding, check similarity, and mark as duplicate if threshold exceeded
            text_to_embed = f"{item.title}. {item.abstract or ''}"
            vector = self.vector_store.generate_embedding(text_to_embed)
            
            # Index vector in Qdrant
            self.vector_store.upsert_item(
                item_id=item.id,
                vector=vector,
                metadata={
                    "title": item.title,
                    "url": item.url,
                    "content_type": item.content_type.value,
                    "published_date": item.published_date.isoformat() if item.published_date else None
                }
            )
            
            # Query similar items
            similar = self.vector_store.search_similar(query_vector=vector, limit=2, threshold=0.88)
            # Exclude current item
            similar = [s for s in similar if s["id"] != item.id]
            
            if similar:
                duplicate_parent_id = similar[0]["id"]
                item.duplicate_of = duplicate_parent_id
                db_session.commit()
                logger.info(f"Item marked as semantic duplicate of {duplicate_parent_id}")
            
            return item
            
        except Exception as e:
            logger.error(f"Error in ResearcherAgent ingestion: {e}")
            db_session.rollback()
            return None


class EnricherAgent(MultiAgentCoordinator):
    """Agent responsible for summaries, classifications, and hedge-fund scoring of research and news."""
    
    def __init__(self):
        super().__init__()
        
    async def enrich(self, db_session, item: ResearchItem) -> Optional[ItemEnrichment]:
        """Calculates executive summaries, technical highlights, and calculates composite scores."""
        try:
            logger.info(f"EnricherAgent analyzing item: {item.title[:60]}")
            
            # 1. Executive and technical summaries
            content_desc = f"Title: {item.title}\nAbstract/Content: {item.abstract or 'N/A'}"
            
            prompt_summary = f"Summarize this AI announcement for a hedge-fund manager. Extract the core innovation, the market impact, and key technical highlights. Format as JSON with keys: 'exec_summary', 'tech_summary', 'business_impact', 'key_insights' (list), 'applications' (list), 'gaps' (list).\n\nContent:\n{content_desc}"
            
            raw_response = await self._call_llm(prompt_summary, max_tokens=600)
            
            # Initialize default values
            exec_summary = f"Summary of {item.title}."
            tech_summary = "Technical details of innovation."
            biz_impact = "Market impact analysis."
            key_insights = ["Key technology release."]
            applications = ["Commercial software", "Research systems"]
            gaps = ["Integration challenges", "Scalability limitations"]
            
            if raw_response:
                try:
                    # Clean potential markdown wrappers
                    cleaned = raw_response.strip().strip("```json").strip("```").strip()
                    data = json.loads(cleaned)
                    exec_summary = data.get("exec_summary", exec_summary)
                    tech_summary = data.get("tech_summary", tech_summary)
                    biz_impact = data.get("business_impact", biz_impact)
                    key_insights = data.get("key_insights", key_insights)
                    applications = data.get("applications", applications)
                    gaps = data.get("gaps", gaps)
                except Exception as ex:
                    logger.warning(f"Failed to parse LLM JSON in EnricherAgent: {ex}. Raw: {raw_response[:100]}")
            
            # 2. Advanced Multi-Factor Scoring
            # Innovation, Market Impact, Technical Novelty, Regulatory Risk, Valuation Potential
            prompt_scores = f"Analyze and score this AI update on these 5 criteria: Innovation (0-100), Market Impact (0-100), Technical Novelty (0-100), Regulatory Risk (0-100, where 0 is high risk/blocked, 100 is perfectly compliant/safe), and Virality Prediction (0-1). Return only valid JSON with keys: 'innovation', 'market_impact', 'novelty', 'regulatory_compliance', 'virality'.\n\nContent:\n{content_desc}"
            
            raw_scores = await self._call_llm(prompt_scores, max_tokens=150)
            
            # Default scores
            innovation = 60.0
            market_impact = 55.0
            novelty = 60.0
            regulatory_compliance = 80.0
            virality = 0.4
            
            if raw_scores:
                try:
                    cleaned_scores = raw_scores.strip().strip("```json").strip("```").strip()
                    s_data = json.loads(cleaned_scores)
                    innovation = float(s_data.get("innovation", innovation))
                    market_impact = float(s_data.get("market_impact", market_impact))
                    novelty = float(s_data.get("novelty", novelty))
                    regulatory_compliance = float(s_data.get("regulatory_compliance", regulatory_compliance))
                    virality = float(s_data.get("virality", virality))
                except Exception as ex:
                    logger.warning(f"Failed to parse score JSON: {ex}")
            
            # Estimate additional metrics
            citation_velocity = 50.0
            social_engagement = virality * 100
            authority = item.source.authority_score if item.source else 0.5
            
            # Calculate importance (standard system score 0-100)
            importance_score = (
                innovation * 0.25 +
                market_impact * 0.20 +
                novelty * 0.20 +
                citation_velocity * 0.15 +
                social_engagement * 0.10 +
                (regulatory_compliance / 2) * 0.10
            ) * (0.7 + authority * 0.3)
            
            # Calculate valuation potential based on market impact
            valuation_potential = market_impact * 1.2
            if item.content_type == ContentType.FUNDING_ROUND or item.content_type == ContentType.STARTUP_ANNOUNCEMENT:
                valuation_potential = min(100.0, valuation_potential + 15.0)
            
            # Calculate hedge-fund intelligence score (0-100)
            # Formula: 30% Importance + 25% Market Impact + 20% Valuation Potential + 15% Regulatory Feasibility + 10% Virality
            intelligence_score = (
                importance_score * 0.30 +
                market_impact * 0.25 +
                valuation_potential * 0.20 +
                regulatory_compliance * 0.15 +
                (virality * 100) * 0.10
            )
            
            importance_score = min(100.0, max(0.0, importance_score))
            intelligence_score = min(100.0, max(0.0, intelligence_score))
            
            enrichment = ItemEnrichment(
                item_id=item.id,
                executive_summary=exec_summary,
                technical_summary=tech_summary,
                business_impact=biz_impact,
                innovation_score=innovation,
                market_impact_score=market_impact,
                research_significance_score=novelty,  # map to significance
                citation_velocity=citation_velocity,
                social_engagement_score=social_engagement,
                technical_novelty_score=novelty,
                importance_score=importance_score,
                intelligence_score=intelligence_score,
                virality_prediction=virality,
                impact_prediction=market_impact / 100.0,
                key_insights=key_insights,
                potential_applications=applications,
                research_gaps=gaps,
                model_used=settings.DEFAULT_LLM_PROVIDER,
                generation_timestamp=datetime.utcnow()
            )
            
            db_session.add(enrichment)
            db_session.commit()
            
            logger.info(f"Enrichment complete. Intelligence Score: {intelligence_score:.1f}")
            return enrichment
            
        except Exception as e:
            logger.error(f"EnricherAgent enrichment failed: {e}")
            db_session.rollback()
            return None


class ValuationAgent(MultiAgentCoordinator):
    """Agent responsible for startup tracking, funding predictions, and GPU market updates."""
    
    def __init__(self):
        super().__init__()
        
    async def track_startup(self, db_session, name: str, round_amount: float, stage: str, focus_areas: List[str], details: str) -> Startup:
        """Discovers or updates an AI startup record, predicting current and future valuations."""
        try:
            startup = db_session.query(Startup).filter_by(name=name).first()
            
            # Predict valuation multiplier based on stage
            multipliers = {
                "seed": 8.0,
                "pre-seed": 5.0,
                "series_a": 6.0,
                "series_b": 5.0,
                "series_c": 4.5,
                "growth": 4.0
            }
            mult = multipliers.get(stage.lower(), 5.0)
            predicted_val = round_amount * mult
            
            if not startup:
                startup = Startup(
                    name=name,
                    description=details,
                    total_funding=round_amount,
                    latest_funding_round=round_amount,
                    latest_funding_date=datetime.utcnow(),
                    funding_stage=stage,
                    focus_areas=focus_areas,
                    current_valuation=predicted_val,
                    predicted_valuation=predicted_val * 1.3, # 30% growth prediction
                    valuation_confidence=0.75,
                    reputation_score=70.0
                )
                db_session.add(startup)
            else:
                startup.total_funding += round_amount
                startup.latest_funding_round = round_amount
                startup.latest_funding_date = datetime.utcnow()
                startup.funding_stage = stage
                startup.current_valuation = predicted_val
                startup.predicted_valuation = predicted_val * 1.25
                startup.focus_areas = list(set((startup.focus_areas or []) + focus_areas))
                
            db_session.commit()
            logger.info(f"ValuationAgent updated startup: {name}. Predicted Valuation: ${predicted_val/1e6:.1f}M")
            return startup
        except Exception as e:
            logger.error(f"ValuationAgent failed to track startup {name}: {e}")
            db_session.rollback()
            return None

    def update_gpu_market_index(self, db_session, gpu_model: str, provider: str, price_per_hour: float, status: str) -> GPUMarketIndex:
        """Records a pricing data point for AI training hardware."""
        try:
            # Estimate demand index based on price changes or provider status
            base_prices = {"H100": 2.50, "A100": 1.20, "H200": 3.80, "V100": 0.60}
            base = base_prices.get(gpu_model.upper(), 1.0)
            demand = price_per_hour / base if base > 0 else 1.0
            
            index = GPUMarketIndex(
                gpu_model=gpu_model,
                provider=provider,
                price_per_hour=price_per_hour,
                availability_status=status,
                demand_index=min(3.0, max(0.5, demand)),
                recorded_at=datetime.utcnow()
            )
            db_session.add(index)
            db_session.commit()
            return index
        except Exception as e:
            logger.error(f"ValuationAgent failed to update GPU market index: {e}")
            db_session.rollback()
            return None


class RAGAnalystAgent(MultiAgentCoordinator):
    """User-facing QA assistant providing real-time synthesis, strategic forecasts, and regulatory reports."""
    
    def __init__(self):
        super().__init__()
        
    async def answer_question(self, question: str) -> Dict[str, Any]:
        """Performs semantic search retrieval, queries SQLite metadata, and returns synthetic analysis."""
        db = SessionLocal()
        try:
            logger.info(f"RAGAnalystAgent processing query: {question}")
            
            # Generate query embedding
            q_vector = self.vector_store.generate_embedding(question)
            
            # Search similar documents (threshold 0.70 to get relevant context)
            matches = self.vector_store.search_similar(query_vector=q_vector, limit=8, threshold=0.70)
            
            context_items = []
            citations = []
            
            for m in matches:
                # Fetch full metadata from PostgreSQL
                item = db.query(ResearchItem).filter_by(id=m["id"]).first()
                if item:
                    enrichment_info = ""
                    if item.enrichment:
                        enrichment_info = f"Summary: {item.enrichment.executive_summary}\nBusiness Impact: {item.enrichment.business_impact}\nScores: Intelligence={item.enrichment.intelligence_score}, Importance={item.enrichment.importance_score}"
                        
                    context_items.append(
                        f"Title: {item.title}\nSource: {item.source.name if item.source else 'Unknown'}\nUrl: {item.url}\nPublished: {item.published_date}\nAbstract: {item.abstract or 'N/A'}\n{enrichment_info}\n"
                    )
                    citations.append({
                        "id": item.id,
                        "title": item.title,
                        "url": item.url,
                        "source": item.source.name if item.source else "Unknown",
                        "published_date": item.published_date.strftime("%Y-%m-%d") if item.published_date else None
                    })
            
            # Check relational statistics for structured data (e.g. GPU prices, startups, regulations)
            startups_info = ""
            recent_startups = db.query(Startup).order_by(Startup.latest_funding_date.desc()).limit(5).all()
            if recent_startups:
                startups_info = "Recent Funded Startups:\n" + "\n".join(
                    [f"- {s.name}: ${s.total_funding/1e6:.1f}M raised, stage: {s.funding_stage}, focus: {s.focus_areas}" for s in recent_startups]
                )
                
            gpu_info = ""
            recent_gpu = db.query(GPUMarketIndex).order_by(GPUMarketIndex.recorded_at.desc()).limit(5).all()
            if recent_gpu:
                gpu_info = "Recent GPU Pricing Index:\n" + "\n".join(
                    [f"- {g.gpu_model} at {g.provider}: ${g.price_per_hour}/hr, demand mult: {g.demand_index:.2f}" for g in recent_gpu]
                )
                
            policies_info = ""
            recent_policies = db.query(RegulationPolicy).order_by(RegulationPolicy.announcement_date.desc()).limit(5).all()
            if recent_policies:
                policies_info = "Emerging Regulatory Policies:\n" + "\n".join(
                    [f"- {p.title} ({p.governing_body}): Jurisdiction {p.jurisdiction}, status: {p.status}, impact: {p.impact_level}" for p in recent_policies]
                )
            
            # Build synthesis prompt
            context_str = "\n---\n".join(context_items)
            prompt = f"""You are a senior hedge-fund research analyst specializing in Artificial Intelligence. Use the following context documents and platform metrics to answer the research question. Be highly analytical, strategic, quantitative, and professional. 

Context Documents:
{context_str}

Structured Platform Analytics:
{startups_info}
{gpu_info}
{policies_info}

Question:
{question}

Provide a detailed summary. If the context does not contain sufficient details to answer, use your pre-trained knowledge of the AI market to augment the answer, but clearly distinguish between platform retrieved data and general market knowledge. Include strategic recommendations or future outlook where relevant."""

            synthesis = await self._call_llm(prompt, max_tokens=800)
            if not synthesis:
                synthesis = "Unable to reach the analytical model at this time. Here are the matching search items:\n" + "\n".join([f"- {c['title']} ({c['url']})" for c in citations])
                
            return {
                "question": question,
                "answer": synthesis,
                "citations": citations,
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"RAGAnalystAgent failed to answer question: {e}")
            return {
                "question": question,
                "answer": f"Error during analytical query execution: {e}",
                "citations": [],
                "timestamp": datetime.utcnow().isoformat()
            }
        finally:
            db.close()
