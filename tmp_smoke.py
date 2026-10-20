import asyncio
from fileflow.app import FileFlowApp

async def smoke():
    app = FileFlowApp()
    async with app.run_test() as pilot:
        print('APP_OK')
        await pilot.press('q')
        print('QUIT_SENT')

asyncio.run(smoke())
