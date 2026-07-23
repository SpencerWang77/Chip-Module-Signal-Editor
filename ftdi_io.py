from pyftdi.gpio import GpioAsyncController
from pyftdi.spi import SpiController
from pyftdi.jtag import JtagEngine
from pyftdi.bits import BitSequence

# AD0: SCLK, AD1: MOSI, AD2: MISO, AD3: CS
def SPIInit(url='ftdi://ftdi:232h:FT80IVK9/1', freq=1e6, mode=0):
    ctrl = SpiController()
    ctrl.configure(url)
    spi_inst = ctrl.get_port(0, freq, mode)
    return spi_inst

class GPIO(object):
    def __init__(self, url='ftdi://ftdi:232h:0:1/1', freq=1e6, dir=0x0):
        self.__inst = GpioAsyncController()
        self.__inst.configure(url=url, frequency=freq, direction=dir)

    # NOTE: The default value for unconnected pins is 1.
    def ReadPin(self, pin):
        if pin > 7:
            raise ValueError("Exceeding the maximum number of pins!")
        value = self.__inst.read()
        pin_val = (value>>pin) & 0x1
        return pin_val

    def WritePin(self, pin, value):
        if pin > 7:
            raise ValueError("Exceeding the maximum number of pins!")
        mask = 1 << pin
        cur_val = self.__inst.read()
        new_val = (cur_val & (~mask)) | (value << pin)
        self.__inst.write(new_val)

# AD0: TCK, AD1: TDI, AD2: TDO, AD3: TMS, AD4: RST
class JTAGIO(object):
    def __init__(self, url='ftdi://ftdi:232h:FT80JBMT/1', freq=1e6):
        self.__inst = JtagEngine(trst=True, frequency=freq)
        self.__inst.configure(url)
        self.__inst.reset()

        self.user_codes = {
            "READ": BitSequence("01", msb=True, length=2),
            "WRITE": BitSequence("10", msb=True, length=2),
            "RDFLG": BitSequence("11", msb=True, length=2)}

        user_inst = BitSequence('0111', msb=True, length=16)
        self.__inst.write_ir(user_inst)
        self.__inst.go_idle()
        self.ReadWord(0x20000000)

    def WaitIdel(self):
        cmd = BitSequence(0x0, msby=False, length=4)
        for i in range(4):
            self.__inst.write_tms(cmd)  # wait 4 cycles

    def ReadWord(self, addr):
        bs_cmd = BitSequence(msb=True)
        bs_addr = BitSequence(addr, msby=False, length=32)
        bs_data = BitSequence(0x0, msby=False, length=32)
        bs_cmd.append(self.user_codes["READ"]).append(bs_addr).append(bs_data)

        self.__inst.write_dr(bs_cmd)
        self.__inst.go_idle()
        self.WaitIdel()
        rdata = self.__inst.read_dr(66)  # read data
        rb_data = rdata.tobytes()
        self.__inst.go_idle()

        addr_r = int.from_bytes(rb_data[4:8], byteorder='big', signed=False)
        if addr_r != addr:
            raise ValueError("Read out fail!!")
        result = int.from_bytes(rb_data[0:4], byteorder="big", signed=False)
        return result

    def WriteWord(self, addr, val):
        cmd = BitSequence(msb=True)
        addr = BitSequence(addr, msby=False, length=32)
        data = BitSequence(val, msby=False, length=32)
        cmd.append(self.user_codes["WRITE"]).append(addr).append(data)

        self.__inst.write_dr(cmd)  # set read command
        self.__inst.go_idle()
        self.WaitIdel()

    def ReadWords(self, start, word):
        results = []
        start &= 0xfffffffc
        for i in range(word):
            offset = i * 4
            val = self.ReadWord(start + offset)
            results.append(val)
        return results

    def WriteWords(self, start, data_list):
        start &= 0xfffffffc
        word = len(data_list)
        for i in range(word):
            offset = i * 4
            self.WriteWord(start + offset, data_list[i])