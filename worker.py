import asyncio

from clients import SQSQueue, queue_url
from graph import graph, initial_state
from logger import log_header, log_info
from schemas import ArticleRequest


async def process_request(body: str) -> None:
    request = ArticleRequest.model_validate_json(body)
    log_info(f"Request: {request.topic}")
    await asyncio.to_thread(graph.invoke, initial_state(request))  # type: ignore


async def run() -> None:
    queue = SQSQueue(queue_url("SQS_INPUT_QUEUE_URL"))
    log_header("Waiting for Requests")
    log_info(f"Listening on {queue.url}")
    await queue.consume(process_request)
