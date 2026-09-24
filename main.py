import asyncio

from cli import build_request, parse_args
from review import run_until_done
from runner import start_or_resume
from utils import print_report
from worker import push_request
from worker import run as run_worker


def main():
    args = parse_args()
    if args.pull:
        asyncio.run(run_worker())
        return

    request = build_request(args)
    if args.push:
        asyncio.run(push_request(request))
        return

    thread, topic = args.thread, args.topic
    config = {"configurable": {"thread_id": thread}}

    state = start_or_resume(request, topic, config)
    state = run_until_done(state, thread, config)

    print_report(state)


if __name__ == "__main__":
    main()
