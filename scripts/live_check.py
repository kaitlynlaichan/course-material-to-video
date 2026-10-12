"""
live_check.py — start the MCP server the way a Claude app does and call every tool.

Uses the network and a little quota (0 if the search is already cached).
Run: .venv/bin/python scripts/live_check.py
"""

import asyncio
from pathlib import Path

from mcp import Client, StdioServerParameters

ROOT = Path(__file__).resolve().parent.parent

CALLS = [
    ("search_videos", {"query": "eigenvalues and eigenvectors", "max_results": 3}),
    ("find_in_transcript", {"video_id": "PFDu9oVAE-g", "terms": ["eigenbasis"], "context_lines": 1}),
    ("get_transcript", {"video_id": "PFDu9oVAE-g", "start_seconds": 180, "end_seconds": 190}),
    ("quota_status", {}),
    ("get_transcript", {"video_id": "not-an-id"}),  # should fail with a clear reason
]


async def main():
    params = StdioServerParameters(command=str(ROOT / ".venv/bin/python"), args=["-m", "cmv.server"],
                                   cwd=str(ROOT), env={"PYTHONPATH": str(ROOT)})
    async with Client(params) as client:
        print("tools:", [t.name for t in (await client.list_tools()).tools])
        for name, args in CALLS:
            result = await client.call_tool(name, args)
            print(f"\n=== {name} (error={result.is_error})\n{result.content[0].text[:700]}")


if __name__ == "__main__":
    asyncio.run(main())
