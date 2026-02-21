# test_full_system.py

import asyncio
from app.flow_controller import FlowController


async def run_test():
    flow = FlowController()

    print("---- STEP 1: Casual ----")
    print(await flow.handle_message("Hi"))

    print("\n---- STEP 2: Start Query ----")
    print(await flow.handle_message("Main minority student hoon"))

    print("\n---- STEP 3: Provide Age ----")
    print(await flow.handle_message("14 saal ka hoon"))

    print("\n---- STEP 4: Provide Income ----")
    print(await flow.handle_message("Meri income 80000 hai"))


asyncio.run(run_test())