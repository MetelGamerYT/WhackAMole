import time


try:
    import RPi.GPIO as GPIO
    from RPLCD.gpio import CharLCD
except (ImportError, RuntimeError):
    GPIO = None
    CharLCD = None


class HardwareController:
    ROWS = [5, 6, 13, 19]
    COLS = [12, 16, 20, 21]
    KEYS = [
        ["1", "2", "3", "A"],
        ["4", "5", "6", "B"],
        ["7", "8", "9", "C"],
        ["*", "0", "#", "D"],
    ]

    LED_R = 7
    LED_G = 9
    LED_B = 10

    ENC_CLK = 11
    ENC_DT = 14
    ENC_SW = 15

    DEBOUNCE_SECONDS = 0.03
    BUTTON_DEBOUNCE_SECONDS = 0.2

    def __init__(self):
        self.available = GPIO is not None and CharLCD is not None
        self.key_active = False
        self.last_clk = None
        self.last_button = None
        self.last_button_press = 0.0
        self.lcd = None

        if self.available:
            self._setup_gpio()

    def _setup_gpio(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)

        for row_pin in self.ROWS:
            GPIO.setup(row_pin, GPIO.OUT)
            GPIO.output(row_pin, GPIO.HIGH)

        for col_pin in self.COLS:
            GPIO.setup(col_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

        self.lcd = CharLCD(
            numbering_mode=GPIO.BCM,
            cols=16,
            rows=2,
            pin_rs=26,
            pin_e=24,
            pins_data=[4, 17, 18, 27, 22, 23, 25, 8],
        )

        GPIO.setup(self.LED_R, GPIO.OUT)
        GPIO.setup(self.LED_G, GPIO.OUT)
        GPIO.setup(self.LED_B, GPIO.OUT)
        self.set_rgb(False, False, False)

        GPIO.setup(self.ENC_CLK, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(self.ENC_DT, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(self.ENC_SW, GPIO.IN, pull_up_down=GPIO.PUD_UP)

        self.last_clk = GPIO.input(self.ENC_CLK)
        self.last_button = GPIO.input(self.ENC_SW)
        self.lcd_clear()

    def is_available(self):
        return self.available

    def scan_keypad(self):
        if not self.available:
            return None

        for row_index, row_pin in enumerate(self.ROWS):
            GPIO.output(row_pin, GPIO.LOW)

            for col_index, col_pin in enumerate(self.COLS):
                if GPIO.input(col_pin) == GPIO.LOW:
                    GPIO.output(row_pin, GPIO.HIGH)
                    return self.KEYS[row_index][col_index]

            GPIO.output(row_pin, GPIO.HIGH)

        return None

    def poll_keypad(self):
        key = self.scan_keypad()

        if key and not self.key_active:
            time.sleep(self.DEBOUNCE_SECONDS)

            if self.scan_keypad() == key:
                self.key_active = True
                return key

        if not key:
            self.key_active = False

        return None

    def poll_encoder(self):
        if not self.available:
            return None

        clk_state = GPIO.input(self.ENC_CLK)
        dt_state = GPIO.input(self.ENC_DT)
        event = None

        if clk_state != self.last_clk:
            if dt_state != clk_state:
                event = "next"
            else:
                event = "previous"

        self.last_clk = clk_state

        button_state = GPIO.input(self.ENC_SW)
        now = time.monotonic()

        if (
            self.last_button == GPIO.HIGH
            and button_state == GPIO.LOW
            and now - self.last_button_press >= self.BUTTON_DEBOUNCE_SECONDS
        ):
            event = "press"
            self.last_button_press = now

        self.last_button = button_state
        return event

    def lcd_show(self, line1, line2=""):
        if not self.available or self.lcd is None:
            return

        line1 = str(line1)[:16].ljust(16)
        line2 = str(line2)[:16].ljust(16)

        self.lcd.cursor_pos = (0, 0)
        self.lcd.write_string(line1)
        self.lcd.cursor_pos = (1, 0)
        self.lcd.write_string(line2)

    def lcd_clear(self):
        if self.available and self.lcd is not None:
            self.lcd.clear()

    def set_rgb(self, r=False, g=False, b=False):
        if not self.available:
            return

        GPIO.output(self.LED_R, GPIO.HIGH if r else GPIO.LOW)
        GPIO.output(self.LED_G, GPIO.HIGH if g else GPIO.LOW)
        GPIO.output(self.LED_B, GPIO.HIGH if b else GPIO.LOW)

    def led_off(self):
        self.set_rgb(False, False, False)

    def cleanup(self):
        if not self.available:
            return

        self.led_off()
        self.lcd_clear()
        GPIO.cleanup()
        self.available = False


_hardware = None


def get_hardware():
    global _hardware

    if _hardware is None:
        _hardware = HardwareController()

    return _hardware


def cleanup_hardware():
    global _hardware

    if _hardware is not None:
        _hardware.cleanup()
        _hardware = None
