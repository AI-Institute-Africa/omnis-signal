import logging
import json
from typing import Optional, List, Dict, Any
from datetime import datetime
import hashlib
from app.config import settings
from app.models import ItemEnrichment, ResearchItem, ResearchCategory
import openai
import anthropic
import litellm

logger = logging.getLogger(__name__)


class AIEnrichmentService:
    """Service for AI-powered content enrichment and scoring."""
    
    def __init__(self):
        self.openai_client = openai.OpenAI(api_key=settings.OPENAI_API_KEY) if settings.OPENAI_API_KEY else None
        self.anthropic_client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY) if settings.ANTHROPIC_API_KEY else None
    
    async def enrich_item(self, item: ResearchItem, db_session) -> Optional[ItemEnrichment]:
        """Enrich a research item with AI-generated content and scores."""
        try:
            logger.info(f"Enriching item: {item.title[:50]}...")
            
            # Generate summaries
            executive_summary = await self._generate_executive_summary(item)
            technical_summary = await self._generate_technical_summary(item)
            business_impact = await self._generate_business_impact(item)
            
            # Generate insights
            key_insights = await self._extract_key_insights(item, executive_summary)
            applications = await self._predict_applications(item, executive_summary)
            research_gaps = await self._identify_research_gaps(item)
            
            # Calculate scores
            innovation_score = await self._calculate_innovation_score(item, technical_summary)
            market_impact_score = await self._calculate_market_impact(item, business_impact)
            research_significance = await self._calculate_research_significance(item)
            citation_velocity = await self._estimate_citation_velocity(item)
            social_engagement = await self._estimate_social_engagement(item)
            technical_novelty = await self._score_technical_novelty(item)
            virality_pred = await self._predict_virality(item)
            impact_pred = await self._predict_impact(item)
            
            # Calculate composite importance score
            importance_score = self._calculate_importance_score(
                innovation_score,
                market_impact_score,
                research_significance,
                citation_velocity,
                social_engagement,
                technical_novelty,
                item.source.authority_score if item.source else 0.5
            )
            
            # Calculate hedge-fund intelligence score
            intelligence_score = self._calculate_intelligence_score(
                importance_score,
                virality_pred,
                impact_pred,
                market_impact_score,
                research_significance
            )
            
            # Create enrichment record
            enrichment = ItemEnrichment(
                item_id=item.id,
                executive_summary=executive_summary,
                technical_summary=technical_summary,
                business_impact=business_impact,
                innovation_score=innovation_score,
                market_impact_score=market_impact_score,
                research_significance_score=research_significance,
                citation_velocity=citation_velocity,
                social_engagement_score=social_engagement,
                technical_novelty_score=technical_novelty,
                importance_score=importance_score,
                intelligence_score=intelligence_score,
                virality_prediction=virality_pred,
                impact_prediction=impact_pred,
                key_insights=key_insights,
                potential_applications=applications,
                research_gaps=research_gaps,
                model_used=settings.DEFAULT_LLM_PROVIDER,
                generation_timestamp=datetime.utcnow()
            )
            
            db_session.add(enrichment)
            db_session.commit()
            
            logger.info(f"Item enriched successfully. Importance Score: {importance_score:.2f}, Intelligence Score: {intelligence_score:.2f}")
            return enrichment
            
        except Exception as e:
            logger.error(f"Error enriching item: {e}")
            db_session.rollback()
            return None
    
    async def _generate_executive_summary(self, item: ResearchItem) -> str:
        """Generate executive summary."""
        prompt = f"""Generate a concise executive summary (2-3 sentences) for this AI research item:

Title: {item.title}
Abstract: {item.abstract or 'N/A'}
Categories: {', '.join(item.categories or [])}

Summary should be understandable to non-technical business professionals."""
        
        return await self._call_llm(prompt, max_tokens=200)
    
    async def _generate_technical_summary(self, item: ResearchItem) -> str:
        """Generate technical summary."""
        prompt = f"""Generate a technical summary (3-4 sentences) for this AI research:

Title: {item.title}
Abstract: {item.abstract or 'N/A'}

Highlight the technical approach, methods, and key innovations."""
        
        return await self._call_llm(prompt, max_tokens=300)
    
    async def _generate_business_impact(self, item: ResearchItem) -> str:
        """Generate business impact analysis."""
        prompt = f"""Analyze the potential business impact of this AI research:

Title: {item.title}
Abstract: {item.abstract or 'N/A'}
Categories: {', '.join(item.categories or [])}

Consider: market opportunities, competitive advantages, commercialization potential."""
        
        return await self._call_llm(prompt, max_tokens=250)
    
    async def _extract_key_insights(self, item: ResearchItem, summary: str) -> List[str]:
        """Extract key insights."""
        prompt = f"""Extract 3-5 key insights from this research summary:

{summary}

Return as a JSON array of strings."""
        
        response = await self._call_llm(prompt, max_tokens=200)
        try:
            return json.loads(response)
        except:
            return [summary[:100]]
    
    async def _predict_applications(self, item: ResearchItem, summary: str) -> List[str]:
        """Predict practical applications."""
        prompt = f"""List 3-5 potential real-world applications of this research:

{summary}

Return as a JSON array of application descriptions."""
        
        response = await self._call_llm(prompt, max_tokens=250)
        try:
            return json.loads(response)
        except:
            return ["Enterprise AI", "Research Applications"]
    
    async def _identify_research_gaps(self, item: ResearchItem) -> List[str]:
        """Identify remaining research gaps."""
        prompt = f"""What are the key research gaps or future work suggested by:

Title: {item.title}
Abstract: {item.abstract or 'N/A'}

Return as a JSON array."""
        
        response = await self._call_llm(prompt, max_tokens=200)
        try:
            return json.loads(response)
        except:
            return ["Further optimization", "Scalability research"]
    
    async def _calculate_innovation_score(self, item: ResearchItem, summary: str) -> float:
        """Calculate innovation score (0-100)."""
        prompt = f"""Rate the innovation/novelty of this research on a scale of 0-100:

{summary}

Consider: new methods, breaking assumptions, groundbreaking approaches.
Return ONLY the number."""
        
        try:
            score = float(await self._call_llm(prompt, max_tokens=10))
            return max(0, min(100, score))
        except:
            return 50.0
    
    async def _calculate_market_impact(self, item: ResearchItem, business_impact: str) -> float:
        """Calculate market impact score (0-100)."""
        prompt = f"""Rate the market impact potential of this research 0-100:

{business_impact}

Consider: market size, competitive advantage, revenue potential.
Return ONLY the number."""
        
        try:
            score = float(await self._call_llm(prompt, max_tokens=10))
            return max(0, min(100, score))
        except:
            return 50.0
    
    async def _calculate_research_significance(self, item: ResearchItem) -> float:
        """Calculate research significance (0-100)."""
        # Higher significance for papers from prestigious sources
        base_score = 50.0
        if item.source and item.source.authority_score > 0.8:
            base_score += 25
        if item.abstract and len(item.abstract) > 500:
            base_score += 10
        return min(100, base_score)
    
    async def _estimate_citation_velocity(self, item: ResearchItem) -> float:
        """Estimate citation velocity (0-100)."""
        # Prediction based on publication date and source
        days_old = (datetime.utcnow() - (item.published_date or item.discovered_date)).days
        if days_old < 7:
            return 75.0
        elif days_old < 30:
            return 50.0
        else:
            return 30.0
    
    async def _estimate_social_engagement(self, item: ResearchItem) -> float:
        """Estimate social engagement (0-100)."""
        # Base score, could integrate real metrics
        return 60.0
    
    async def _score_technical_novelty(self, item: ResearchItem) -> float:
        """Score technical novelty."""
        prompt = f"""Rate the technical novelty (0-100) of this research:

Title: {item.title}
Abstract: {item.abstract or 'N/A'}

Return ONLY the number."""
        
        try:
            score = float(await self._call_llm(prompt, max_tokens=10))
            return max(0, min(100, score))
        except:
            return 50.0
    
    async def _predict_virality(self, item: ResearchItem) -> float:
        """Predict virality score (0-1)."""
        # Factors: timing, novelty, simplicity of explanation
        prompt = f"""Predict virality (0-1) for this AI research in tech community:

Title: {item.title}
Return ONLY a decimal number."""
        
        try:
            score = float(await self._call_llm(prompt, max_tokens=10))
            return max(0, min(1, score))
        except:
            return 0.5
    
    async def _predict_impact(self, item: ResearchItem) -> float:
        """Predict long-term impact (0-1)."""
        prompt = f"""Predict long-term impact (0-1) of this AI research:

Title: {item.title}
Return ONLY a decimal number."""
        
        try:
            score = float(await self._call_llm(prompt, max_tokens=10))
            return max(0, min(1, score))
        except:
            return 0.5
    
    def _calculate_importance_score(
        self,
        innovation: float,
        market_impact: float,
        significance: float,
        citation_velocity: float,
        engagement: float,
        novelty: float,
        authority: float,
    ) -> float:
        """Calculate weighted importance score (0-100)."""
        weights = {
            'innovation': 0.25,
            'market_impact': 0.20,
            'significance': 0.20,
            'citation_velocity': 0.15,
            'engagement': 0.10,
            'novelty': 0.10,
        }
        
        score = (
            innovation * weights['innovation'] +
            market_impact * weights['market_impact'] +
            significance * weights['significance'] +
            citation_velocity * weights['citation_velocity'] +
            engagement * weights['engagement'] +
            novelty * weights['novelty']
        )
        
        # Authority boost
        score = score * (0.7 + authority * 0.3)
        return min(100, max(0, score))
    
    def _calculate_intelligence_score(
        self,
        importance: float,
        virality: float,
        impact: float,
        market_impact: float,
        significance: float,
    ) -> float:
        """Calculate hedge-fund intelligence score (0-100)."""
        # For institutional investors: emphasis on lasting impact, market value
        score = (
            importance * 0.30 +
            impact * 100 * 0.30 +  # Convert 0-1 to 0-100
            market_impact * 0.25 +
            virality * 100 * 0.10 +
            significance * 0.05
        )
        return min(100, max(0, score))
    
    async def _call_llm(self, prompt: str, max_tokens: int = 500) -> str:
        """Call LLM based on configuration."""
        try:
            if settings.DEFAULT_LLM_PROVIDER == "openai" and self.openai_client:
                response = self.openai_client.chat.completions.create(
                    model=settings.OPENAI_MODEL,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=max_tokens,
                    temperature=0.7,
                )
                return response.choices[0].message.content.strip()
            
            elif settings.DEFAULT_LLM_PROVIDER == "anthropic" and self.anthropic_client:
                response = self.anthropic_client.messages.create(
                    model=settings.ANTHROPIC_MODEL,
                    max_tokens=max_tokens,
                    messages=[{"role": "user", "content": prompt}],
                )
                return response.content[0].text.strip()
            
            else:
                # Fallback - return placeholder
                logger.warning("No LLM provider configured, returning placeholder")
                return "Unable to generate at this time"
                
        except Exception as e:
            logger.error(f"LLM call failed: {e}")
            return "Error generating content"
