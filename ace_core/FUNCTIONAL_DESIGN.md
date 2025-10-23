# Functional Design - ACE Framework

## 🎯 Nguyên Tắc Thiết Kế

### 1. Functional Core - Imperative Shell

```
┌─────────────────────────────────────────────┐
│         Imperative Shell                    │
│  (Side Effects - I/O Layer)                 │
│                                             │
│  - Ollama API calls (async)                 │
│  - File I/O                                 │
│  - User input/output                        │
│  - Logging                                  │
│  - Network requests                         │
└──────────────┬──────────────────────────────┘
               │
               │ Pure data in/out
               │
┌──────────────▼──────────────────────────────┐
│         Functional Core                     │
│  (Pure Functions - Business Logic)          │
│                                             │
│  - Context operations                       │
│  - Bullet scoring & ranking                 │
│  - Delta merging                            │
│  - Parsing & transformation                 │
│  - Deduplication logic                      │
└─────────────────────────────────────────────┘
```

### 2. Railway-Oriented Programming

```python
# Success track
Query → Success(trajectory) → Success(insights) → Success(delta) → Success(context)

# Failure track (short-circuits immediately)
Query → Failure(error) ──────────────────────────────────────────> Failure(error)
```

**Ưu điểm:**
- Không cần try/catch lồng nhau
- Error propagation tự động
- Code dễ đọc và maintain
- Type-safe error handling

### 3. Immutability

```python
# ❌ Mutable (OOP style)
class Bullet:
    def update_feedback(self, helpful: bool):
        if helpful:
            self.helpful_count += 1  # Modifies state
        else:
            self.harmful_count += 1

# ✅ Immutable (Functional style)
@dataclass(frozen=True)
class ContextBullet:
    helpful_count: int = 0
    
def update_bullet_feedback(bullet: ContextBullet, helpful: bool) -> ContextBullet:
    """Returns NEW bullet, original unchanged"""
    return ContextBullet(
        id=bullet.id,
        content=bullet.content,
        helpful_count=bullet.helpful_count + (1 if helpful else 0),
        harmful_count=bullet.harmful_count + (0 if helpful else 1),
        created_at=bullet.created_at,
        tags=bullet.tags
    )
```

**Ưu điểm:**
- No shared mutable state
- Thread-safe by default
- Easier to reason about
- Time-travel debugging possible

## 📦 Module Organization

### ace_types.py - Type Definitions

```python
# Immutable domain types
@dataclass(frozen=True)
class ContextBullet: ...

@dataclass(frozen=True)
class Trajectory: ...

@dataclass(frozen=True)
class Insight: ...

# Result types for Railway-Oriented Programming
@dataclass(frozen=True)
class Success(Generic[T]): ...

@dataclass(frozen=True)
class Failure(Generic[E]): ...
```

**Đặc điểm:**
- Tất cả types đều immutable (`frozen=True`)
- Generic types cho type safety
- No methods, chỉ data

### functional_core.py - Pure Functions

```python
# Pure function signature
def function_name(input: InputType) -> OutputType:
    """
    Pure function:
    - No side effects
    - Deterministic (same input → same output)
    - No external state access
    - No I/O operations
    """
    # Pure computation
    return result
```

**Ví dụ:**

```python
def score_bullet(bullet: ContextBullet, query_words: set) -> float:
    """Pure function - no side effects"""
    bullet_words = set(bullet.content.lower().split())
    overlap = len(query_words.intersection(bullet_words))
    feedback_score = (bullet.helpful_count - bullet.harmful_count) * 0.1
    return overlap + feedback_score

def merge_delta(context: ContextState, delta: DeltaUpdate) -> ContextState:
    """Pure function - returns new context"""
    new_bullets = dict(context.bullets)  # Copy
    
    for bullet in delta.bullets:
        duplicate_id = find_duplicate_bullet(bullet, new_bullets)
        if duplicate_id:
            existing = new_bullets[duplicate_id]
            new_bullets[duplicate_id] = update_bullet_feedback(existing, True)
        else:
            new_bullets[bullet.id] = bullet
    
    return ContextState(bullets=new_bullets, version=context.version + 1)
```

### imperative_shell.py - Side Effects

```python
# Impure operations isolated here
class OllamaClient:
    async def generate(self, prompt: str) -> Result[str, str]:
        """I/O operation wrapped in Result"""
        try:
            # Network I/O
            response = await self.session.post(...)
            return Success(response)
        except Exception as e:
            return Failure(str(e))

def log_info(message: str) -> None:
    """Side effect - prints to console"""
    print(f"ℹ️  {message}")
```

### ace.py - Composition

```python
class ACEFramework:
    """Composes pure functions with I/O operations"""
    
    async def process_query(self, query: str) -> Result[Tuple[str, DeltaUpdate], str]:
        # Step 1: I/O - Generate trajectory
        traj_result = await self.generator.generate_trajectory(query, context)
        
        match traj_result:
            case Failure(error):
                return Failure(error)  # Short-circuit
            case Success(trajectory):
                pass
        
        # Step 2: I/O - Reflect
        insights_result = await self.reflector.reflect(trajectory)
        
        match insights_result:
            case Failure(error):
                return Failure(error)  # Short-circuit
            case Success(insights):
                pass
        
        # Step 3: Pure - Create delta
        delta = self.curator.create_delta(insights)  # Pure function
        
        # Step 4: Pure - Apply delta
        self.curator.apply_delta(delta)  # Pure function
        
        return Success((response, delta))
```

## 🔄 Data Flow

### Query Processing Pipeline

```
User Query (String)
    ↓
[Generator] → I/O: Ollama API
    ↓
Trajectory (Immutable)
    ↓
[Reflector] → I/O: Ollama API
    ↓
Insights (Immutable List)
    ↓
[Curator] → Pure: insights_to_delta()
    ↓
DeltaUpdate (Immutable)
    ↓
[Curator] → Pure: merge_delta()
    ↓
ContextState (New Immutable)
```

### Error Handling Flow

```
Success Path:
Query → Success(traj) → Success(insights) → Success(delta) → Success(result)

Failure Path (any step fails):
Query → ... → Failure(error) → Failure(error) → ... → Failure(error)
                    ↓
              Log error & return to user
```

## 🧪 Testing Strategy

### Pure Functions (Easy to Test)

```python
def test_score_bullet():
    # Arrange
    bullet = ContextBullet(
        id="test",
        content="validate input data",
        helpful_count=5,
        harmful_count=0
    )
    query_words = {"validate", "input"}
    
    # Act
    score = score_bullet(bullet, query_words)
    
    # Assert
    assert score == 2.5  # 2 overlaps + 0.5 feedback
```

**Ưu điểm:**
- No mocking needed
- No setup/teardown
- Fast execution
- Deterministic

### Impure Functions (Need Mocking)

```python
async def test_ollama_client():
    # Need to mock network I/O
    mock_session = MockSession()
    client = OllamaClient(config)
    client.session = mock_session
    
    result = await client.generate("test")
    assert isinstance(result, Success)
```

## 💡 Best Practices

### 1. Keep Functions Pure When Possible

```python
# ✅ Good - Pure function
def calculate_score(helpful: int, harmful: int) -> float:
    return (helpful - harmful) * 0.1

# ❌ Bad - Impure (accesses external state)
def calculate_score(bullet_id: str) -> float:
    bullet = global_context.bullets[bullet_id]  # External state
    return (bullet.helpful_count - bullet.harmful_count) * 0.1
```

### 2. Use Pattern Matching for Result Types

```python
# ✅ Good - Explicit error handling
match result:
    case Success(value):
        process(value)
    case Failure(error):
        log_error(error)

# ❌ Bad - Implicit error handling
try:
    value = result.value  # May not exist
    process(value)
except:
    pass
```

### 3. Compose Functions

```python
# ✅ Good - Composable
def get_relevant_bullets(context, query, max_bullets):
    bullets = list(context.bullets.values())
    scored = [(score_bullet(b, query_words), b) for b in bullets]
    sorted_bullets = sorted(scored, key=lambda x: x[0], reverse=True)
    return [b for _, b in sorted_bullets[:max_bullets]]

# ❌ Bad - Monolithic
def get_relevant_bullets(context, query, max_bullets):
    # 100 lines of mixed logic
    ...
```

### 4. Separate I/O from Logic

```python
# ✅ Good - Separated
async def process_query(query: str) -> Result[str, str]:
    # I/O
    response = await ollama_client.generate(prompt)
    
    # Pure logic
    match response:
        case Success(text):
            trajectory = parse_trajectory_response(query, text)  # Pure
            return Success(trajectory)
        case Failure(error):
            return Failure(error)

# ❌ Bad - Mixed
async def process_query(query: str) -> str:
    response = await ollama_client.generate(prompt)  # I/O
    trajectory = Trajectory(...)  # Logic
    self.context.add(trajectory)  # Side effect
    return trajectory.outcome
```

## 📊 Benefits Summary

| Aspect | Benefit |
|--------|---------|
| **Testability** | Pure functions easy to test, no mocking |
| **Maintainability** | Clear separation of concerns |
| **Concurrency** | No shared mutable state |
| **Debugging** | Deterministic, reproducible |
| **Composition** | Functions easily composable |
| **Error Handling** | Railway-oriented, type-safe |
| **Reasoning** | Easier to understand data flow |

---

**Functional programming makes complex systems simple!** 🚀
