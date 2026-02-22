import asyncio
from agents.form_filler import launch_form_filler


async def main():
    event = asyncio.Event()
    ready = asyncio.Event()

    def on_done():
        print('[run_filler] on_done called')

    def on_error(err: str):
        print('[run_filler] on_error called:', err)

    task = asyncio.create_task(
        launch_form_filler(
            event=event,
            scheme_id='scheme_002',
            user_data={
                'full_name': 'Test User',
                'age': 30,
                'income': 50000,
                'community': 'OBC',
                'occupation': 'Farmer',
                'state': 'Uttar Pradesh',
            },
            on_done=on_done,
            on_error=on_error,
            ready=ready,
        )
    )

    try:
        print('[run_filler] waiting for ready...')
        await asyncio.wait_for(ready.wait(), timeout=15)
        print('[run_filler] ready event set by filler (browser should be open)')
    except asyncio.TimeoutError:
        print('[run_filler] timeout waiting for ready')

    # Give the user a moment to see/open the browser, then resume
    await asyncio.sleep(3)
    print('[run_filler] signaling resume (event.set())')
    event.set()

    # Wait for the task to complete or fail
    await asyncio.sleep(8)


if __name__ == '__main__':
    asyncio.run(main())
