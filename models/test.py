#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from bluepy.btle import Scanner, DefaultDelegate, Peripheral, BTLEException
import time, binascii, sys

# ============ 配置区 ============
TARGET_NAME = ""    # 设备名称（或 MAC）
TARGET_ADDR = "13:53:18:75:90:44"              # 可填写设备MAC，如 "A4:C1:38:12:34:56"
WRITE_UUID  = "0783b03e-8535-b5a0-7140-a304d2495cb9"  # 写入特征UUID
NOTIFY_UUID = "0783B03E-8535-B5A0-7140-A304D2495CB8"  # 通知特征UUID
SEND_DATA   = bytes.fromhex("20070A0A05050103327B")  # 要发送的指令
# ===============================


# 通知回调类
class NotifyDelegate(DefaultDelegate):
    def __init__(self):
        DefaultDelegate.__init__(self)

    def handleNotification(self, cHandle, data):
        print(f"📩 收到数据: {binascii.hexlify(data).decode().upper()}")


def find_device():
    """扫描目标设备"""
    scanner = Scanner()
    print("🔍 扫描中...")
    devices = scanner.scan(8.0)
    for dev in devices:
        name = dev.getValueText(9)
        if name:
            print(f"  - {dev.addr} [{name}] RSSI={dev.rssi} dB")
        if TARGET_NAME and name == TARGET_NAME:
            print(f"✅ 找到目标设备: {name} ({dev.addr})")
            return dev.addr
        elif TARGET_ADDR and dev.addr.lower() == TARGET_ADDR.lower():
            print(f"✅ 找到目标设备: {dev.addr}")
            return dev.addr
    print("❌ 未找到目标设备")
    return None


def main():
    addr = TARGET_ADDR or find_device()

    try:
        print(f"🔗 正在连接 {addr} ...")
        dev = Peripheral(addr)
        dev.setDelegate(NotifyDelegate())
        print("✅ 已连接")
        # for svc in dev.services:
        #     print("Service:", svc.uuid)
        #     for ch in svc.getCharacteristics():
        #         print(f"  Char: {ch.uuid} -> {ch.propertiesToString()}")

        # 启用通知
        notify_ch = dev.getCharacteristics(uuid=NOTIFY_UUID)[0]
        notify_handle = notify_ch.getHandle() + 1
        dev.writeCharacteristic(notify_handle, b"\x01\x00", withResponse=True)
        print("🔔 已开启通知监听")

        # 发送数据
        write_ch = dev.getCharacteristics(uuid=WRITE_UUID)[0]
        write_ch.write(SEND_DATA, withResponse=True)
        print(f"📤 已发送: {SEND_DATA.hex().upper()}")

        # 循环等待数据
        print("⏳ 等待设备返回数据 (Ctrl+C退出)...")
        while True:
            if dev.waitForNotifications(5.0):
                continue
            else:
                print("...暂无数据")

    except KeyboardInterrupt:
        print("\n🛑 用户中断，断开连接")
    except BTLEException as e:
        import traceback
        traceback.print_exc()
        print("❌ 蓝牙异常：", e)
    finally:
        try:
            dev.disconnect()
        except:
            pass
        print("🔚 已断开连接")


if __name__ == "__main__":
    
    main()
