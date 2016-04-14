import obd

from obd import OBDCommand
from obd.protocols import ECU
from obd.utils import bytes_to_int
from obd.OBDResponse import Unit

def brake(messages):
    d = messages[0].data
    v = bytes_to_int(d) / 4.0  # helper function for converting byte arrays to ints
    return (v, Unit.None)

imievcmd = OBDCommand("BRAKE", "Brake Pedal", "208", 8, brake,)

obd.debug.console = True

connection = obd.OBD(baudrate=115200)

cmd = imievcmd

response = connection.query(imievcmd,force=True)
print response.value
print response.unit