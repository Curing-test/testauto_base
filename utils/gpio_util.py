class PIN:
    # TYPE1 电池仓锁
    class SADDLE_LOCK_1:
        unlock   = 21      # 开锁
        lock     = 20      # 关锁
        feedback = 16      # 反馈
    # TYPE6 头盔锁
    class HELMET_LOCK_6:
        unlock    = 26      # 开锁
        lock      = 19      # 关锁
        induction = 13      # 感应
        ready     = 6       # 到位
    # 大电
    class ExternalPower:
        power = 14          # 大电控制引脚

    # 薄膜超载
    class OVERLOAD_2:
        head = 23         # 前触点
        tail = 24         # 后触点

    class RFID:
        acc = 12            # RFID 5V供电检测

    class MOTOR_CONTROLLER1:
        acc_detect_pin     = 15  # 电门检测引脚
        wheel_rotation_pin = 18  # 轮动输出引脚
