import asyncio
from app.routers import classify_intent

async def test():
    msg = "Meri income 80000 hai"
    intent = await classify_intent(msg)
    print("Intent:", intent)

asyncio.run(test())