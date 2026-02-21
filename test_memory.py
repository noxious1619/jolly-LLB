import asyncio
from app.extractor import extract_user_profile
from app.memory import ConversationMemory


async def test():
    memory = ConversationMemory()

    # Turn 1
    msg1 = "Main minority student hoon"
    profile1 = await extract_user_profile(msg1)
    merged1 = memory.merge_profile(profile1)

    print("After Turn 1:")
    print(merged1)

    # Turn 2
    msg2 = "14 saal ka hoon"
    profile2 = await extract_user_profile(msg2)
    merged2 = memory.merge_profile(profile2)

    print("\nAfter Turn 2:")
    print(merged2)


asyncio.run(test())