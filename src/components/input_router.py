from src.models.core_models import RouteDecision
from src import settings  # Import configuration settings for confidence values
from typing import Set
import os
import platform


class InputRouter:
    def __init__(self):
        # Parse comma-separated configuration strings into sets for efficient lookup
        # Created: To replace hard-coded word lists with configurable settings
        # Purpose: Enable customization without code changes, support different languages/shells
        # Benefit: Users can extend via environment variables or .env file
        
        # Detect current platform and shell for enhanced compatibility
        self._platform = platform.system().lower()  # 'windows', 'darwin', 'linux'
        self._shell_name = self._detect_shell()
        self._is_windows = self._platform == 'windows'
        self._is_powershell = self._shell_name == 'powershell'
        
        # Configure shell prefixes based on platform and shell
        base_prefixes = settings.SHELL_PREFIXES
        if self._is_windows and settings.ENABLE_SHELL_DETECTION:
            base_prefixes = settings.WINDOWS_SHELL_PREFIXES
            
        self._shell_prefixes: Set[str] = self._parse_config_list(base_prefixes)
        # Converts "!,$,>" → {"!", "$", ">"} for O(1) membership testing
        
        self._known_commands: Set[str] = self._parse_config_list(
            settings.KNOWN_COMMANDS
        )
        # Converts "ls,cd,pwd,git,..." → {"ls", "cd", "pwd", "git", ...} for command detection
        
        # PowerShell cmdlet prefixes for enhanced detection
        self._powershell_prefixes: Set[str] = self._parse_config_list(
            settings.POWERSHELL_CMDLET_PREFIXES
        ) if settings.ENABLE_SHELL_DETECTION else set()
        
        self._question_words: Set[str] = self._parse_config_list(
            settings.QUESTION_WORDS
        )
        # Converts "what,how,why,..." → {"what", "how", "why", ...} for question pattern detection
        
        self._articles: Set[str] = self._parse_config_list(
            settings.SENTENCE_ARTICLES
        )
        # Converts "a,an,the,..." → {"a", "an", "the", ...} for sentence structure analysis

    def _parse_config_list(self, config_string: str) -> Set[str]:
        """
        Parse comma-separated configuration string into a set of lowercase strings.
        
        Created: To convert configuration strings like "ls,cd,pwd" into sets for efficient lookup
        Purpose: Enables O(1) membership testing instead of O(n) list iteration
        Handles: Empty strings, whitespace, case normalization, malformed input
        
        Args:
            config_string: Comma-separated values like "git,npm,python"
        Returns:
            Set of lowercase strings: {"git", "npm", "python"}
        
        Edge Cases Handled:
        - None/empty input → empty set
        - Whitespace-only items → filtered out
        - Mixed case → normalized to lowercase
        - Leading/trailing spaces → stripped
        - Special characters → preserved (for prefixes like "!")
        """
        try:
            if not config_string or not isinstance(config_string, str):
                return set()
            
            if not config_string.strip():
                return set()
            
            # Parse and clean items
            items = set()
            for item in config_string.split(","):
                cleaned_item = item.strip()
                if cleaned_item:  # Skip empty items after stripping
                    # Normalize to lowercase but preserve special characters
                    items.add(cleaned_item.lower())
            
            return items
            
        except (AttributeError, TypeError, ValueError) as e:
            # Graceful degradation: return empty set on any parsing error
            # This prevents the entire InputRouter from failing due to config issues
            return set()

    def _detect_shell(self) -> str:
        """
        Detect the current shell environment for platform-specific optimizations.
        
        Created: To enable shell-specific command detection and prefix handling
        Purpose: Improve accuracy by adapting to different shell environments
        Returns: Shell name as string ('powershell', 'cmd', 'bash', 'zsh', 'fish', 'unknown')
        """
        try:
            # Check for PowerShell-specific environment variables
            if os.getenv('PSModulePath') or os.getenv('POWERSHELL_DISTRIBUTION_CHANNEL'):
                return 'powershell'
            
            # Check SHELL environment variable (Unix-like systems)
            shell_env = os.getenv('SHELL', '').lower()
            if 'powershell' in shell_env or 'pwsh' in shell_env:
                return 'powershell'
            elif 'bash' in shell_env:
                return 'bash'
            elif 'zsh' in shell_env:
                return 'zsh'
            elif 'fish' in shell_env:
                return 'fish'
            elif 'cmd' in shell_env or platform.system().lower() == 'windows':
                return 'cmd'
            
            # Check parent process name (fallback)
            parent_name = os.getenv('_', '').lower()
            if any(shell in parent_name for shell in ['powershell', 'pwsh']):
                return 'powershell'
            elif any(shell in parent_name for shell in ['bash', 'zsh', 'fish']):
                return parent_name.split('/')[-1] if '/' in parent_name else 'bash'
                
            return 'unknown'
        except Exception:
            return 'unknown'

    def route_input(self, user_input: str) -> RouteDecision:
        """
        Route user input to either command execution or prompt processing.
        
        Created: Main entry point for InputRouter with comprehensive error handling
        Purpose: Safely classify input while gracefully handling edge cases
        Handles: All input validation, sanitization, and error recovery
        
        Args:
            user_input: Raw user input string
        Returns:
            RouteDecision with prediction "command" or "prompt"
            
        Edge Cases Handled:
        - None input → defaults to "prompt"
        - Empty/whitespace-only → defaults to "prompt"  
        - Non-string input → converts to string safely
        - Extremely long input → truncated for performance
        - Special characters → preserved and processed correctly
        - Unicode characters → handled properly
        """
        try:
            # Input validation and sanitization
            # Created: To handle malformed or dangerous input safely
            # Purpose: Prevent crashes and ensure consistent behavior
            
            if user_input is None:
                return RouteDecision(prediction="prompt")
            
            # Convert to string safely (handles non-string input)
            if not isinstance(user_input, str):
                try:
                    user_input = str(user_input)
                except (TypeError, ValueError):
                    return RouteDecision(prediction="prompt")
            
            # Handle empty or whitespace-only input
            if not user_input or not user_input.strip():
                return RouteDecision(prediction="prompt")
            
            # Truncate extremely long input for performance
            # Created: To prevent performance issues with very long strings
            # Limit: 1000 characters should be sufficient for any reasonable command/prompt
            MAX_INPUT_LENGTH = 1000
            if len(user_input) > MAX_INPUT_LENGTH:
                user_input = user_input[:MAX_INPUT_LENGTH]
            
            cleaned_input = user_input.strip()
            
            # Execute algorithms with error handling
            # Created: To ensure individual algorithm failures don't crash the entire routing
            # Purpose: Graceful degradation - if one algorithm fails, others continue working
            # Fallback: Default to neutral confidence (0.0, 0.0) on algorithm failure
            
            try:
                prefix_cmd_conf, prefix_prompt_conf = self._detect_prefixes(cleaned_input)
            except Exception:
                prefix_cmd_conf, prefix_prompt_conf = 0.0, 0.0
            
            try:
                cmd_dict_cmd_conf, cmd_dict_prompt_conf = self._match_commands(cleaned_input)
            except Exception:
                cmd_dict_cmd_conf, cmd_dict_prompt_conf = 0.0, 0.0
            
            try:
                question_cmd_conf, question_prompt_conf = self._detect_questions(cleaned_input)
            except Exception:
                question_cmd_conf, question_prompt_conf = 0.0, 0.0
            
            try:
                struct_cmd_conf, struct_prompt_conf = self._analyze_structure(cleaned_input)
            except Exception:
                struct_cmd_conf, struct_prompt_conf = 0.0, 0.0
            
            # Calculate total confidence scores with validation
            # Created: To handle potential floating-point issues and ensure valid results
            # Purpose: Prevent NaN, infinity, or invalid confidence values
            
            try:
                total_command_confidence = (
                    prefix_cmd_conf + cmd_dict_cmd_conf + 
                    question_cmd_conf + struct_cmd_conf
                )
                total_prompt_confidence = (
                    prefix_prompt_conf + cmd_dict_prompt_conf + 
                    question_prompt_conf + struct_prompt_conf
                )
                
                # Validate confidence values are finite numbers
                if not (
                    all(isinstance(x, (int, float)) and not (x != x or x == float('inf') or x == float('-inf')) 
                        for x in [total_command_confidence, total_prompt_confidence])
                ):
                    # Fallback to default if invalid confidence values
                    return RouteDecision(prediction="prompt")
                
                # Make routing decision with tie-breaking
                # Created: To handle exact ties consistently
                # Tie-breaking: Default to "prompt" when confidences are equal
                if total_command_confidence > total_prompt_confidence:
                    prediction = "command"
                elif total_prompt_confidence > total_command_confidence:
                    prediction = "prompt"
                else:
                    # Exact tie - default to prompt for safety
                    prediction = "prompt"
                
                return RouteDecision(prediction=prediction)
                
            except (TypeError, ValueError, OverflowError, ArithmeticError):
                # Handle any mathematical errors in confidence calculation
                return RouteDecision(prediction="prompt")
        
        except Exception:
            # Ultimate fallback: if anything goes wrong, default to prompt
            # Created: To ensure InputRouter never crashes regardless of input
            # Purpose: System stability - terminal should always remain functional
            return RouteDecision(prediction="prompt")

    def _detect_prefixes(self, input_str: str) -> tuple[float, float]:
        first_char = input_str[0] if input_str else ""
        
        if first_char in self._shell_prefixes:
            # Shell prefix detected: high command confidence, low prompt confidence
            return (settings.PREFIX_COMMAND_CONFIDENCE, settings.PREFIX_PROMPT_CONFIDENCE)
        else:
            # No shell prefix: reverse the confidence (favor prompts)
            return (settings.PREFIX_PROMPT_CONFIDENCE, settings.PREFIX_COMMAND_CONFIDENCE)

    def _match_commands(self, input_str: str) -> tuple[float, float]:
        words = input_str.split()
        if not words:
            # No words: default to favoring prompts over commands
            return (settings.COMMAND_NO_MATCH_CONFIDENCE, settings.COMMAND_MATCH_CONFIDENCE)
        
        first_word = words[0]
        
        # Apply case-insensitive matching if enabled (important for Windows)
        if settings.CASE_INSENSITIVE_MATCHING:
            first_word_lower = first_word.lower()
        else:
            first_word_lower = first_word
        
        # Check against known commands
        if first_word_lower in self._known_commands:
            # Known command detected: high command confidence, low prompt confidence
            return (settings.COMMAND_MATCH_CONFIDENCE, settings.COMMAND_NO_MATCH_CONFIDENCE)
        
        # Enhanced PowerShell cmdlet detection
        if self._is_powershell and settings.ENABLE_SHELL_DETECTION:
            # Check for PowerShell cmdlet patterns (Verb-Noun)
            if '-' in first_word and len(first_word.split('-')) == 2:
                verb_part = first_word.split('-')[0] + '-'
                if verb_part in self._powershell_prefixes:
                    # PowerShell cmdlet detected: high command confidence
                    return (settings.COMMAND_MATCH_CONFIDENCE, settings.COMMAND_NO_MATCH_CONFIDENCE)
        
        # Check for Windows executable extensions if on Windows
        if self._is_windows and settings.ENABLE_SHELL_DETECTION:
            # Check for common executable extensions
            if any(first_word.lower().endswith(ext) for ext in ['.exe', '.bat', '.cmd', '.ps1', '.msi']):
                return (settings.COMMAND_MATCH_CONFIDENCE, settings.COMMAND_NO_MATCH_CONFIDENCE)
        
        # Unknown command: favor prompts over commands
        return (settings.COMMAND_NO_MATCH_CONFIDENCE, settings.COMMAND_MATCH_CONFIDENCE)

    def _detect_questions(self, input_str: str) -> tuple[float, float]:
        lower_input = input_str.lower()
        
        # Check for question words
        has_question_word = any(
            word in lower_input.split() for word in self._question_words
        )
        
        # Check for question mark
        has_question_mark = "?" in input_str
        
        # Check for conversational patterns (starting with question words)
        words = lower_input.split()
        starts_with_question = bool(words and words[0] in self._question_words)
        
        if has_question_word or has_question_mark or starts_with_question:
            # Question patterns detected: favor prompts over commands
            return (settings.QUESTION_COMMAND_CONFIDENCE, settings.QUESTION_PROMPT_CONFIDENCE)
        else:
            # No question patterns: favor commands over prompts
            return (settings.QUESTION_PROMPT_CONFIDENCE, settings.QUESTION_COMMAND_CONFIDENCE)

    def _analyze_structure(self, input_str: str) -> tuple[float, float]:
        words = input_str.lower().split()
        
        # Check for articles (indicates sentence-like structure)
        has_articles = any(word in self._articles for word in words)
        
        # Check for proper punctuation (complete sentences)
        ends_with_punctuation = bool(
            input_str.strip() and input_str.strip()[-1] in ".!?"
        )
        
        # Check for multiple words (sentences tend to be longer)
        is_multi_word = len(words) > 2
        
        # Check for capitalization (proper grammar)
        has_proper_capitalization = bool(
            input_str and input_str[0].isupper()
        )
        
        sentence_indicators = sum([
            has_articles, ends_with_punctuation, 
            is_multi_word, has_proper_capitalization
        ])
        
        # More sentence-like indicators = higher prompt confidence
        if sentence_indicators >= 2:
            # Sentence-like structure detected: favor prompts over commands
            return (settings.SENTENCE_COMMAND_CONFIDENCE, settings.SENTENCE_PROMPT_CONFIDENCE)
        else:
            # Command-like structure: favor commands over prompts
            return (settings.SENTENCE_PROMPT_CONFIDENCE, settings.SENTENCE_COMMAND_CONFIDENCE)


input_router = InputRouter()