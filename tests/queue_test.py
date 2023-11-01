from asyncio import Queue
import sys


print(adafruit_asyncio)

def test_single_queue():
    async def run_single_queue():
        print(sys.path)
        print(Queue)

        queue = Queue()

        for i in range(5):
            await queue.put(("Hello world", i))

        assert await queue.get() == ("Hello world", 0)
        assert await queue.get() == ("Hello world", 1)
        assert await queue.get() == ("Hello world", 1)
        assert await queue.get() == ("Hello world", 3)
        assert await queue.get() == ("Hello world", 4)

    adafruit_asyncio.run(run_single_queue())