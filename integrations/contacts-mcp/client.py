"""Official MCP SDK transport; no channel access or automatic sending here."""
import json
import os
from contextlib import asynccontextmanager

import httpx2
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client


class ToolError(RuntimeError):
    pass


class Client:
    def __init__(self, session):
        self.session = session

    async def call(self, name, **arguments):
        result = await self.session.call_tool(name, arguments)
        if result.is_error:
            # Never echo server errors: they can contain credentials or private content.
            raise ToolError(f"contacts-mcp tool failed: {name}")
        for block in result.content:
            if block.type == "text":
                return json.loads(block.text)
        raise ToolError(f"contacts-mcp returned no JSON: {name}")


@asynccontextmanager
async def open_client():
    url, token = os.environ.get("CONTACTS_MCP_URL"), os.environ.get("CONTACTS_MCP_TOKEN")
    if not url or not token:
        raise ToolError("Set CONTACTS_MCP_URL and CONTACTS_MCP_TOKEN")
    async with httpx2.AsyncClient(headers={"Authorization": f"Bearer {token}"}, timeout=30) as http:
        async with streamable_http_client(url, http_client=http) as (read, write):
            async with ClientSession(read, write, read_timeout_seconds=30) as session:
                await session.initialize()
                yield Client(session)
