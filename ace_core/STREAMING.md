# Streaming Response - ACE Framework

## 🎯 Overview

ACE Framework hỗ trợ **streaming response** để cải thiện trải nghiệm người dùng.

## ✨ Features

### Request-Response (Non-Streaming)
```python
result = await ace.process_query(query)
# Wait for complete response
print(result)
```

### Streaming
```python
async for chunk in ace.process_query_stream(query):
    print(chunk, end='', flush=True)
# Response appears token by token
```

## 🔧 Implementation

### OllamaClient Streaming

```python
async def generate_stream(self, prompt: str):
    """Generate streaming response"""
    payload = {
        "model": self.config.model,
        "prompt": prompt,
        "stream": True  # Enable streaming
    }
    
    async with self.session.post(...) as resp:
        async for line in resp.content:
            data = json.loads(line)
            if 'response' in data:
                yield Success(data['response'])
```

### ACEFramework Streaming

```python
async def process_query_stream(self, query: str):
    """Process with streaming"""
    full_response = ""
    
    # Stream to user
    async for result in self.client.generate_stream(prompt):
        match result:
            case Success(chunk):
                full_response += chunk
                yield chunk  # Stream to user
    
    # Learn from complete response
    trajectory = parse_trajectory_response(query, full_response)
    insights = await self.reflector.reflect(trajectory)
    self.curator.apply_delta(insights)
```

## 📊 Benefits

✅ **Better UX** - User sees response immediately
✅ **Perceived Speed** - Feels faster than waiting
✅ **Real-time Feedback** - Token-by-token display
✅ **Functional** - Still maintains pure functions for learning

## 🚀 Usage

### Interactive Mode
```bash
python main.py

👤 You: Hello
🤖 ACE:
Hello! How can I assist you today?
💡 Context: 1 bullets learned
```

### Demo Mode
```bash
python main.py demo

🤖 Response:
STEPS: [analyze; plan; execute]
OUTCOME: Complete answer here
SUCCESS: true
```

## 🎓 Architecture

```
User Query
    ↓
[Stream to User] ← OllamaClient.generate_stream()
    ↓              (token by token)
Full Response
    ↓
[Learn] → Parse → Reflect → Curate
    ↓
Context Updated
```

**Streaming for UX, Pure Functions for Learning!** 🚀
