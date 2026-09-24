import argparse

from schemas import ArticleRequest


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Write a cited article about a topic.")
    parser.add_argument("--thread", nargs="?")
    parser.add_argument("--topic", nargs="?")
    parser.add_argument("--audience", nargs="?")
    parser.add_argument("--tone", nargs="?")
    parser.add_argument("--target_words", nargs="?", type=int)
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
    if not args.pull and not args.topic and not args.thread:
        parser.error("a topic is required, unless --pull is set or --thread is provided")
    return args


def build_request(args: argparse.Namespace) -> ArticleRequest:
    given = {
        "topic": args.topic,
        "audience": args.audience,
        "tone": args.tone,
        "target_words": args.target_words,
    }

    return ArticleRequest(**{k: v for k, v in given.items() if v is not None})
