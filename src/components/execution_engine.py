from typing import Iterator
from src.models import ExitCode
import subprocess


class ExecutionEngine:
    def execute_command(self, command: str) -> Iterator[str | ExitCode]:
        process = subprocess.Popen(
            command,
            bufsize=1,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            shell=True,
            text=True,
        )

        try:
            if process.stdout is not None:
                while True:
                    stream = process.stdout.readline()
                    if stream:
                        yield stream
                    elif process.poll() is not None:
                        break
            exit_code = (
                ExitCode(exit_code=0)
                if process.returncode == 0
                else ExitCode(exit_code=1)
            )
            yield exit_code
        except KeyboardInterrupt:
            try:
                process.terminate()
                process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()
            if process.stdout is not None:
                remaining_stream = process.stdout.read()
                if remaining_stream:
                    yield remaining_stream
            yield "^C\nProcess interrupted by user (Ctrl+C)\n"
            yield ExitCode(exit_code=1)


execution_engine = ExecutionEngine()
