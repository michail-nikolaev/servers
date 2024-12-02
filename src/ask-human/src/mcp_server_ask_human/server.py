import logging
from enum import Enum
from time import sleep
from typing import List

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    TextContent,
    Tool,
)
from pydantic import BaseModel


class AskHuman(BaseModel):
    question: str

class HumanTools(str, Enum):
    ASK_HUMAN = "ask_human"


def ask_human(question: str) -> str:
    return "hello, I am human!, you question is: {}".format(question)


async def serve() -> None:
    logger = logging.getLogger(__name__)

    server = Server("ask-human")

    @server.list_tools()
    async def list_tools() -> list[Tool]:
        return [
            Tool(
                name=HumanTools.ASK_HUMAN,
                description="Ask any question to real human",
                inputSchema=AskHuman.schema(),
            )
        ]

    @server.call_tool()
    async def call_tool(name: str, arguments: dict) -> List[TextContent]:
        context = server.request_context
        match name:
            case HumanTools.ASK_HUMAN:
                status = ask_human(arguments["question"])
                progress_token = None

                if context.meta and (progress_token := context.meta.progressToken):
                    # Send progress notifications
                    await context.session.send_progress_notification(
                        progress_token=progress_token,
                        progress=0.5,
                        total=1.0
                    )

                # TODO: here we need to open window to ask user

                if progress_token:
                    await context.session.send_progress_notification(
                        progress_token=progress_token,
                        progress=1.0,
                        total=1.0
                    )

                return [TextContent(
                    type="text",
                    text=f"Human answer:\n{status}"
                )]
            case _:
                raise ValueError(f"Unknown tool: {name}")

    options = server.create_initialization_options()
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, options, raise_exceptions=True)


if __name__ == "__main__":
    import asyncio

    asyncio.run(serve())
