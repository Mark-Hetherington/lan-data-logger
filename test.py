import obd

from obd import OBDCommand
# from obd.protocols import ECU
from obd.utils import bytes_to_hex
from obd.OBDResponse import Unit

PIDs = ["119", "149"]

def brake(messages):
    d = messages[0].data
    v = bytes_to_hex(d)  # helper function for converting byte arrays to hex
    return (v, Unit.NONE)

imievcmd = OBDCommand("BRAKE", "Brake Pedal", "01208", 8, brake,)

obd.debug.console = True

connection = obd.OBD(baudrate=115200)

cmd = imievcmd

response = connection.query(imievcmd,force=True)
print response.value
print response.unit