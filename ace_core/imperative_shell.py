"""
ACE Imperative Shell - Side Effects Layer
Handles all I/O operations with Railway-Oriented Programming
"""
import asyncio
import aiohttp
from typing import Callable, TypeVar
from ace_types import Success, Failure, Result, OllamaConfig

T = TypeVar('T')
U = TypeVar('U')

# Railway-Oriented Programming utilities
def bind(result: Result[T, str], func: Callable[[T], Result[U, str]]) -> Result[U, str]:
    """Bind operation for Result monad"""
    match result:
        case Success(value):
            return func(value)
        case Failure(error):
            return Failure(error)

def map_result(result: Result[T, str], func: Callable[[T], U]) -> Result[U, str]:
    """Map operation for Result monad"""
    match result:
        case Success(value):
            return Success(func(value))
        case Failure(error):
            return Failure(error)

async def try_async(func: Callable, *args, **kwargs) -> Result[T, str]:
    """Execute async function and wrap in Result"""
    try:
        result = await func(*args, **kwargs)
        return Success(result)
    except Exception as e:
        return Failure(f"Error: {str(e)}")

# Ollama API operations
class OllamaClient:
    """Ollama API client with error handling"""
    
    def __init__(self, config: OllamaConfig):
        self.config = config
        self.session: aiohttp.ClientSession | None = None
    
    async def initialize(self) -> Result[bool, str]:
        """Initialize client"""
        try:
            self.session = aiohttp.ClientSession()
            async with self.session.get(f"{self.config.url}/api/tags") as resp:
                if resp.status == 200:
                    return Success(True)
                return Failure(f"Ollama not available: {resp.status}")
        except Exception as e:
            return Failure(f"Connection failed: {str(e)}")
    
    async def generate(self, prompt: str, enable_thinking: bool = False) -> Result[str, str]:
        """Generate response from Ollama"""
        if not self.session:
            return Failure("Client not initialized")
        
        payload = {
            "model": self.config.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": self.config.temperature,
                "num_predict": min(self.config.max_tokens, 512),
                "num_ctx": min(self.config.context_window, 2048)
            }
        }
        
        if enable_thinking:
            payload["options"]["enable_thinking"] = True
        
        timeout = 300 if enable_thinking else 120
        
        try:
            async with self.session.post(
                f"{self.config.url}/api/generate",
                json=payload,
                timeout=aiohttp.ClientTimeout(total=timeout)
            ) as resp:
                if resp.status == 200:
                    result = await resp.json()
                    return Success(result.get('response', '').strip())
                return Failure(f"API error: {resp.status}")
        except asyncio.TimeoutError:
            return Failure("Request timeout")
        except Exception as e:
            return Failure(f"Generation failed: {str(e)}")
    
    async def generate_stream(self, prompt: str, enable_thinking: bool = False):
        """Generate streaming response from Ollama with thinking support"""
        if not self.session:
            yield Failure("Client not initialized")
            return
        
        payload = {
            "model": self.config.model,
            "prompt": prompt,
            "stream": True,
            "options": {
                "temperature": self.config.temperature,
                "num_predict": min(self.config.max_tokens, 512),
                "num_ctx": min(self.config.context_window, 2048)
            }
        }
        
        if enable_thinking:
            payload["options"]["enable_thinking"] = True
        
        timeout = 300 if enable_thinking else 120
        
        try:
            import json
            async with self.session.post(
                f"{self.config.url}/api/generate",
                json=payload,
                timeout=aiohttp.ClientTimeout(total=timeout)
            ) as resp:
                if resp.status == 200:
                    in_thinking = False
                    async for line in resp.content:
                        if line:
                            try:
                                data = json.loads(line.decode('utf-8'))
                                
                                # Handle thinking tokens
                                if 'thinking' in data:
                                    if not in_thinking:
                                        yield Success("\n💭 [Thinking...] ")
                                        in_thinking = True
                                    yield Success(data['thinking'])
                                    continue
                                
                                if in_thinking and 'response' in data:
                                    yield Success("\n\n🤖 [Answer:] ")
                                    in_thinking = False
                                
                                if 'response' in data:
                                    yield Success(data['response'])
                                
                                if data.get('done', False):
                                    break
                            except json.JSONDecodeError:
                                continue
                else:
                    yield Failure(f"API error: {resp.status}")
        except asyncio.TimeoutError:
            yield Failure("Request timeout")
        except Exception as e:
            yield Failure(f"Generation failed: {str(e)}")
    
    async def shutdown(self) -> Result[None, str]:
        """Shutdown client"""
        try:
            if self.session:
                await self.session.close()
            return Success(None)
        except Exception as e:
            return Failure(f"Shutdown failed: {str(e)}")

# Logging operations
def log_info(message: str) -> None:
    """Log info message"""
    print(f"ℹ️  {message}")

def log_success(message: str) -> None:
    """Log success message"""
    print(f"✅ {message}")

def log_error(message: str) -> None:
    """Log error message"""
    print(f"❌ {message}")

def log_warning(message: str) -> None:
    """Log warning message"""
    print(f"⚠️  {message}")
