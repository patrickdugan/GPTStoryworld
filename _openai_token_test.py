import asyncio
from openai import AsyncOpenAI

async def main():
    client = AsyncOpenAI()
    resp = await client.responses.create(
        model="gpt-5-mini",
        input="Say 'ping' and one short sentence about diplomacy.",
        max_output_tokens=30,
    )
    text = resp.output_text
    print('response:', text)

if __name__ == '__main__':
    asyncio.run(main())
