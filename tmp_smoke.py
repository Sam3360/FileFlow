import asyncio
from fileflow.app import FileFlowApp

async def smoke():
    app = FileFlowApp()
    print('BEFORE_RUN_TEST')
    async with app.run_test() as pilot:
        print('IN_RUN_TEST')
        print(app.current_path)
        await pilot.pause()
    print('AFTER_RUN_TEST')

asyncio.run(smoke())
