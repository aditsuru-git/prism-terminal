from pydantic_settings import BaseSettings
from pydantic import Field, model_validator


class Config(BaseSettings):
    HISTORY_TOKEN_LIMIT: int = Field(
        50000,
        ge=10000,
        le=500000,
        description="Token limit must be between 10K and 500K",
    )

    MAX_OUTPUT_SIZE: int = Field(
        8000,
        ge=2000,
        le=16000,
        description="Max output size must be between 2k and 16k",
    )

    OUTPUT_KEEP_START_SIZE: int = Field(
        2000,
        ge=1000,
        le=5000,
        description="'OUTPUT_KEEP_START_SIZE' must be between 1k and 5k",
    )

    OUTPUT_KEEP_END_SIZE: int = Field(
        4000,
        ge=1000,
        le=5000,
        description="'OUTPUT_KEEP_END_SIZE' must be between 1k and 5k",
    )

    CHARS_PER_TOKEN_RATIO: int = Field(
        default=4,
        ge=2,
        le=7,
        description="Characters per token for estimation must be between 2 and 7",
    )

    @model_validator(mode="after")
    def output_truncation_config(self):
        if (
            self.OUTPUT_KEEP_START_SIZE + self.OUTPUT_KEEP_END_SIZE
            > self.MAX_OUTPUT_SIZE
        ):
            raise ValueError(
                "sum of OUTPUT_KEEP_START_SIZE' and 'OUTPUT_KEEP_END_SIZE' must not exceed the max output size."
            )
        return self

    model_config = {
        "env_file": ".env",
    }


settings = Config()  # Ignore the IntelliSense error (if any)
