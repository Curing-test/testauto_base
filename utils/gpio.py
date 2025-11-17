import lgpio
import time
import threading

class LgpioBaseDevice:
    def __init__(self, pin):
        self.pin = pin
        self.chip = lgpio.gpiochip_open(0)
        self._closed = False

    def close(self):
        if not self._closed:
            try:
                lgpio.gpio_write(self.chip, self.pin, 0)
            except:
                pass
            lgpio.gpiochip_close(self.chip)
            self._closed = True

    def __del__(self):
        self.close()

# ========== DigitalOutputDevice ==========
class DigitalOutputDevice(LgpioBaseDevice):
    def __init__(self, pin, active_high=True, initial_value=False):
        super().__init__(pin)
        self.active_high = active_high
        lgpio.gpio_claim_output(self.chip, pin)
        self.value(initial_value)

    def on(self):
        self.value(True)

    def off(self):
        self.value(False)

    def toggle(self):
        self.value(not self.value())

    def value(self, val=None):
        if val is None:
            state = lgpio.gpio_read(self.chip, self.pin)
            return bool(state) if self.active_high else not state
        lgpio.gpio_write(self.chip, self.pin, int(bool(val)) if self.active_high else int(not bool(val)))

# ========== DigitalInputDevice ==========
class DigitalInputDevice(LgpioBaseDevice):
    def __init__(self, pin, pull_up=False, bounce_time=None):
        super().__init__(pin)
        pull = lgpio.SET_PULL_UP if pull_up else lgpio.SET_PULL_DOWN
        lgpio.gpio_claim_input(self.chip, pin)
        # lgpio.gpio_set_pull(self.chip, pin, pull)
        self.bounce_time = bounce_time
        self._callbacks = []
        self._last_state = self.value
        self._start_monitor()

    def _start_monitor(self):
        def poll():
            while not self._closed:
                current = self.value
                if current != self._last_state:
                    self._last_state = current
                    for cb in self._callbacks:
                        cb()
                time.sleep(self.bounce_time or 0.01)
        threading.Thread(target=poll, daemon=True).start()

    def when_activated(self, callback):
        self._callbacks.append(lambda: callback() if self.is_active else None)

    def when_deactivated(self, callback):
        self._callbacks.append(lambda: callback() if not self.is_active else None)

    @property
    def is_active(self):
        return self.value

    @property
    def value(self):
        return bool(lgpio.gpio_read(self.chip, self.pin))

# ========== PWMOutputDevice ==========
class PWMOutputDevice(LgpioBaseDevice):
    def __init__(self, pin, frequency=1000, initial_value=0.0):
        super().__init__(pin)
        self.frequency = frequency
        self.duty_cycle = initial_value
        self._value = initial_value
        lgpio.gpio_claim_output(self.chip, pin)
        self._apply_pwm()

    def _apply_pwm(self):
        duty_percent = max(0.0, min(1.0, self.duty_cycle)) * 100.0
        lgpio.tx_pwm(self.chip, self.pin, self.frequency, duty_percent)

    def on(self):
        self.duty_cycle = 1.0
        self._apply_pwm()

    def off(self):
        self.duty_cycle = 0.0
        self._apply_pwm()

    def toggle(self):
        self.duty_cycle = 1.0 - self.duty_cycle
        self._apply_pwm()


    @property
    def value(self):
        return self._value
    
    @value.setter
    def value(self, v=None):
        if v is None:
            return self.duty_cycle
        self.duty_cycle = max(0.0, min(1.0, v))
        self._apply_pwm()


    def set_frequency(self, freq):
        self.frequency = freq
        self._apply_pwm()
