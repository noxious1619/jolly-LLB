# test_flow.py

import asyncio
from app.flow_controller import FlowController


async def test():
    flow = FlowController()

    print("---- Test 1: Casual ----")
    print(await flow.handle_message("Hi"))

    print("\n---- Test 2: Start Policy Query ----")
    print(await flow.handle_message("Main minority student hoon"))

    print("\n---- Test 3: Provide Age ----")
    print(await flow.handle_message("14 saal ka hoon"))

    print("\n---- Test 4: Provide Income ----")
    print(await flow.handle_message("Meri income 80000 hai"))


asyncio.run(test())