import lgpio

class LgpioController:
    h = None

    @staticmethod
    def get_handle():
        if LgpioController.h is None:
            LgpioController.h = lgpio.gpiochip_open(0)
        return LgpioController.h

    @staticmethod
    def cleanup():
        if LgpioController.h is not None:
            lgpio.gpiochip_close(LgpioController.h)
            LgpioController.h = None


class DigitalOutput:
    def __init__(self, pin):
        self.pin = pin
        self.h = LgpioController.get_handle()
        lgpio.gpio_claim_output(self.h, pin, 0)
        self._value = 0

    def on(self):
        self.value = 1

    def off(self):
        self.value = 0

    def toggle(self):
        self.value = 0 if self._value else 1

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, v):
        self._value = 1 if v else 0
        lgpio.gpio_write(self.h, self.pin, self._value)

    def close(self):
        self.off()


class DigitalInput:
    def __init__(self, pin, pull='off'):
        self.pin = pin
        self.h = LgpioController.get_handle()
        pulls = {'up': lgpio.SET_PULL_UP, 'down': lgpio.SET_PULL_DOWN, 'off': 0}
        lgpio.gpio_claim_input(self.h, pin, pulls.get(pull, 0))

        self.when_activated = None
        self.when_deactivated = None

        lgpio.gpio_claim_alert(self.h, pin, lgpio.BOTH_EDGES)
        lgpio.gpio_add_event_func(self.h, pin, self._callback)

    def _callback(self, chip, gpio, level, tick):
        if level == 1 and self.when_activated:
            self.when_activated()
        elif level == 0 and self.when_deactivated:
            self.when_deactivated()

    @property
    def value(self):
        return lgpio.gpio_read(self.h, self.pin)

    @property
    def is_active(self):
        return self.value == 1

    def close(self):
        lgpio.gpio_remove_event_func(self.h, self.pin, self._callback)


class PWMOutput:
    def __init__(self, pin, freq=100):
        self.pin = pin
        self.h = LgpioController.get_handle()
        lgpio.gpio_claim_output(self.h, pin, 0)
        self._freq = freq
        self._value = 0.0
        self.set_freq(freq)

    def set_freq(self, freq):
        self._freq = freq

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, v):
        v = max(0.0, min(1.0, v))
        self._value = v
        lgpio.tx_pwm(self.h, self.pin, self._freq, self._value)

    def on(self):
        self.value = 1.0

    def off(self):
        self.value = 0.0

    def toggle(self):
        self.value = 0.0 if self._value else 1.0

    def close(self):
        self.off()
