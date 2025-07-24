from src.models import ExitCode
from src import settings


class OutputProcessor:
    MAX_SIZE = settings.MAX_OUTPUT_SIZE
    KEEP_START = settings.OUTPUT_KEEP_START_SIZE
    KEEP_END = settings.OUTPUT_KEEP_END_SIZE

    def process_output(self, output: str, exit_code: ExitCode) -> str:
        # If command failed, always return full output (preserve errors)
        if exit_code.exit_code != 0:
            return output

        # If output is small enough, return as-is
        if len(output) <= self.MAX_SIZE:
            return output

        # Apply intelligent truncation
        start_part = output[: self.KEEP_START]
        end_part = output[-self.KEEP_END :]
        middle_size = len(output) - self.KEEP_START - self.KEEP_END

        truncated = (
            f"{start_part}\n"
            f"\n... [truncated {middle_size} characters] ...\n\n"
            f"{end_part}"
        )

        return truncated


output_processor = OutputProcessor()
