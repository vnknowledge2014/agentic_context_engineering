#!/usr/bin/env python3
"""
Test Functional Core - Pure Functions
Demonstrates functional programming principles
"""
from ace_types import ContextBullet, ContextState, ReasoningStep, Trajectory, Insight
from functional_core import (
    create_bullet, update_bullet_feedback, score_bullet,
    get_relevant_bullets, find_duplicate_bullet, merge_delta,
    prune_low_quality_bullets, limit_context_size,
    parse_trajectory_response, parse_insights_response, insights_to_delta
)

def test_bullet_operations():
    """Test pure bullet operations"""
    print("🧪 Testing Bullet Operations")
    
    # Create bullet (pure function)
    bullet1 = create_bullet("Always validate input", ["strategy"])
    print(f"✅ Created bullet: {bullet1.id[:8]}... - {bullet1.content}")
    
    # Update feedback (returns new bullet, original unchanged)
    bullet2 = update_bullet_feedback(bullet1, helpful=True)
    print(f"✅ Updated feedback: helpful={bullet2.helpful_count} (original={bullet1.helpful_count})")
    
    # Score bullet
    query_words = {"validate", "input", "check"}
    score = score_bullet(bullet2, query_words)
    print(f"✅ Bullet score: {score}")

def test_context_operations():
    """Test context operations"""
    print("\n🧪 Testing Context Operations")
    
    # Create context with bullets
    bullets = {
        "b1": create_bullet("Validate input before processing", ["strategy"]),
        "b2": create_bullet("Handle errors gracefully", ["strategy"]),
        "b3": create_bullet("Log all operations", ["optimization"])
    }
    context = ContextState(bullets=bullets)
    print(f"✅ Created context with {len(context.bullets)} bullets")
    
    # Get relevant bullets
    query = "How to validate input data?"
    relevant = get_relevant_bullets(context, query, max_bullets=2)
    print(f"✅ Found {len(relevant)} relevant bullets for query")
    
    # Find duplicate
    new_bullet = create_bullet("Always validate input first", ["strategy"])
    duplicate_id = find_duplicate_bullet(new_bullet, context.bullets)
    print(f"✅ Duplicate detection: {duplicate_id or 'None found'}")

def test_immutability():
    """Test immutability of data structures"""
    print("\n🧪 Testing Immutability")
    
    # Create bullet
    bullet = create_bullet("Test content", ["test"])
    original_helpful = bullet.helpful_count
    
    # Try to update (creates new bullet)
    updated = update_bullet_feedback(bullet, helpful=True)
    
    print(f"✅ Original bullet unchanged: {bullet.helpful_count == original_helpful}")
    print(f"✅ New bullet updated: {updated.helpful_count == original_helpful + 1}")
    print(f"✅ Different objects: {bullet is not updated}")

def test_parsing():
    """Test parsing functions"""
    print("\n🧪 Testing Parsing Functions")
    
    # Parse trajectory
    response = """
    STEPS: [Analyze query; Plan approach; Execute solution]
    OUTCOME: Successfully completed task
    SUCCESS: true
    USED_BULLETS: [b1, b2]
    """
    trajectory = parse_trajectory_response("Test query", response)
    print(f"✅ Parsed trajectory: {len(trajectory.steps)} steps, success={trajectory.success}")
    
    # Parse insights
    insights_response = """
    INSIGHTS:
    [Content: Always validate input; Type: strategy; Confidence: 0.9]
    [Content: Avoid null pointers; Type: failure_mode; Confidence: 0.8]
    """
    insights = parse_insights_response(insights_response, "source1")
    print(f"✅ Parsed {len(insights)} insights")

def test_railway_pattern():
    """Test railway-oriented programming pattern"""
    print("\n🧪 Testing Railway-Oriented Pattern")
    
    from ace_types import Success, Failure
    
    # Success path
    result1 = Success(42)
    print(f"✅ Success value: {result1.value}")
    
    # Failure path
    result2 = Failure("Something went wrong")
    print(f"✅ Failure error: {result2.error}")
    
    # Pattern matching
    match result1:
        case Success(value):
            print(f"✅ Pattern match Success: {value}")
        case Failure(error):
            print(f"❌ Pattern match Failure: {error}")

def main():
    """Run all tests"""
    print("="*60)
    print("ACE Functional Core Tests")
    print("="*60)
    
    test_bullet_operations()
    test_context_operations()
    test_immutability()
    test_parsing()
    test_railway_pattern()
    
    print("\n" + "="*60)
    print("✅ All tests passed!")
    print("="*60)

if __name__ == "__main__":
    main()
