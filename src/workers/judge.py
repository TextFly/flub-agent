import os
from dedalus_labs import AsyncDedalus, DedalusRunner
from dotenv import load_dotenv
from dedalus_labs.utils.stream import stream_async
import asyncio

load_dotenv()

async def main():
    client = AsyncDedalus()
    runner = DedalusRunner(client)

    result = await runner.run(
        input="",
        model=["google/gemini-2.5-pro"],
        mcp_servers=[],
        stream=False
    )

    print(result.final_output)

if __name__ == "__main__":
    asyncio.run(main())