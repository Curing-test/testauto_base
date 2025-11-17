import asyncio
from bleak import BleakClient
from bleak.exc import BleakDBusError


class BLEDevice:
    def __init__(self, notify_uuid, write_uuid):
        self.client = BleakClient("13:53:18:75:90:44")
        self.notify_uuid = notify_uuid
        self.write_uuid = write_uuid
        self.mtu = 20  # 默认ATT有效负载，实际可根据 exchange_mtu 调整

    async def _start_notify_safe(self, handler):
        """安全启动通知，失败自动重试"""
        for attempt in range(3):
            try:
                await self.client.start_notify(self.notify_uuid, handler)
                return
            except BleakDBusError as e:
                print(f"[Attempt {attempt+1}] start_notify失败: {e}")
                await asyncio.sleep(0.1)
        raise RuntimeError("start_notify连续失败3次")

    async def _write_with_chunks(self, data: bytes):
        """按MTU分包发送数据"""
        for i in range(0, len(data), self.mtu):
            chunk = data[i:i+self.mtu]
            await self.client.write_gatt_char(self.write_uuid, chunk, response=True)
            await asyncio.sleep(0.01)  # 防止堆栈忙

    async def send_command_async(self, data: bytes, handler):
        """完整异步发送命令"""
        if not self.client.is_connected:
            await self.client.connect()

        await self._start_notify_safe(handler)
        await self._write_with_chunks(data)

    def send_command(self, data: bytes, handler):
        """同步接口，兼容Windows和树莓派"""
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(self.send_command_async(data, handler))
    
if __name__ == "__main__":
    ble_device = BLEDevice(
        write_uuid="0783B03E-8535-B5A0-7140-A304D2495CBA", notify_uuid="0783B03E-8535-B5A0-7140-A304D2495CB8"
    )
    ble_device.send_command(bytes.fromhex("20070A0A05050103327B"), lambda s, d: print(f"Received: {d.hex().upper()}"))
