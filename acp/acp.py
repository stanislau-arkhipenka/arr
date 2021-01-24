import board
import busio
import adafruit_pca9685

class Acp:

    def __init__(self):
        self.i2c = busio.I2C(board.SCL, board.SDA)
        self.pca1 = adafruit_pca9685.PCA9685(i2c, address=0x40)
        self.pca2 = adafruit_pca9685.PCA9685(i2c, address=0x40) # TODO change address

        



