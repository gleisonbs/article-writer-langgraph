import asyncio
import os
import signal
import sys
import traceback
from collections.abc import Awaitable, Callable

import boto3

from logger import log_error, log_warning

POLL_WAIT = 20  # long polling; the most SQS allows


def queue_url(env_var: str) -> str:
    url = os.environ.get(env_var)
    if not url:
        raise SystemExit(f"{env_var} is not set; add it to .env")
    return url


def _stop_now(sig: int) -> None:
    # exit at once instead of waiting for the message in progress, which can take
    # minutes; SQS redelivers it once its visibility timeout (set on the queue) runs out
    log_warning("Worker stopped")
    sys.stdout.flush()
    os._exit(128 + sig)


class SQSQueue:
    """An SQS queue, consumed one message at a time.

    A message is deleted once handling succeeds, and left on the queue, for SQS
    to redeliver once its visibility timeout runs out, if handling raises.
    """

    def __init__(self, url: str):
        self.url = url
        self._client = boto3.client("sqs")

    async def consume(self, handle: Callable[[str], Awaitable[None]]) -> None:
        loop = asyncio.get_running_loop()
        for sig in (signal.SIGINT, signal.SIGTERM):
            loop.add_signal_handler(sig, _stop_now, sig)

        while True:
            for message in await self._receive():
                await self._handle_one(message, handle)

    async def _handle_one(
        self, message: dict, handle: Callable[[str], Awaitable[None]]
    ) -> None:
        message_id, receipt = message["MessageId"], message["ReceiptHandle"]
        try:
            await handle(message["Body"])
            await self._delete(receipt)
        except Exception:  # noqa: BLE001
            log_error(f"Message {message_id} failed, leaving it on the queue")
            traceback.print_exc()

    async def _receive(self) -> list[dict]:
        response = await asyncio.to_thread(
            self._client.receive_message,
            QueueUrl=self.url,
            MaxNumberOfMessages=1,
            WaitTimeSeconds=POLL_WAIT,
        )
        return response.get("Messages", [])

    async def _delete(self, receipt: str) -> None:
        await asyncio.to_thread(
            self._client.delete_message, QueueUrl=self.url, ReceiptHandle=receipt
        )

    async def send(self, body: str) -> None:
        await asyncio.to_thread(
            self._client.send_message, QueueUrl=self.url, MessageBody=body
        )
