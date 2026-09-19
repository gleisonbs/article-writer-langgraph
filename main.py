import argparse
import asyncio

from clients import SQSQueue, queue_url
from graph import graph, initial_state
from logger import log_success
from nodes import coverage
from schemas import ArticleRequest
from utils import print_article
from worker import run as run_worker


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Write a cited article about a topic.")
    parser.add_argument("topic", nargs="?")
    parser.add_argument("audience", nargs="?")
    parser.add_argument("tone", nargs="?")
    parser.add_argument("target_words", nargs="?", type=int)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument(
        "--push", action="store_true", help="push this request to SQS_INPUT_QUEUE_URL"
    )
    mode.add_argument(
        "--pull",
        action="store_true",
        help="pull requests from SQS_INPUT_QUEUE_URL and run them",
    )
    args = parser.parse_args()

    if args.pull and args.topic:
        parser.error("with --pull, topics come from the queue, not the command line")
    if not args.pull and not args.topic:
        parser.error("a topic is required, unless --pull is set")
    return args


def build_request(args: argparse.Namespace) -> ArticleRequest:
    given = {
        "topic": args.topic,
        "audience": args.audience,
        "tone": args.tone,
        "target_words": args.target_words,
    }
    # anything left out falls back to ArticleRequest's defaults
    return ArticleRequest(**{k: v for k, v in given.items() if v is not None})


async def push_request(request: ArticleRequest) -> None:
    queue = SQSQueue(queue_url("SQS_INPUT_QUEUE_URL"))
    await queue.send(request.model_dump_json())
    log_success(f"Pushed: {request.topic}")


def main() -> None:
    args = parse_args()
    if args.pull:
        asyncio.run(run_worker())
        return

    request = build_request(args)
    if args.push:
        asyncio.run(push_request(request))
        return

    state = initial_state(request)
    result = graph.invoke(state)  # type: ignore
    print_article(result, coverage(result))  # type: ignore


if __name__ == "__main__":
    main()
