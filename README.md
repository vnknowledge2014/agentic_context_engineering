# ACE Framework - Agentic Context Engineering

**Functional Programming + Railway-Oriented Programming + Advanced AI Tools**

## 🎯 Tổng Quan

Implementation hoàn chỉnh của **Agentic Context Engineering** (ICLR 2026) với:
- **Functional Programming** - Pure functions, immutable data
- **Railway-Oriented Programming** - Error handling với Result types
- **ACE Framework** - Generator, Reflector, Curator theo đúng paper
- **Advanced Tools** - Thinking, Search, Deep Research (như OpenAI)

## 🚀 Tính Năng Nổi Bật

### 🧠 Native Thinking Support
- Hỗ trợ models có native thinking (Qwen3, DeepSeek-R1)
- Hiển thị quá trình suy nghĩ real-time
- Timeout 300s cho thinking phức tạp
- Toggle `/thinking on|off`

### 🔍 Web Search (như OpenAI)
- Search trong context đã học
- Search trên web qua DuckDuckGo API
- Hiển thị nguồn: 📚 Context hoặc 🌐 Web
- Toggle `/web on|off`

### 🔬 Deep Research (như OpenAI)
- Multi-step research với 4 bước
- Tổng hợp từ nhiều nguồn
- Báo cáo toàn diện có cấu trúc
- Hỗ trợ web search

### 🌊 Streaming Response
- Real-time token-by-token response
- Hiển thị thinking process
- Better UX, perceived speed

## 📁 Cấu Trúc Project

```
ace_core/
├── ace_types.py          # Type definitions (immutable)
├── functional_core.py    # Pure functions (no side effects)
├── imperative_shell.py   # Side effects (I/O, API calls)
├── ace.py               # ACE Framework implementation
├── tools.py             # Thinking, Search, Research tools
├── main.py              # Entry point
├── test_functional.py   # Tests
└── requirements.txt
```

## 🚀 Quick Start

### 1. Prerequisites

```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Start Ollama
ollama serve

# Pull model (choose one)
ollama pull qwen2.5-coder:1.5b  # Fast
ollama pull qwen3:8b            # With native thinking
```

### 2. Install

```bash
cd ace_core
pip install -r requirements.txt
```

### 3. Run

```bash
# Interactive mode
python main.py

# Demo mode
python main.py demo
```

## 💬 Commands

### Basic Commands
- `help` - Hiển thị help
- `stats` - Context statistics
- `exit` - Thoát

### AI Tools
- `/think <query>` - Deep thinking với native support
- `/search <query>` - Search context/web
- `/research <topic>` - Deep research đa bước

### Toggles
- `/thinking on|off` - Bật/tắt native thinking mode
- `/web on|off` - Bật/tắt web search (như OpenAI)

## 🎮 Ví Dụ Sử dụng

```bash
👤 You: /web on
✅ 🌐 Web search enabled (like OpenAI)

👤 You: /search Python asyncio
🔍 Searching...
1. 🌐 asyncio is a library to write concurrent code...
   🔗 https://docs.python.org/3/library/asyncio.html
2. 📚 ACE uses asyncio for streaming responses...

👤 You: /thinking on
✅ Native thinking mode enabled

👤 You: Giải phương trình x^2 - 5x + 6 = 0
🤖 ACE:
💭 [Thinking...] Đây là phương trình bậc 2...
Tôi cần tìm a, b, c...
Delta = b^2 - 4ac...

🤖 [Answer:] Phương trình có 2 nghiệm: x1=2, x2=3

👤 You: /research Quantum Computing
🔬 Researching:
🔍 Step 1: Searching knowledge sources...
   Found 5 relevant sources
   1. 🌐 Web: Quantum computing uses quantum bits...
   2. 📚 Context: Quantum superposition allows...

🤔 Step 2: Generating research questions...
   Q1: What are the fundamental principles?
   Q2: What are current applications?
   Q3: What are the challenges?

💡 Step 3: Researching answers...
   ✓ Answered Q1
   ✓ Answered Q2
   ✓ Answered Q3

📝 Step 4: Synthesizing comprehensive report...
============================================================
QUANTUM COMPUTING RESEARCH REPORT

Executive Summary:
...
```

## 🧠 ACE Framework (ICLR 2026)

### 3 Thành Phần Chính

```
┌─────────────┐      ┌─────────────┐      ┌─────────────┐
│  Generator  │ ───> │  Reflector  │ ───> │   Curator   │
└─────────────┘      └─────────────┘      └─────────────┘
      │                     │                     │
   Trajectory           Insights            Delta Update
```

1. **Generator** - Tạo reasoning trajectories
2. **Reflector** - Trích xuất insights
3. **Curator** - Tích hợp vào context (grow-and-refine)

### Đặc Điểm

✅ **Incremental Delta Updates** - Không rewrite context
✅ **Grow-and-Refine** - Mở rộng và tinh chỉnh liên tục
✅ **Context Bullets** - Structured knowledge units
✅ **No Context Collapse** - Giữ detailed information
✅ **Self-Improving** - Học từ feedback

## 💡 Advanced Features

### Native Thinking Support

```python
# Tự động phát hiện thinking tokens
async for result in client.generate_stream(prompt, enable_thinking=True):
    # Hiển thị: 💭 [Thinking...] <thinking process>
    # Sau đó: 🤖 [Answer:] <final answer>
```

### Web Search Integration

```python
search_tool = SearchTool(enable_web_search=True)
results = await search_tool.search(query, context_bullets)
# Returns: context results + web results
```

### Deep Research

```python
research_tool = DeepResearchTool(enable_web_search=True)
report = await research_tool.research(topic, client, context)
# 4-step process: Search → Questions → Answers → Synthesis
```

## 📊 So Sánh Với OpenAI

| Feature | OpenAI | ACE Framework |
|---------|--------|---------------|
| Thinking | ✅ o1, o3 | ✅ Qwen3, DeepSeek-R1 |
| Web Search | ✅ Paid | ✅ Free (DuckDuckGo) |
| Deep Research | ✅ Paid | ✅ Free |
| Context Learning | ❌ | ✅ ACE mechanism |
| Streaming | ✅ | ✅ |
| Cost | 💰💰💰 | 🆓 Free |

## 🎓 Kiến Trúc

### Functional Core - Imperative Shell

```
┌─────────────────────────────────────┐
│     Imperative Shell (I/O)          │
│  - Ollama API (with thinking)       │
│  - Web search API                   │
│  - Logging, User I/O                │
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

### Railway-Oriented Programming

```python
# Success path
Success(value) → bind(func) → Success(new_value)

# Failure path (short-circuits)
Failure(error) → bind(func) → Failure(error)

# Pattern matching
match result:
    case Success(value): ...
    case Failure(error): ...
```

## 🔧 Configuration

```python
config = OllamaConfig(
    url="http://localhost:11434",
    model="qwen3:8b",           # Model with thinking
    temperature=0.7,
    max_tokens=512,
    context_window=2048
)
```

## 📈 Ưu Điểm

✅ **Minimal Code** - ~600 lines, 6 files
✅ **Functional** - Pure functions, immutable data
✅ **Type-Safe** - Strong typing
✅ **Advanced Tools** - Thinking, Search, Research
✅ **ACE-Compliant** - Tuân theo ICLR 2026 paper
✅ **Free** - No API costs
✅ **Extensible** - Dễ thêm tools mới

## 🚧 Troubleshooting

**Ollama not responding?**
```bash
curl http://localhost:11434/api/tags
```

**Thinking not showing?**
- Cần model hỗ trợ (Qwen3, DeepSeek-R1)
- Dùng `/thinking on`

**Web search not working?**
- Check internet connection
- DuckDuckGo API có thể rate limit

## 📚 Tài Liệu

- **Paper**: Agentic Context Engineering (ICLR 2026)
- **Pattern**: Functional Core - Imperative Shell
- **Error Handling**: Railway-Oriented Programming
- **Models**: Qwen3, DeepSeek-R1 (thinking support)

---

**ACE Framework - Where functional programming meets advanced AI!** 🚀
