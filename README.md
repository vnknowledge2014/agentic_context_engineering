# ACE Framework - Agentic Context Engineering

**Functional Programming + Railway-Oriented Programming Implementation**

## 🎯 Tổng Quan

Implementation hoàn chỉnh của **Agentic Context Engineering** (ICLR 2026) với:
- **Functional Programming** - Pure functions, immutable data
- **Railway-Oriented Programming** - Error handling với Result types
- **Functional Core - Imperative Shell** - Tách biệt business logic và side effects
- **ACE Framework** - Generator, Reflector, Curator theo đúng paper

## 📁 Cấu Trúc Project

```
ACE/
├── ace_core/
│   ├── ace_types.py          # Type definitions (immutable)
│   ├── functional_core.py    # Pure functions (no side effects)
│   ├── imperative_shell.py   # Side effects (I/O, logging)
│   ├── ace.py               # ACE Framework implementation
│   ├── main.py              # Entry point
│   ├── test_functional.py   # Functional tests
│   ├── requirements.txt
│   └── README.md
├── Agentic_Context_Engineer.pdf  # ICLR 2026 paper
└── README.md                     # This file
```

**Total: ~5 core files, ~500 lines of clean functional code**

## 🧠 ACE Framework (ICLR 2026)

### 3 Thành Phần Chính

```
┌─────────────┐      ┌─────────────┐      ┌─────────────┐
│  Generator  │ ───> │  Reflector  │ ───> │   Curator   │
└─────────────┘      └─────────────┘      └─────────────┘
      │                     │                     │
   Trajectory           Insights            Delta Update
```

1. **Generator** - Tạo reasoning trajectories từ queries
2. **Reflector** - Trích xuất insights từ trajectories
3. **Curator** - Tích hợp insights vào context (grow-and-refine)

### Đặc Điểm Chính

✅ **Incremental Delta Updates** - Không rewrite toàn bộ context
✅ **Grow-and-Refine** - Mở rộng và tinh chỉnh liên tục
✅ **Context Bullets** - Structured knowledge units
✅ **No Context Collapse** - Giữ được detailed information
✅ **Self-Improving** - Học từ execution feedback

## 🚀 Quick Start

### 1. Prerequisites

```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Start Ollama server
ollama serve

# Pull model
ollama pull qwen2.5-coder:1.5b
```

### 2. Install Dependencies

```bash
cd ace_core
pip install -r requirements.txt
```

### 3. Run Tests

```bash
# Test functional core
python test_functional.py
```

### 4. Run ACE System

**Demo Mode:**
```bash
python main.py demo
```

**Interactive Mode:**
```bash
python main.py
```

## 💡 Functional Programming Features

### Pure Functions

```python
# functional_core.py - No side effects
def create_bullet(content: str, tags: List[str]) -> ContextBullet:
    """Pure function - same input always gives same output"""
    return ContextBullet(id=str(uuid.uuid4()), content=content, tags=tuple(tags))

def update_bullet_feedback(bullet: ContextBullet, helpful: bool) -> ContextBullet:
    """Returns new bullet, original unchanged (immutable)"""
    return ContextBullet(
        id=bullet.id,
        content=bullet.content,
        helpful_count=bullet.helpful_count + (1 if helpful else 0),
        # ... other fields
    )
```

### Railway-Oriented Programming

```python
# Success path
Success(value) → bind(func) → Success(new_value) → ...

# Failure path (short-circuits)
Failure(error) → bind(func) → Failure(error) → ...

# Pattern matching
match result:
    case Success(value):
        # Handle success
    case Failure(error):
        # Handle error
```

### Immutable Data Structures

```python
@dataclass(frozen=True)  # Immutable
class ContextBullet:
    id: str
    content: str
    helpful_count: int = 0
    # Cannot be modified after creation
```

## 📊 Context Engineering

### Context Bullets

Mỗi bullet là một knowledge unit:

```python
ContextBullet(
    id="uuid-123",
    content="Strategy: Always validate input before processing",
    helpful_count=5,
    harmful_count=0,
    tags=["strategy"]
)
```

### Delta Updates

Incremental updates thay vì full rewrite:

```python
# Old approach (context collapse risk)
context = llm.rewrite(entire_context)  # ❌ Loses information

# ACE approach (preserves information)
delta = DeltaUpdate(bullets=(new_bullet1, new_bullet2))  # ✅
context = merge_delta(context, delta)
```

### Grow-and-Refine Mechanism

```python
1. Grow   - Add new bullets from insights
2. Prune  - Remove low-quality bullets
3. Limit  - Keep top N most helpful bullets
```

## 🎓 Kiến Trúc

### Functional Core - Imperative Shell

```
┌─────────────────────────────────────┐
│     Imperative Shell (I/O)          │
│  - Ollama API calls                 │
│  - Logging                          │
│  - User input/output                │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│     Functional Core (Pure)          │
│  - Context operations               │
│  - Bullet scoring                   │
│  - Delta merging                    │
│  - Parsing                          │
└─────────────────────────────────────┘
```

### Tại Sao Functional?

✅ **Testable** - Pure functions dễ test
✅ **Composable** - Functions có thể compose
✅ **Predictable** - No hidden state
✅ **Concurrent** - No shared mutable state
✅ **Maintainable** - Clear separation of concerns

## 🔧 Commands (Interactive Mode)

- `stats` - Hiển thị context statistics
- `help` - Hiển thị help
- `exit` - Thoát system

## 📈 So Sánh Với Cũ

| Feature | Old (OOP) | New (Functional) |
|---------|-----------|------------------|
| Lines of code | 580KB+ (40+ files) | ~500 lines (5 files) |
| Mutable state | ✅ Everywhere | ❌ None |
| Side effects | ✅ Mixed with logic | ✅ Isolated |
| Error handling | Try/catch | Railway-oriented |
| Testability | Hard | Easy |
| ACE compliant | ❌ No | ✅ Yes |

## 🎯 Ưu Điểm

✅ **Minimal Code** - Chỉ 5 files core, ~500 lines
✅ **Functional** - Pure functions, immutable data
✅ **Type-Safe** - Strong typing với dataclasses
✅ **Error Handling** - Railway-oriented programming
✅ **ACE-Compliant** - Tuân theo đúng ICLR 2026 paper
✅ **No Context Collapse** - Incremental delta updates
✅ **Self-Improving** - Learns from execution feedback
✅ **Testable** - Pure functions dễ test

## 📚 Tài Liệu Tham Khảo

- **Paper**: Agentic Context Engineering (ICLR 2026)
- **Pattern**: Functional Core - Imperative Shell
- **Error Handling**: Railway-Oriented Programming (Scott Wlaschin)
- **FP**: Functional Programming principles

## 🚧 Troubleshooting

**Ollama not responding?**
```bash
curl http://localhost:11434/api/tags
```

**Import errors?**
```bash
cd ace_core
python -c "import ace_types; import functional_core; print('OK')"
```

**Test functional core:**
```bash
python test_functional.py
```

---

**ACE Framework - Where functional programming meets agentic AI!** 🚀
