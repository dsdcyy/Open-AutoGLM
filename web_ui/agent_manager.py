import asyncio
import io
import sys
from typing import Callable, Optional
from phone_agent import PhoneAgent
from phone_agent.model import ModelConfig
from phone_agent.agent import AgentConfig


class WebAgentManager:
    def __init__(self):
        self.agent: Optional[PhoneAgent] = None
        self.log_callback: Optional[Callable[[str], None]] = None
        self.step_callback: Optional[Callable[[dict], None]] = None
        self.is_running = False

    def set_log_callback(self, callback: Callable[[str], None]):
        self.log_callback = callback

    def set_step_callback(self, callback: Callable[[dict], None]):
        self.step_callback = callback

    def log(self, message: str):
        if self.log_callback:
            self.log_callback(message)
        # Avoid infinite recursion if sys.stdout is redirected
        sys.__stdout__.write(message + "\n")
        sys.__stdout__.flush()

    def on_agent_step(self, result):
        if self.step_callback:
            # Format event for frontend
            event = {
                "type": "step",
                "action": result.action.get("action") if result.action else "None",
                "screenshot": result.screenshot_base64,
            }
            self.step_callback(event)

    def initialize_agent(
        self, base_url: str, model: str, apikey: str, lang: str = "cn"
    ):
        model_config = ModelConfig(
            base_url=base_url,
            api_key=apikey,
            model_name=model,
        )
        agent_config = AgentConfig(lang=lang, verbose=True)
        self.agent = PhoneAgent(
            model_config=model_config,
            agent_config=agent_config,
            # We can implement web-based callbacks later if needed
            confirmation_callback=lambda msg: True,
            takeover_callback=lambda msg: self.log(f"Takeover requested: {msg}"),
            step_callback=self.on_agent_step,
        )
        self.log(f"Agent initialized with model: {model}")

    async def run_task(self, task: str):
        if not self.agent:
            self.log("Error: Agent not initialized.")
            return

        self.is_running = True
        self.log(f"Starting task: {task}")

        # Capture stdout to redirect "Thinking" logs to web client
        # This is a bit of a hack because PhoneAgent prints to stdout

        class StreamToLogger(io.StringIO):
            def __init__(self, logger_func):
                super().__init__()
                self.logger_func = logger_func

            def write(self, buf):
                # Don't strip! Spaces are important for streaming tokens.
                # Only ignore completely empty writes if any
                if buf:
                    self.logger_func(buf)
                return super().write(buf)

        old_stdout = sys.stdout
        sys.stdout = StreamToLogger(self.log)

        try:
            # Run the synchronous agent.run in a thread pool to be async-friendly
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(None, self.agent.run, task)
            self.log(f"Task Finished. Result: {result}")
        except Exception as e:
            self.log(f"Task Failed: {str(e)}")
        finally:
            sys.stdout = old_stdout
            self.is_running = False

    def cancel_task(self):
        """Cancel the ongoing task."""
        if self.agent and self.is_running:
            self.agent.stop()
            self.log("Task cancellation requested...")


agent_manager = WebAgentManager()
