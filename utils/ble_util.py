import asyncio
import time
from bleak import BleakClient

class BLEDeviceSync:
    def __init__(self, address, write_uuid="0783B03E-8535-B5A0-7140-A304D2495CBA", notify_uuid="0783B03E-8535-B5A0-7140-A304D2495CB8"):
        self.address     = address
        self.client      = None
        # self.loop        = asyncio.get_event_loop()                 # 使用持久 loop
        self.lock        = asyncio.Lock()                           # 避免并发时 BLE 通道冲突
        self.write_uuid  = write_uuid
        self.notify_uuid = notify_uuid
        self._notification_started = False

    async def ensure_connected(self):
        """确保BLE设备已连接，否则自动重连"""
        print("当前蓝牙连接状态:", self.client.is_connected if self.client else "未连接")
        if not self.client or not self.client.is_connected:
            if self.client:
                try:
                    await self.client.disconnect()
                except Exception:
                    pass
            self.client = BleakClient(self.address)
            await self.client.connect()
            print("蓝牙已连接")

    async def _send_and_wait_async(self, packet, timeout: float = 5.0):
        for _ in range(3):
            try:
                await self.ensure_connected()
                break
            except Exception as e:
                import traceback
                print("蓝牙连接失败，重试中...", e)
                traceback.print_exc()
                await asyncio.sleep(1)
        else:
            raise ConnectionError("蓝牙无法连接")
        async with self.lock:  # 保证同一时刻只有一个命令在发
            result_container = {}
            event = asyncio.Event()
            def notification_handler(sender, data):
                # print(f"蓝牙接收:{data.hex().upper()}")
                result_container["raw"] = data
                event.set()
            await self.client.start_notify(self.notify_uuid, notification_handler)
            await self.client.write_gatt_char(self.write_uuid, packet)
            try:
                await asyncio.wait_for(event.wait(), timeout)
            except asyncio.TimeoutError:
                print(f"蓝牙数据接收超时：{packet.hex().upper()}")
            await self.client.stop_notify(self.notify_uuid)
            return result_container


    async def disconnect(self):
        """主动断开连接"""
        try:
            if self._notification_started:
                await self.client.stop_notify(self.notify_uuid)
                self._notification_started = False
            await self.client.disconnect()
        except:
            pass

if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    ble_device = BLEDeviceSync(address="13:53:18:75:90:44")
    response = ble_device.send_command(0x20, {"defend": 1, "idx": 3, "volumn": 50})
    print("Response:", response)
    time.sleep(2)
    response2 = ble_device.send_command(0x21, {})
    print("Response:", response2)
    time.sleep(2)
    response3 = ble_device.send_command(0x24, {"saddle": 0, "idx": 3, "volumn": 50})
    print("蓝牙解析后数据: ", response3)
    time.sleep(2)
    loop.run_until_complete(ble_device.disconnect())
    loop.run_until_complete(asyncio.sleep(0.2))  # 让Bleak后台彻底释放
    loop.close()