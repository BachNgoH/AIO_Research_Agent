import logging
from typing import Any, Dict, List, Optional

from llama_index.core.callbacks.base_handler import BaseCallbackHandler
from llama_index.core.callbacks.schema import CBEventType, EventPayload

import chainlit as cl
from chainlit import run_sync


logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)


class ChainlitCallback(BaseCallbackHandler):
    """
    AimCallback callback class.

    Args:
        repo (:obj:`str`, optional):
            Aim repository path or Repo object to which Run object is bound.
            If skipped, default Repo is used.
        experiment_name (:obj:`str`, optional):
            Sets Run's `experiment` property. 'default' if not specified.
            Can be used later to query runs/sequences.
        system_tracking_interval (:obj:`int`, optional):
            Sets the tracking interval in seconds for system usage
            metrics (CPU, Memory, etc.). Set to `None` to disable
            system metrics tracking.
        log_system_params (:obj:`bool`, optional):
            Enable/Disable logging of system params such as installed packages,
            git info, environment variables, etc.
        capture_terminal_logs (:obj:`bool`, optional):
            Enable/Disable terminal stdout logging.
        event_starts_to_ignore (Optional[List[CBEventType]]):
            list of event types to ignore when tracking event starts.
        event_ends_to_ignore (Optional[List[CBEventType]]):
            list of event types to ignore when tracking event ends.
    """

    def __init__(
        self,
        event_starts_to_ignore: Optional[List[CBEventType]] = None,
        event_ends_to_ignore: Optional[List[CBEventType]] = None,
    ) -> None:
        
        event_starts_to_ignore = (
            event_starts_to_ignore if event_starts_to_ignore else []
        )
        event_ends_to_ignore = event_ends_to_ignore if event_ends_to_ignore else []
        
        super().__init__(
            event_starts_to_ignore=event_starts_to_ignore,
            event_ends_to_ignore=event_ends_to_ignore,
        )
        
    def on_event_start(
        self,
        event_type: CBEventType,
        payload: Optional[Dict[str, Any]] = None,
        event_id: str = "",
        parent_id: str = "",
        **kwargs: Any,
    ) -> str:
        """
        Args:
            event_type (CBEventType): event type to store.
            payload (Optional[Dict[str, Any]]): payload to store.
            event_id (str): event id to store.
            parent_id (str): parent event id.
        """
        if event_type == CBEventType.FUNCTION_CALL:
            async def run_step():
                async with cl.Step(name=payload[EventPayload.TOOL].name) as step:
                    step.input = f"""
Calling function: {payload[EventPayload.TOOL].name} with parameters {payload[EventPayload.FUNCTION_CALL]}
            
            """        
            run_sync(run_step())
        

    def on_event_end(
        self,
        event_type: CBEventType,
        payload: Optional[Dict[str, Any]] = None,
        event_id: str = "",
        **kwargs: Any,
    ) -> None:
        """
        Args:
            event_type (CBEventType): event type to store.
            payload (Optional[Dict[str, Any]]): payload to store.
            event_id (str): event id to store.
        """

        if event_type == CBEventType.FUNCTION_CALL:
            async def run_step():
                async with cl.Step(name="generating response") as step:
                    step.output = payload["function_call_response"]
        
            run_sync(run_step())


    def start_trace(self, trace_id: Optional[str] = None) -> None:
        pass

    def end_trace(
        self,
        trace_id: Optional[str] = None,
        trace_map: Optional[Dict[str, List[str]]] = None,
    ) -> None:
        pass