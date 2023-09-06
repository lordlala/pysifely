from .base_service import BaseService
from ..types import Device, DeviceTypes


class Lock(Device):
    unlocked = False
    door_open = False
    trash_mode = False


class LockService(BaseService):
    async def update(self, lock: Lock):
        device_info = await self._get_lock_info(lock)
        lock.raw_dict = device_info["device"]

        lock.available = lock.raw_dict.get("available") == 1
        lock.door_open = lock.raw_dict.get("door_open") == 1
        lock.trash_mode = lock.raw_dict.get("trash_mode") == 1

        # store the nested dict for easier reference below
        lock.unlocked = lock.raw_dict.get("unlocked")
        # Check if the door is locked
        #lock.unlocked = locker_status.get("hardlock") == 2

        return lock

    async def get_locks(self):
        if self._devices is None:
            self._devices = await self.get_object_list()

        locks = [device for device in self._devices if device.type is DeviceTypes.LOCK]

        return [Lock(device.raw_dict) for device in locks]

    async def lock(self, lock: Lock):
        await self._lock_control(lock, "Lock")

    async def unlock(self, lock: Lock):
        await self._lock_control(lock, "Unlock")