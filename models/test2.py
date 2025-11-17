from bluepy.btle import Peripheral, DefaultDelegate
import binascii

TARGET_NAME = ""    # 设备名称（或 MAC）
TARGET_ADDR = "13:53:18:75:90:44"              # 可填写设备MAC，如 "A4:C1:38:12:34:56"
WRITE_UUID  = "0783b03e-8535-b5a0-7140-a304d2495cb9"  # 写入特征UUID
NOTIFY_UUID = "0783B03E-8535-B5A0-7140-A304D2495CB8"  # 通知特征UUID
SEND_DATA   = bytes.fromhex("20070A0A05050103327B")  # 要发送的指令

class MyDelegate(DefaultDelegate):
    def handleNotification(self, cHandle, data):
        print("📩 收到设备返回:", binascii.hexlify(data).decode().upper())

dev = Peripheral(TARGET_ADDR)
dev.setDelegate(MyDelegate())
print("✅ 已连接" if dev.getState() == "conn" else "❌ 连接失败")
# 启用通知
notify_ch = dev.getCharacteristics(uuid=NOTIFY_UUID)[0]
notify_handle = notify_ch.getHandle() + 1
dev.writeCharacteristic(notify_handle, b"\x01\x00", withResponse=True)
print(dev.getCharacteristics(uuid=NOTIFY_UUID)[0].propertiesToString())
# 发送数据
write_ch = dev.getCharacteristics(uuid=WRITE_UUID)[0]
props = write_ch.propertiesToString()
with_response = 'WRITE NO RESPONSE' not in props
write_ch.write(SEND_DATA, withResponse=with_response)
print("📤 数据已发送:", SEND_DATA.hex().upper())

# 循环等待返回
while True:
    if dev.waitForNotifications(5.0):
        continue
    print("⏳ 等待设备返回...")
