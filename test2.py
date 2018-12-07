from logger import global_log

# global_log("warning", "Uwaga dupa!")

print({k: n for k, n in enumerate(["a", "b"])})

exit()
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

    await asyncio.wait(tasks)

asyncio.run(main())