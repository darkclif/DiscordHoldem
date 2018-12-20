from logger import global_log

import threading, asyncio

async def test(a):
    await asyncio.sleep(2)
    print("{b: >12}".format(b=a))


async def test_wrapper(a):
    await test(a)


async def main():
    tasks = []

    for w in ["Hello", "world!"]:
        tasks.append(asyncio.create_task(test_wrapper(w)))

    tasks[0].cancel()
    #await asyncio.wait(tasks)
    print(tasks[0])

asyncio.run(main())