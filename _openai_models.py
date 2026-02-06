import asyncio
from openai import AsyncOpenAI

async def main():
    m = await AsyncOpenAI().models.list()
    print([x.id for x in m.data])

asyncio.run(main())
