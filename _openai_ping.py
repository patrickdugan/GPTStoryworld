import asyncio
from openai import AsyncOpenAI

async def main():
    client = AsyncOpenAI()
    models = await client.models.list()
    print('model_count', len(models.data))
    print('models', [m.id for m in models.data])

if __name__ == '__main__':
    asyncio.run(main())
