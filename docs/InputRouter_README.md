# InputRouter Component Documentation

## Overview

The **InputRouter** is a core component of Prism Terminal that intelligently classifies user input as either a **shell command** or a **conversational prompt** for AI processing. It uses a sophisticated multi-algorithm confidence scoring system to make accurate routing decisions.

**Location**: `src/components/input_router.py`  
**Dependencies**: `src/config.py`, `src/models/core_models.py`  
**Architecture**: Singleton pattern with configurable algorithms  

---

## Table of Contents

1. [Purpose & Functionality](#purpose--functionality)
2. [Architecture Overview](#architecture-overview)
3. [Configuration System](#configuration-system)
4. [Algorithm Details](#algorithm-details)
5. [File Structure](#file-structure)
6. [Usage Examples](#usage-examples)
7. [Testing](#testing)
8. [Error Handling](#error-handling)
9. [Performance](#performance)
10. [Extension Guide](#extension-guide)

---

## Purpose & Functionality

### Core Problem
Prism Terminal supports dual-mode interaction where users can:
- Execute shell commands: `git status`, `ls -la`, `!clear`
- Ask AI questions: `"What does this error mean?"`, `"How do I configure Git?"`

The InputRouter solves the challenge of **automatically determining user intent** without requiring explicit mode switching.

### Solution Approach
Uses **4 confidence-scoring algorithms** that analyze different aspects of input:
1. **Shell Prefix Detection** - Looks for `!`, `$`, `>`
2. **Command Dictionary Matching** - Matches against known commands
3. **Question Pattern Detection** - Identifies question words and patterns
4. **Sentence Structure Analysis** - Analyzes grammar and punctuation

Each algorithm contributes confidence scores, and the highest total confidence determines the routing decision.

---

## Architecture Overview

### Design Patterns
- **Singleton Pattern**: Single `input_router` instance used throughout application
- **Strategy Pattern**: Multiple algorithms with consistent interface
- **Configuration Pattern**: All parameters externalized to config
- **Graceful Degradation**: System remains stable under any input conditions

### Data Flow
```
User Input → InputRouter.route_input() → RouteDecision
    ↓
Input Validation & Sanitization
    ↓
4 Parallel Algorithms Execute
    ↓
Confidence Scores Combined
    ↓
Decision: "command" or "prompt"
```

### SOLID Principles Implementation
- **SRP**: Each algorithm has single responsibility
- **OCP**: Easy to add new algorithms without modifying existing code
- **LSP**: All algorithms follow consistent interface pattern
- **ISP**: Clean, focused interfaces for each component
- **DIP**: Depends on configuration abstractions, not hard-coded values

---

## Configuration System

### Configuration Files

#### `src/config.py`
Contains all InputRouter configuration with Pydantic validation:

```python
# Confidence Values (0.0-1.0)
PREFIX_COMMAND_CONFIDENCE: float = 0.8    # Shell prefix detected
PREFIX_PROMPT_CONFIDENCE: float = 0.1     # No shell prefix
COMMAND_MATCH_CONFIDENCE: float = 0.7     # Known command found
COMMAND_NO_MATCH_CONFIDENCE: float = 0.2  # Unknown command
QUESTION_PROMPT_CONFIDENCE: float = 0.6   # Question pattern detected
QUESTION_COMMAND_CONFIDENCE: float = 0.1  # No question pattern
SENTENCE_PROMPT_CONFIDENCE: float = 0.5   # Sentence-like structure
SENTENCE_COMMAND_CONFIDENCE: float = 0.3  # Command-like structure

# Configurable Word Lists (comma-separated strings)
SHELL_PREFIXES: str = "!,$,>"
KNOWN_COMMANDS: str = "ls,cd,pwd,git,python,npm,curl,grep,cat,mkdir,rm,cp,mv,chmod,sudo"
QUESTION_WORDS: str = "what,how,why,help,can,could,would,should,where,when,which,who"
SENTENCE_ARTICLES: str = "a,an,the,this,that,these,those"
```

#### Environment Variable Override
All configuration can be overridden via `.env` file:
```bash
PREFIX_COMMAND_CONFIDENCE=0.9
KNOWN_COMMANDS="ls,cd,pwd,git,docker,kubectl,terraform"
QUESTION_WORDS="what,how,why,help,qué,cómo,por qué"  # Multi-language support
```

### Configuration Benefits
- **Tunable**: Adjust confidence values for different use cases
- **Extensible**: Add new commands, question words, shell prefixes
- **Multilingual**: Support different languages by adding localized question words
- **Environment-specific**: Different configs for development/production

---

## Algorithm Details

### 1. Shell Prefix Detection (`_detect_prefixes`)

**Purpose**: Detect shell-specific prefixes that indicate commands

**Logic**:
- Checks first character against configured shell prefixes
- Default prefixes: `!` (bang), `$` (variable), `>` (redirect)
- Returns high command confidence if prefix found

**Examples**:
```python
"!clear"     → (0.8, 0.1) # Command confidence, Prompt confidence
"$USER"      → (0.8, 0.1)
">output"    → (0.8, 0.1)
"hello"      → (0.1, 0.8)
```

### 2. Command Dictionary Matching (`_match_commands`)

**Purpose**: Match first word against known shell commands

**Logic**:
- Splits input into words, checks first word (case-insensitive)
- Matches against configurable command dictionary
- Supports 15 common commands by default, easily extensible

**Examples**:
```python
"git status"    → (0.7, 0.2)
"ls -la"        → (0.7, 0.2)
"unknown cmd"   → (0.2, 0.7)
""              → (0.2, 0.7)  # Empty input
```

### 3. Question Pattern Detection (`_detect_questions`)

**Purpose**: Identify conversational questions and help requests

**Logic**:
- Checks for question words (configurable list)
- Looks for question marks
- Detects questions starting with question words
- **Fixed**: Uses word boundaries, not substring matching

**Examples**:
```python
"what is this?"       → (0.1, 0.6)
"how do I configure"  → (0.1, 0.6)
"help me"            → (0.1, 0.6)
"download file"      → (0.6, 0.1)  # No false positive for "how" substring
```

### 4. Sentence Structure Analysis (`_analyze_structure`)

**Purpose**: Analyze grammatical structure to distinguish natural language from commands

**Logic**:
- Counts sentence indicators: articles, punctuation, capitalization, word count
- Uses threshold-based scoring (≥2 indicators = sentence-like)
- Helps distinguish `"Delete the file"` (prompt) from `"rm file"` (command)

**Examples**:
```python
"This is a sentence."     → (0.3, 0.5)  # Articles + punctuation + capitalization
"Please help me setup."   → (0.3, 0.5)  # Multi-word + articles
"ls"                     → (0.5, 0.3)   # Command-like
"git push"               → (0.5, 0.3)   # Command-like
```

---

## File Structure

### Core Files

```
src/
├── components/
│   └── input_router.py          # Main InputRouter implementation
├── models/
│   └── core_models.py           # RouteDecision model definition
├── config.py                    # Configuration with Pydantic validation
└── __init__.py                  # Package initialization

tests/
├── test_input_router.py         # Comprehensive functionality tests
└── test_edge_cases.py          # Edge case and error handling tests
```

### Key Classes and Models

#### `InputRouter` Class (`src/components/input_router.py`)
```python
class InputRouter:
    def __init__(self):
        # Parses configuration into efficient sets for O(1) lookup
        
    def route_input(self, user_input: str) -> RouteDecision:
        # Main entry point with comprehensive error handling
        
    def _parse_config_list(self, config_string: str) -> Set[str]:
        # Converts comma-separated strings to sets with error handling
        
    def _detect_prefixes(self, input_str: str) -> tuple[float, float]:
        # Algorithm 1: Shell prefix detection
        
    def _match_commands(self, input_str: str) -> tuple[float, float]:
        # Algorithm 2: Command dictionary matching
        
    def _detect_questions(self, input_str: str) -> tuple[float, float]:
        # Algorithm 3: Question pattern detection
        
    def _analyze_structure(self, input_str: str) -> tuple[float, float]:
        # Algorithm 4: Sentence structure analysis
```

#### `RouteDecision` Model (`src/models/core_models.py`)
```python
class RouteDecision(BaseModel):
    prediction: Literal["command", "prompt"]
```

---

## Usage Examples

### Basic Usage
```python
from src.components.input_router import input_router

# Command examples
result = input_router.route_input("git status")
print(result.prediction)  # → "command"

result = input_router.route_input("!clear")
print(result.prediction)  # → "command"

# Prompt examples  
result = input_router.route_input("What does this error mean?")
print(result.prediction)  # → "prompt"

result = input_router.route_input("How do I configure Git?")
print(result.prediction)  # → "prompt"
```

### Configuration Customization
```python
# In .env file
KNOWN_COMMANDS="ls,cd,pwd,git,docker,kubectl,terraform,npm,yarn"
QUESTION_WORDS="what,how,why,help,qué,cómo,por qué,was,wie,warum"
SHELL_PREFIXES="!,$,>,#,@"

# Confidence tuning for different environments
PREFIX_COMMAND_CONFIDENCE=0.9   # Higher confidence for shell prefixes
COMMAND_MATCH_CONFIDENCE=0.8    # Higher confidence for known commands
```

### Integration Example
```python
# In main application loop
from src.components.input_router import input_router
from src.components.execution_engine import execution_engine
from src.components.llm_orchestrator import llm_orchestrator

user_input = get_user_input()
decision = input_router.route_input(user_input)

if decision.prediction == "command":
    # Execute shell command
    for output in execution_engine.execute_command(user_input):
        display_output(output)
else:
    # Process as AI prompt
    response = llm_orchestrator.process_prompt(user_input)
    display_response(response)
```

---

## Testing

### Test Coverage
- **57 comprehensive tests** across all algorithms and configurations
- **45 edge case tests** for error handling and robustness
- **100% pass rate** on core functionality

### Test Files

#### `test_input_router.py` - Main Test Suite
- Configuration value verification
- Individual algorithm testing
- Full routing decision testing
- Enhanced functionality validation

#### `test_edge_cases.py` - Edge Case Testing
- Malformed input handling
- Unicode character support
- Configuration resilience
- Performance validation
- Algorithm isolation testing

### Running Tests
```bash
# Main functionality tests
python test_input_router.py

# Edge case and error handling tests
python test_edge_cases.py

# Both test suites
python test_input_router.py && python test_edge_cases.py
```

### Test Examples
```python
# Configuration tests
assert settings.PREFIX_COMMAND_CONFIDENCE == 0.8
assert "sudo" in input_router._known_commands

# Functionality tests
assert input_router.route_input("git status").prediction == "command"
assert input_router.route_input("what is this?").prediction == "prompt"

# Edge case tests
assert input_router.route_input(None).prediction == "prompt"  # None input
assert input_router.route_input("a" * 2000).prediction == "prompt"  # Long input
```

---

## Error Handling

### Comprehensive Error Recovery

#### Input Validation
- **None/Non-string input**: Safely converts or defaults to "prompt"
- **Empty/whitespace input**: Always returns "prompt"
- **Unicode characters**: Properly handled (emoji, accented chars, international text)
- **Extremely long input**: Truncated to 1000 characters for performance
- **Type validation**: Ensures input is converted to string safely

#### Algorithm Isolation
- **Individual failures**: If one algorithm crashes, others continue
- **Graceful degradation**: Failed algorithms contribute neutral confidence (0.0, 0.0)
- **Mathematical validation**: Checks for NaN, infinity, invalid numbers
- **Ultimate fallback**: Always returns valid RouteDecision, never crashes

#### Configuration Resilience
- **Malformed CSV**: Handles invalid comma-separated values gracefully
- **Empty configuration**: Defaults to empty sets, system continues functioning
- **Type errors**: Non-string configs handled without system failure
- **Parse errors**: Individual config failures don't crash entire system

### Error Handling Examples
```python
# These all return valid RouteDecision without crashing:
input_router.route_input(None)           # → RouteDecision("prompt")
input_router.route_input("")             # → RouteDecision("prompt")
input_router.route_input(12345)          # → RouteDecision("prompt")
input_router.route_input("🚀🌟⚡")        # → RouteDecision("prompt")
input_router.route_input("a" * 5000)     # → RouteDecision("prompt")
```

---

## Performance

### Optimization Strategies

#### Data Structure Efficiency
- **O(1) Set Lookups**: All word lists converted to sets for constant-time membership testing
- **Minimal String Operations**: Efficient parsing with early termination
- **Memory Management**: Avoids creating large intermediate objects
- **Lazy Evaluation**: Algorithms only execute when needed

#### Performance Characteristics
- **Response Time**: < 1ms for typical inputs
- **Memory Usage**: ~50KB for configuration data
- **Scalability**: Performance doesn't degrade with larger vocabularies
- **Input Limits**: 1000 character maximum for performance safety

#### Benchmarks
```python
# Performance test results:
"git status"                 # ~0.1ms
"what is this error?"       # ~0.1ms  
"word " * 500               # ~0.1ms (long repetitive)
"a" * 1000                  # ~0.1ms (truncated)
```

---

## Extension Guide

### Adding New Algorithms

1. **Create Algorithm Method**:
```python
def _detect_new_pattern(self, input_str: str) -> tuple[float, float]:
    """
    Created: To detect specific new pattern in user input
    Purpose: Add domain-specific intelligence for routing decisions
    """
    # Your algorithm logic here
    return (command_confidence, prompt_confidence)
```

2. **Add Configuration**:
```python
# In src/config.py
NEW_PATTERN_COMMAND_CONFIDENCE: float = Field(default=0.6, ge=0.0, le=1.0)
NEW_PATTERN_PROMPT_CONFIDENCE: float = Field(default=0.4, ge=0.0, le=1.0)
```

3. **Integrate with Main Logic**:
```python
# In route_input method
try:
    new_cmd_conf, new_prompt_conf = self._detect_new_pattern(cleaned_input)
except Exception:
    new_cmd_conf, new_prompt_conf = 0.0, 0.0

total_command_confidence += new_cmd_conf
total_prompt_confidence += new_prompt_conf
```

### Adding New Languages

1. **Extend Configuration**:
```python
# In .env file
QUESTION_WORDS="what,how,why,help,qué,cómo,por qué,was,wie,warum"
KNOWN_COMMANDS="ls,cd,git,список,директория"  # Add localized commands
```

2. **Language-Specific Patterns**:
```python
# Add language detection algorithm
def _detect_language_patterns(self, input_str: str) -> tuple[float, float]:
    # Language-specific routing logic
    pass
```

### Custom Command Categories

1. **Domain-Specific Commands**:
```python
# DevOps environment
KNOWN_COMMANDS="ls,cd,git,docker,kubectl,terraform,ansible,helm"

# Data Science environment  
KNOWN_COMMANDS="ls,cd,python,jupyter,pandas,numpy,pip,conda"

# Web Development environment
KNOWN_COMMANDS="ls,cd,git,npm,yarn,node,webpack,vite"
```

2. **Custom Confidence Tuning**:
```python
# High precision environment (favor commands)
COMMAND_MATCH_CONFIDENCE=0.9
QUESTION_PROMPT_CONFIDENCE=0.4

# Conversational environment (favor prompts)
COMMAND_MATCH_CONFIDENCE=0.5
QUESTION_PROMPT_CONFIDENCE=0.8
```

---

## Troubleshooting

### Common Issues

#### Wrong Routing Decisions
- **Check confidence values**: Tune via environment variables
- **Verify word lists**: Ensure relevant commands/question words are included
- **Test individual algorithms**: Use test suite to isolate issues

#### Configuration Problems
- **Validate .env syntax**: Ensure proper comma-separated format
- **Check data types**: Configuration values must be proper types
- **Test parsing**: Use `input_router._parse_config_list()` to verify

#### Performance Issues
- **Input length**: Check for extremely long inputs (>1000 chars)
- **Configuration size**: Very large word lists may impact performance
- **Algorithm complexity**: Profile individual algorithms if needed

### Debug Mode
```python
# Enable detailed logging for debugging
router = input_router

# Test individual algorithms
print(f"Prefix: {router._detect_prefixes('git status')}")
print(f"Command: {router._match_commands('git status')}")
print(f"Question: {router._detect_questions('git status')}")
print(f"Structure: {router._analyze_structure('git status')}")

# Inspect configuration
print(f"Shell prefixes: {router._shell_prefixes}")
print(f"Known commands: {router._known_commands}")
```

---

## Development Guidelines

### Code Style
- Follow existing codebase patterns
- Add comprehensive docstrings with "Created:", "Purpose:", "Handles:" sections
- Use type hints throughout
- Implement error handling for all external inputs

### Testing Requirements
- Write tests for any new algorithms
- Include edge cases in test coverage
- Verify performance benchmarks
- Test configuration changes

### Documentation Standards
- Update this README for any architectural changes
- Add inline comments explaining complex logic
- Include usage examples for new features
- Document configuration options

---

## Contributing

When contributing to InputRouter:

1. **Read the Architecture**: Understand the 4-algorithm confidence system
2. **Follow SOLID Principles**: Maintain clean, extensible design
3. **Add Comprehensive Tests**: Test functionality and edge cases
4. **Document Everything**: Clear creation purpose and usage examples
5. **Maintain Performance**: Keep response times under 1ms
6. **Handle Errors Gracefully**: Never crash, always return valid decisions

For questions or contributions, refer to the main project documentation and follow the established patterns in the codebase.

---

**InputRouter**: Intelligent command/prompt classification for Prism Terminal  
**Status**: Production-ready with comprehensive error handling and testing  
**Maintainers**: Prism Terminal Development Team