"""
ACE Types - Functional Type Definitions
Railway-Oriented Programming with Result types
"""
from dataclasses import dataclass, field
from typing import TypeVar, Generic, Callable, List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

# Generic types
T = TypeVar('T')
E = TypeVar('E')

# Result type for Railway-Oriented Programming
@dataclass(frozen=True)
class Success(Generic[T]):
    value: T

@dataclass(frozen=True)
class Failure(Generic[E]):
    error: E

Result = Success[T] | Failure[E]

# ACE Domain Types
@dataclass(frozen=True)
class ContextBullet:
    """Immutable context bullet"""
    id: str
    content: str
    helpful_count: int = 0
    harmful_count: int = 0
    created_at: datetime = field(default_factory=datetime.now)
    tags: List[str] = field(default_factory=list)

@dataclass(frozen=True)
class ReasoningStep:
    """Single reasoning step"""
    description: str
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass(frozen=True)
class Trajectory:
    """Reasoning trajectory from Generator"""
    query: str
    steps: tuple[ReasoningStep, ...]
    outcome: str
    success: bool
    used_bullets: tuple[str, ...] = ()
    feedback: Optional[str] = None

@dataclass(frozen=True)
class InsightType(Enum):
    STRATEGY = "strategy"
    FAILURE_MODE = "failure_mode"
    OPTIMIZATION = "optimization"

@dataclass(frozen=True)
class Insight:
    """Insight from Reflector"""
    content: str
    insight_type: str
    confidence: float
    source_id: str

@dataclass(frozen=True)
class DeltaUpdate:
    """Delta context update"""
    bullets: tuple[ContextBullet, ...]
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass(frozen=True)
class ContextState:
    """Immutable context state"""
    bullets: Dict[str, ContextBullet]
    version: int = 0

@dataclass(frozen=True)
class OllamaConfig:
    """Ollama configuration"""
    url: str = "http://localhost:11434"
    model: str = "qwen2.5-coder:1.5b"
    temperature: float = 0.7
    max_tokens: int = 1024
    context_window: int = 4096
