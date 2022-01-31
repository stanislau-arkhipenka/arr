import RPi.GPIO as GPIO


class Led:

    def __init__(self, id: int):
        self.id = id
        self.state = False
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.id, GPIO.OUT)

    def change(self):
        if self.state:
            self.off()
        else:
            self.on()
        self.state = not self.state

    def on(self):
        GPIO.output(self.id, GPIO.HIGH)
    
    def off(self):
        GPIO.output(self.id, GPIO.LOW)