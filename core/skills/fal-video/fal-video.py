#!/usr/bin/env python3
"""Restricted fal MCP client for allowlisted video endpoints. Never exposes unrestricted image/model execution.

Usage (from the repo root):
  .venv/bin/python core/skills/fal-video/fal-video.py schema  --endpoint ENDPOINT
  .venv/bin/python core/skills/fal-video/fal-video.py pricing --endpoint ENDPOINT
  .venv/bin/python core/skills/fal-video/fal-video.py submit  --endpoint ENDPOINT --input raw/INPUT.json --approve-spend
  .venv/bin/python core/skills/fal-video/fal-video.py status|result|cancel --endpoint ENDPOINT --request-id ID

FAL_KEY is read from the repo-root .env. See core/skills/fal-video/SKILL.md.
"""
import argparse
import asyncio
import json
import os
from pathlib import Path
from dotenv import load_dotenv
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client
from mcp.shared._httpx_utils import create_mcp_http_client

ROOT = Path(__file__).resolve().parents[3]  # repo root: core/skills/fal-video/ is three levels down
ENDPOINTS = {
    "bytedance/seedance-2.5/image-to-video",
    "bytedance/seedance-2.5/reference-to-video",
    "bytedance/seedance-2.5/text-to-video",
    "bytedance/seedance-2.0/image-to-video",
    "bytedance/seedance-2.0/reference-to-video",
    "bytedance/seedance-2.0/text-to-video",
    "bytedance/seedance-2.0/fast/image-to-video",
    "fal-ai/kling-video/v2.6/pro/image-to-video",
    "fal-ai/kling-video/v3/turbo/pro/image-to-video",
    "fal-ai/kling-video/lipsync/audio-to-video",
    "fal-ai/bytedance/omnihuman",
    "fal-ai/wan-i2v",
}
TOOLS = {"schema": "get_model_schema", "pricing": "get_pricing", "submit": "submit_job", "status": "check_job", "result": "get_job_result", "cancel": "cancel_job"}

def validate(action, endpoint, approved=False):
    if endpoint not in ENDPOINTS:
        raise ValueError("Blocked: endpoint is not in the verified video-only allowlist. Stills follow core/skills/image-prompt/SKILL.md.")
    if action == "submit" and not approved:
        raise ValueError("Submission requires --approve-spend after reviewing current pricing and reference-upload consent.")

async def invoke(action, endpoint, input_path=None, request_id=None, approved=False):
    validate(action, endpoint, approved)
    # A long-running Pi process may still carry the original empty placeholder.
    # Refresh only when no usable explicit environment value is present.
    load_dotenv(ROOT / ".env", override=not bool(os.environ.get("FAL_KEY")))
    key = os.environ.get("FAL_KEY")
    if not key:
        raise ValueError("BLOCKED: FAL_KEY missing. Add it privately to the repo-root .env.")
    args = {"endpoint_id": endpoint}
    if action == "submit":
        if not input_path:
            raise ValueError("--input JSON file required; obtain live schema first")
        args["input"] = json.loads(Path(input_path).read_text())
    if action in ("status", "result", "cancel"):
        if not request_id:
            raise ValueError("--request-id required")
        args["request_id"] = request_id
    async with create_mcp_http_client(headers={"Authorization": f"Bearer {key}"}) as client:
        async with streamable_http_client("https://mcp.fal.ai/mcp", http_client=client) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                result = await session.call_tool(TOOLS[action], args)
                print(result.model_dump_json())
                if result.is_error:
                    raise ValueError("fal returned a tool error; see result above")

def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("action", choices=TOOLS)
    parser.add_argument("--endpoint", default="bytedance/seedance-2.5/image-to-video")
    parser.add_argument("--input")
    parser.add_argument("--request-id")
    parser.add_argument("--approve-spend", action="store_true")
    args = parser.parse_args()
    try:
        asyncio.run(asyncio.wait_for(invoke(args.action, args.endpoint, args.input, args.request_id, args.approve_spend), timeout=90))
    except (ValueError, TimeoutError) as error:
        parser.exit(2, f"{error}\n")

if __name__ == "__main__":
    main()
