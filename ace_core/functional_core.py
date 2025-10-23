"""
ACE Functional Core - Pure Functions
All business logic without side effects
"""
from typing import List, Dict, Tuple, Optional
from datetime import datetime, timedelta
import re
import uuid
from ace_types import Success, Failure, Result, ContextBullet, Trajectory, Insight, DeltaUpdate, ContextState, ReasoningStep

# Pure functions for context operations
def create_bullet(content: str, tags: List[str] = None) -> ContextBullet:
    """Create new context bullet"""
    return ContextBullet(
        id=str(uuid.uuid4()),
        content=content,
        tags=tuple(tags or [])
    )

def update_bullet_feedback(bullet: ContextBullet, helpful: bool) -> ContextBullet:
    """Update bullet feedback (returns new bullet)"""
    return ContextBullet(
        id=bullet.id,
        content=bullet.content,
        helpful_count=bullet.helpful_count + (1 if helpful else 0),
        harmful_count=bullet.harmful_count + (0 if helpful else 1),
        created_at=bullet.created_at,
        tags=bullet.tags
    )

def score_bullet(bullet: ContextBullet, query_words: set) -> float:
    """Score bullet relevance to query"""
    bullet_words = set(bullet.content.lower().split())
    overlap = len(query_words.intersection(bullet_words))
    feedback_score = (bullet.helpful_count - bullet.harmful_count) * 0.1
    return overlap + feedback_score

def get_relevant_bullets(
    context: ContextState,
    query: str,
    max_bullets: int = 10
) -> List[ContextBullet]:
    """Get most relevant bullets for query"""
    if not context.bullets:
        return []
    
    query_words = set(query.lower().split())
    scored = [(score_bullet(b, query_words), b) for b in context.bullets.values()]
    scored.sort(key=lambda x: x[0], reverse=True)
    return [b for score, b in scored[:max_bullets] if score > 0]

def find_duplicate_bullet(
    new_bullet: ContextBullet,
    existing: Dict[str, ContextBullet],
    threshold: float = 0.7
) -> Optional[str]:
    """Find duplicate bullet by content similarity"""
    new_words = set(new_bullet.content.lower().split())
    
    for bullet_id, existing_bullet in existing.items():
        existing_words = set(existing_bullet.content.lower().split())
        if not new_words or not existing_words:
            continue
        overlap = len(new_words.intersection(existing_words))
        similarity = overlap / len(new_words)
        if similarity >= threshold:
            return bullet_id
    return None

def merge_delta(
    context: ContextState,
    delta: DeltaUpdate
) -> ContextState:
    """Merge delta update into context (pure function)"""
    new_bullets = dict(context.bullets)
    
    for bullet in delta.bullets:
        duplicate_id = find_duplicate_bullet(bullet, new_bullets)
        if duplicate_id:
            existing = new_bullets[duplicate_id]
            new_bullets[duplicate_id] = update_bullet_feedback(existing, True)
        else:
            new_bullets[bullet.id] = bullet
    
    return ContextState(bullets=new_bullets, version=context.version + 1)

def prune_low_quality_bullets(
    context: ContextState,
    min_days_old: int = 30
) -> ContextState:
    """Remove low-quality bullets"""
    now = datetime.now()
    filtered = {}
    
    for bullet_id, bullet in context.bullets.items():
        # Keep if more helpful than harmful
        if bullet.helpful_count > bullet.harmful_count:
            filtered[bullet_id] = bullet
        # Keep if neutral but recent
        elif bullet.helpful_count == bullet.harmful_count == 0:
            days_old = (now - bullet.created_at).days
            if days_old <= min_days_old:
                filtered[bullet_id] = bullet
    
    return ContextState(bullets=filtered, version=context.version + 1)

def limit_context_size(
    context: ContextState,
    max_size: int = 1000
) -> ContextState:
    """Limit context to top N bullets"""
    if len(context.bullets) <= max_size:
        return context
    
    now = datetime.now()
    scored = []
    for bullet_id, bullet in context.bullets.items():
        score = bullet.helpful_count - bullet.harmful_count
        days_old = (now - bullet.created_at).days
        recency_bonus = max(0, 7 - days_old) * 0.1
        scored.append((score + recency_bonus, bullet_id, bullet))
    
    scored.sort(key=lambda x: x[0], reverse=True)
    top_bullets = {bullet_id: bullet for _, bullet_id, bullet in scored[:max_size]}
    
    return ContextState(bullets=top_bullets, version=context.version + 1)

def parse_trajectory_response(query: str, response: str) -> Trajectory:
    """Parse LLM response into trajectory"""
    # Extract steps
    steps_match = re.search(r'STEPS:\s*\[(.*?)\]', response, re.DOTALL | re.IGNORECASE)
    if steps_match:
        steps_text = steps_match.group(1)
        steps = tuple(ReasoningStep(s.strip()) for s in steps_text.split(';') if s.strip())
    else:
        # Fallback: use first 3 lines as steps
        lines = [l.strip() for l in response.split('\n') if l.strip()][:3]
        steps = tuple(ReasoningStep(l) for l in lines) if lines else (ReasoningStep("Processed query"),)
    
    # Extract outcome
    outcome_match = re.search(r'OUTCOME:\s*(.+?)(?=\n|$)', response, re.DOTALL | re.IGNORECASE)
    outcome = outcome_match.group(1).strip() if outcome_match else response[:200]
    
    # Extract success
    success_match = re.search(r'SUCCESS:\s*(true|false)', response, re.IGNORECASE)
    success = success_match.group(1).lower() == 'true' if success_match else True
    
    # Extract used bullets
    bullets_match = re.search(r'USED_BULLETS:\s*\[(.*?)\]', response, re.IGNORECASE)
    used_bullets = tuple(b.strip() for b in bullets_match.group(1).split(',') if b.strip()) if bullets_match else ()
    
    return Trajectory(
        query=query,
        steps=steps,
        outcome=outcome,
        success=success,
        used_bullets=used_bullets
    )

def parse_insights_response(response: str, source_id: str) -> List[Insight]:
    """Parse LLM response into insights"""
    # Extract insight blocks
    blocks = re.findall(
        r'\[Content:\s*(.+?);\s*Type:\s*(.+?);\s*Confidence:\s*([0-9.]+)\]',
        response,
        re.DOTALL | re.IGNORECASE
    )
    
    insights = []
    for content, insight_type, confidence in blocks:
        try:
            conf_val = float(confidence)
            if 0.0 <= conf_val <= 1.0:
                insights.append(Insight(
                    content=content.strip(),
                    insight_type=insight_type.strip(),
                    confidence=conf_val,
                    source_id=source_id
                ))
        except ValueError:
            continue
    
    # Fallback: extract first meaningful sentence as insight
    if not insights:
        sentences = [s.strip() for s in response.split('.') if len(s.strip()) > 20]
        if sentences:
            insights.append(Insight(
                content=sentences[0],
                insight_type="strategy",
                confidence=0.6,
                source_id=source_id
            ))
    
    return insights if insights else [
        Insight(
            content="Task completed successfully",
            insight_type="strategy",
            confidence=0.5,
            source_id=source_id
        )
    ]

def insights_to_delta(insights: List[Insight], min_confidence: float = 0.5) -> DeltaUpdate:
    """Convert insights to delta update"""
    bullets = []
    for insight in insights:
        if insight.confidence >= min_confidence:
            bullet = create_bullet(insight.content, [insight.insight_type])
            bullets.append(bullet)
    
    return DeltaUpdate(bullets=tuple(bullets))

def build_context_prompt(bullets: List[ContextBullet]) -> str:
    """Build context text from bullets"""
    if not bullets:
        return "No previous context available."
    
    parts = [
        f"[{b.id[:8]}] {b.content} (helpful: {b.helpful_count}, harmful: {b.harmful_count})"
        for b in bullets
    ]
    return "\n".join(parts)
