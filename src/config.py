from pydantic_settings import BaseSettings
from pydantic import Field


class Config(BaseSettings):
    HISTORY_TOKEN_LIMIT: int = Field(
        50000,
        ge=10000,
        le=500000,
        description="Token limit must be between 10K and 500K",
    )

    CHARS_PER_TOKEN_RATIO: int = Field(
        default=4,
        ge=2,
        le=7,
        description="Characters per token for estimation must be between 2 and 7",
    )

    # InputRouter confidence values
    PREFIX_COMMAND_CONFIDENCE: float = Field(
        default=0.8,
        ge=0.0,
        le=1.0,
        description="Confidence boost for shell prefixes (!, $, >) indicating commands",
    )
    PREFIX_PROMPT_CONFIDENCE: float = Field(
        default=0.1,
        ge=0.0,
        le=1.0,
        description="Confidence for prompts when shell prefixes are not detected",
    )
    
    COMMAND_MATCH_CONFIDENCE: float = Field(
        default=0.7,
        ge=0.0,
        le=1.0,
        description="Confidence boost when first word matches known commands",
    )
    COMMAND_NO_MATCH_CONFIDENCE: float = Field(
        default=0.2,
        ge=0.0,
        le=1.0,
        description="Confidence for prompts when command dictionary doesn't match",
    )
    
    QUESTION_PROMPT_CONFIDENCE: float = Field(
        default=0.6,
        ge=0.0,
        le=1.0,
        description="Confidence boost for prompts with question patterns",
    )
    QUESTION_COMMAND_CONFIDENCE: float = Field(
        default=0.1,
        ge=0.0,
        le=1.0,
        description="Confidence for commands when question patterns detected",
    )
    
    SENTENCE_PROMPT_CONFIDENCE: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="Confidence for prompts with sentence-like structure",
    )
    SENTENCE_COMMAND_CONFIDENCE: float = Field(
        default=0.3,
        ge=0.0,
        le=1.0,
        description="Confidence for commands with sentence-like structure",
    )

    # InputRouter configurable word lists and patterns
    # Created: To make InputRouter extensible and allow customization of detection patterns
    # Purpose: Enable users to add/remove shell prefixes, commands, and question words without code changes
    # Benefit: Makes the system adaptable to different shells, languages, and use cases
    
    SHELL_PREFIXES: str = Field(
        default="!,$,>",
        description="Comma-separated shell prefixes that indicate commands (e.g., '!,#,$,>')",
    )
    # Usage: Detects command prefixes like !clear, $whoami, >output.txt
    # Customizable: Users can add # for comments, @ for decorators, etc.
    
    KNOWN_COMMANDS: str = Field(
        default="ls,cd,pwd,git,python,npm,curl,grep,cat,mkdir,rm,cp,mv,chmod,sudo,dir,type,copy,del,md,rd,cls,echo,find,fc,more,sort,tree,attrib,cacls,diskpart,format,fsutil,icacls,robocopy,sfc,systeminfo,tasklist,taskkill,wmic,powershell,Get-ChildItem,Get-Location,Set-Location,Get-Content,Set-Content,New-Item,Remove-Item,Copy-Item,Move-Item,Get-Process,Stop-Process,Get-Service,Start-Service,Stop-Service,docker,kubectl,terraform,ansible,vagrant,brew,apt,yum,dnf,pacman,zypper,emerge,pip,conda,node,java,javac,gcc,make,cmake,ninja,cargo,rustc,go",
        description="Comma-separated list of known shell commands for dictionary matching (cross-platform)",
    )
    # Usage: First word matching boosts command confidence (e.g., 'git status' → command)
    # Extensible: Add docker,kubectl,terraform for DevOps, or python3,node,java for development
    
    QUESTION_WORDS: str = Field(
        default="what,how,why,help,can,could,would,should,where,when,which,who",
        description="Comma-separated question words that indicate prompts/conversations",
    )
    # Usage: Presence of these words boosts prompt confidence (e.g., 'what is this?' → prompt)
    # Multilingual: Can add que,como,por que for Spanish, or was,wie,warum for German
    
    SENTENCE_ARTICLES: str = Field(
        default="a,an,the,this,that,these,those",
        description="Comma-separated articles that indicate sentence-like structure",
    )
    # Usage: Articles suggest natural language prompts vs command syntax
    # Grammar-based: Helps distinguish 'Delete the file' (prompt) vs 'rm file' (command)

    # Shell detection and platform-specific settings
    ENABLE_SHELL_DETECTION: bool = Field(
        default=True,
        description="Enable automatic shell and platform detection for better compatibility"
    )
    
    CASE_INSENSITIVE_MATCHING: bool = Field(
        default=True,
        description="Enable case-insensitive command matching (important for Windows)"
    )
    
    # Windows-specific command prefixes and patterns
    WINDOWS_SHELL_PREFIXES: str = Field(
        default="!,$,>,&,|,&&,||",
        description="Windows-specific shell prefixes and operators"
    )
    
    POWERSHELL_CMDLET_PREFIXES: str = Field(
        default="Get-,Set-,New-,Remove-,Add-,Clear-,Copy-,Move-,Start-,Stop-,Test-,Enable-,Disable-,Import-,Export-,Invoke-",
        description="PowerShell cmdlet verb prefixes for enhanced detection"
    )

    model_config = {
        "env_file": ".env",
    }


settings = Config()  # Ignore the IntelliSense error (if any)
