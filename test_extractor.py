import asyncio
from app.extractor import extract_user_profile, check_missing_fields

async def test():
    message = "Main 14 saal ka hoon"
    
    profile = await extract_user_profile(message)
    
    print("Extracted Profile:")
    print(profile)

    missing = check_missing_fields(profile)
    print("Missing Fields:", missing)

asyncio.run(test())