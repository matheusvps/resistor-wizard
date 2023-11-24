import platform

if platform.system() != 'Windows':
    import RPi.GPIO as g

    class gpio:
        def __init__(self):
            self.BOARD = g.BOARD
            self.IN = g.IN
            self.OUT = g.OUT
            self.HIGH = g.HIGH
            self.LOW = g.LOW
            self.enabled = False
        #
        def setmode(self, mode):
            if not self.enabled:
                return
            g.setmode(mode)
        #
        def setup(self, pin: int, pinType):
            if not self.enabled:
                return
            g.setup(pin, pinType)
        #
        def output(self, pin: int, state):
            if not self.enabled:
                return
            g.output(pin, state)
        #
        def input(self, pin: int):
            if not self.enabled:
                return
            return g.input(pin)
        #
        def cleanup(self):
            if not self.enabled:
                return
            g.cleanup()
        #
        def PWM(self, pin: int, freq: int):
            if not self.enabled:
                return
            return g.PWM(pin, freq)
else:
    class handler:
        def __init__(self):
            pass
        def start(self, pos: int):
            pass
        def stop(self):
            pass
        def ChangeDutyCycle(self, dc: float):
            pass

    class gpio:
        def __init__(self):
            self.BOARD = 0
            self.IN = 0
            self.OUT = 0
            self.HIGH = 0
            self.LOW = 0
            self.enabled = False
        #
        def setmode(self, mode):
            if not self.enabled:
                return
            else:
                print("You're running this program in a Windows system, which doesn't have GPIO support...")
        #
        def setup(self, pin: int, pinType):
            if not self.enabled:
                return
            else:
                print("You're running this program in a Windows system, which doesn't have GPIO support...")
        #
        def output(self, pin: int, state):
            if not self.enabled:
                return
            else:
                print("You're running this program in a Windows system, which doesn't have GPIO support...")
        #
        def input(self, pin: int):
            if not self.enabled:
                return
            else:
                print("You're running this program in a Windows system, which doesn't have GPIO support...")
        #
        def cleanup(self):
            if not self.enabled:
                return
            else:
                print("You're running this program in a Windows system, which doesn't have GPIO support...")
        #
        def PWM(self, pin: int, freq: int):
            print("You're running this program in a Windows system, which doesn't have GPIO support...")
            return handler()
                