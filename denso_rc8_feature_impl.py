# implementation/denso_rc8_feature_impl.py

from sila2.server import FeatureImplementationBase
from driver.denso_rc8_controller import DensoRC8Controller


class DensoRC8Feature(FeatureImplementationBase):
    def __init__(self, parent_server):
        super().__init__(parent_server)
        self.controller = DensoRC8Controller()

    def ConfigureConnection(self, IPAddress: str, Port: int, Timeout: int,*,metadata):
        self.controller.configure_connection(ip=IPAddress, port=Port, timeout=Timeout)

    def Start(self,*,metadata):
        self.controller.start()

    def SetSValue(self, Index: int, Value: str,*,metadata):
        self.controller.set_s_value(Index = Index, value=Value)

    def GetSValue(self, Index: int,*,metadata) -> int:
        return self.controller.get_s_value(Index = Index)

    def start(self):
        super().start()
        print("🟢 Feature DensoRC8 gestartet")

    def stop(self):
        print("🔴 Feature DensoRC8 gestoppt")
        super().stop()
