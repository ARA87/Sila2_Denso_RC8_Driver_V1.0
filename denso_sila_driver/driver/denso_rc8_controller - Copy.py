# driver/denso_rc8_controller.py
import pybcapclient.bcapclient as bcapclient 


class DensoRC8Controller:
    def __init__(self):
        self.ip = None
        self.port = None
        self.timeout = None

        self.bcap = None
        self.h_ctrl = None
        self.S = None

    def configure_connection(self, ip: str, port: int, timeout: int):
        self.ip = ip
        self.port = port
        self.timeout = timeout

    def start(self):
        if not all([self.ip, self.port, self.timeout]):
            raise RuntimeError("Connection not configured. Call configure_connection() first.")

        self.bcap = bcapclient.BCAPClient(host=self.ip, port=self.port, timeout=self.timeout)
        self.bcap.service_start('')

        self.h_ctrl = self.bcap.controller_connect(
            name='',
            provider='CaoProv.DENSO.VRC',
            machine='localhost',
            option=''
        )

        #self.S10 = self.bcap.controller_getvariable(self.h_ctrl, 'S10', '')
        # 🔧 Dynamische Zuweisung von S-Variablen
        self.S = {}
        for Index in range(0, 49):  # oder nur [10,11,...]
            var_name = f"S{Index}"
            self.S[Index] = self.bcap.controller_getvariable(self.h_ctrl, var_name, '')

    def set_s_value(self, Index:int, value: str):
        if self.S is None or Index not in self.S:
            raise RuntimeError(f"S{Index} not initialized. Call start() first.")
        self.bcap.variable_putvalue(self.S[Index], value)

    def get_s_value(self, Index:int) -> str:
        if self.S is None or Index not in self.S:
            raise RuntimeError(f"S{Index} not initialized. Call start() first.")
        return self.bcap.variable_getvalue(self.S[Index])
