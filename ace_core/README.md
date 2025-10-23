# ACE Framework - Agentic Context Engineering

**Functional Programming + Railway-Oriented Programming Implementation**

## 🎯 Kiến Trúc

Dự án được cấu trúc theo **Functional Core - Imperative Shell** pattern:

```
ace_core/
├── ace_types.py          # Type definitions (immutable)
├── functional_core.py    # Pure functions (business logic)
├── imperative_shell.py   # Side effects (I/O, logging)
├── ace.py               # ACE Framework (Generator, Reflector, Curator)
├── main.py              # Entry point
└── requirements.txt
```

## 🧠 Nguyên Lý ACE (ICLR 2026)

### 3 Thành Phần Chính

1. **Generator** - Tạo reasoning trajectories
2. **Reflector** - Trích xuất insights từ trajectories
3. **Curator** - Tích hợp insights vào context

### Quy Trình

```
Query → Generator → Trajectory → Reflector → Insights → Curator → Delta Update → Context
```

### Đặc Điểm

- **Incremental Delta Updates** - Cập nhật từng phần, không rewrite toàn bộ
- **Grow-and-Refine** - Mở rộng và tinh chỉnh context liên tục
- **Context Bullets** - Structured, itemized knowledge units
- **Railway-Oriented Programming** - Error handling với Result types

## 🚀 Chạy Hệ Thống

### Prerequisites

```bash
# Cài Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Start Ollama
ollama serve

# Pull model
ollama pull qwen2.5-coder:1.5b
```

### Demo Mode

```bash
cd ace_core
python main.py demo
```

### Interactive Mode

```bash
python main.py
```

## 💡 Functional Programming Features

### Pure Functions (functional_core.py)

- Không có side effects
- Deterministic - cùng input → cùng output
- Testable và composable
- Immutable data structures

### Railway-Oriented Programming

```python
# Success path
Success(value) → bind(func) → Success(new_value)

# Failure path
Failure(error) → bind(func) → Failure(error)
```

### Immutable Types

```python
@dataclass(frozen=True)
class ContextBullet:
    id: str
    content: str
    helpful_count: int = 0
    # Không thể modify sau khi tạo
```

## 📊 Context Engineering

### Context Bullets

Mỗi bullet là một unit of knowledge:

```python
ContextBullet(
    id="uuid",
    content="Strategy: Always validate input before processing",
    helpful_count=5,
    harmful_count=0,
    tags=["strategy"]
)
```

### Delta Updates

Thay vì rewrite toàn bộ context:

```python
DeltaUpdate(
    bullets=(bullet1, bullet2, bullet3),
    timestamp=now
)
```

### Grow-and-Refine

1. **Grow** - Thêm bullets mới từ insights
2. **Refine** - Loại bỏ bullets kém chất lượng
3. **Limit** - Giữ top N bullets hữu ích nhất

## 🔧 Commands

**Interactive Mode:**
- `stats` - Hiển thị context statistics
- `help` - Hiển thị help
- `exit` - Thoát

## 📈 Ưu Điểm

✅ **Functional** - Pure functions, dễ test và maintain
✅ **Type-Safe** - Strong typing với dataclasses
✅ **Error Handling** - Railway-oriented programming
✅ **Immutable** - Không có shared mutable state
✅ **Composable** - Functions có thể compose dễ dàng
✅ **Scalable** - Incremental updates, không context collapse
✅ **ACE-Compliant** - Tuân theo đúng paper ICLR 2026

## 🎓 Tài Liệu Tham Khảo

- **Paper**: Agentic Context Engineering (ICLR 2026)
- **Pattern**: Functional Core - Imperative Shell
- **Error Handling**: Railway-Oriented Programming
- **Architecture**: Generator-Reflector-Curator

---

**ACE Framework - Where functional programming meets agentic AI!** 🚀
