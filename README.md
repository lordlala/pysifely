# pysifely
Python module for Sifely home products

A Python 3.11 based project written to interact with Sifely products through code.

To get started:
```
import asyncio

from pysifely import Pysifely, LockService

async def async_main():
    client = await Pysifely.create()
    await client.login("user@gmail.com", "password")
    await client._service.get_user_profile()
    print(await client.unique_device_ids)
    #await client._service.get_object_list()
    lock = LockService(client._auth_lib)
    locks = await lock.get_locks()
    await lock.unlock(locks[0])

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(async_main())
```
