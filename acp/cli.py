import click

from board import SCL, SDA
import busio

from adafruit_motor import servo
from adafruit_pca9685 import PCA9685
from typing import List


@click.group()
def cli() -> None:
    print("Hello")


@cli.command()
@click.argument("bus", type=click.IntRange(min=0, max=1))
@click.argument("channel", type=click.IntRange(min=0, max=15))
@click.argument("value", type=click.IntRange(min=0, max=180))
def set(bus: int, channel: int, value: int) -> None:
    my_servo = servo.Servo(busses[bus].channels[channel])
    my_servo.angle = value
    


if __name__ == "__main__":
    i2c = busio.I2C(SCL, SDA)
    pca1 = PCA9685(i2c, address=0x40)
    pca1.frequency = 50
    pca2 = PCA9685(i2c, address=0x41)
    pca2.frequency = 50
    busses: List[PCA9685] = [pca1, pca2]
    cli()