# Environment Variables

This project uses environment variables for configuration. Copy `.env.sample` to `.env` and adjust the values as needed.

## Available Variables

### Required

- `None`

### Optional

- **`HISTORY_TOKEN_LIMIT`** - Maximum tokens to keep in chat history (default: 50000)

  - Minimum: 10000
  - Maximum: 500000
  - Higher values = longer conversation memory but more API costs

- **`CHARS_PER_TOKEN_RATIO`** - Characters per token ratio for token estimation (default: 4)

  - Range: 2-7
  - Lower values = more conservative token estimates
  - Adjust based on your language/content type

- **`MAX_OUTPUT_SIZE`** — Maximum output size before truncation (default: 8000)

  - Minimum: 1000
  - Maximum: 16000
  - Larger values = larger output allowed before truncation

- **`OUTPUT_KEEP_START_SIZE`** — Number of characters to keep from the start when truncating output (default: 2000)

  - Minimum: 1000
  - Maximum: 5000
  - Adjust to keep important header info

- **`OUTPUT_KEEP_END_SIZE`** — Number of characters to keep from the end when truncating output (default: 4000)

  - Minimum: 1000
  - Maximum: 5000
  - Adjust to keep important trailing info (logs, errors, etc.)

## Setup

1. Copy the sample file:

- ```bash
   cp .env.sample .env
  ```

2. Edit `.env` with your values:

- ```bash
   HISTORY_GEMINI_API_KEY=your_api_key_here
   HISTORY_TOKEN_LIMIT=75000
   HISTORY_CHARS_PER_TOKEN=4
  ```

3. Restart the application to apply changes

## Adding New Variables

To add a new environment variable:

1. Add it to your `.env` file:

   ```bash
   YOUR_NEW_SETTING=value
   ```

2. Update the configuration in `src/config.py`:

   ```python
   your_new_setting: str = Field(default="default_value") # Refer to pydantic-settings documentation for help
   ```

3. Use it in your code:

   ```python
   from src import config
   print(config.your_new_setting)
   ```

4. Update this documentation and `.env.sample`

## Notes

- Environment variables override `.env` file values
- Invalid values will cause the application to exit with an error message
- Keep your `.env` file private - never commit it to version control
