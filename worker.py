import asyncio
from uuid import uuid4

from clients import SQSQueue, queue_url
from graph import get_initial_state
from logger import log_header, log_info, log_success
from runner import resume_until_done
from runner import run as run_graph
from schemas import ArticleRequest


def run_to_completion(request: ArticleRequest) -> None:
    """Run one request on its own thread, auto-approving the outline as proposed."""
    config = {"configurable": {"thread_id": str(uuid4())}}
    state = run_graph(get_initial_state(request), config)
    resume_until_done(state, config, lambda _state: None)


async def process_request(body: str) -> None:
    request = ArticleRequest.model_validate_json(body)
    log_info(f"Request: {request.topic}")
    await asyncio.to_thread(run_to_completion, request)


async def push_request(request: ArticleRequest) -> None:
    queue = SQSQueue(queue_url("SQS_INPUT_QUEUE_URL"))
    await queue.send(request.model_dump_json())
    log_success(f"Pushed: {request.topic}")


async def run() -> None:
    queue = SQSQueue(queue_url("SQS_INPUT_QUEUE_URL"))
    log_header("Waiting for Requests")
    log_info(f"Listening on {queue.url}")
    await queue.consume(process_request)
