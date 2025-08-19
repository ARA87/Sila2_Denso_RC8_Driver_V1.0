from sila2.server import FeatureImplementationBase
from sila2.framework.errors.undefined_execution_error import UndefinedExecutionError
from pybcapclient.orinexception import ORiNException
from driver.denso_rc8_controller import DensoRC8Controller
from typing import List
import logging


class DensoRC8Feature(FeatureImplementationBase):
    def __init__(self, parent_server):
        super().__init__(parent_server)
        self.controller = DensoRC8Controller()

    # --- Connection ---
    def ConfigureConnection(self, IPAddress: str, Port: int, Timeout: int, *, metadata):
        self.controller.configure_connection(ip=IPAddress, port=Port, timeout=Timeout)

    def Start(self, *, metadata):
        self.controller.start()

    # --- S-Variablen ---
    def SetSValue(self, Index: int, Value: str, *, metadata):
        self.controller.set_s_value(Index=Index, value=Value)

    def GetSValue(self, Index: int, *, metadata) -> str:
        return self.controller.get_s_value(Index=Index)

    # --- I-Variablen ---
    def SetIValue(self, Index: int, Value: int, *, metadata):
        self.controller.set_I_value(Index=Index, value=Value)

    def GetIValue(self, Index: int, *, metadata) -> int:
        return self.controller.get_I_value(Index=Index)

    # --- F-Variablen ---
    def SetFValue(self, Index: int, Value: float, *, metadata):
        self.controller.set_F_value(Index=Index, value=Value)

    def GetFValue(self, Index: int, *, metadata) -> float:
        return self.controller.get_F_value(Index=Index)

    # --- P-Variablen ---
    def SetPValue(self, Index: int, Value: List[float], *, metadata):
        self.controller.set_P_value(Index=Index, value=Value)

    def GetPValue(self, Index: int, *, metadata) -> List[float]:
        return self.controller.get_P_value(Index=Index)
        
    # --- J-Variablen ---
    def SetJValue(self, Index: int, Value: List[float], *, metadata):
        self.controller.set_J_value(Index=Index, value=Value)

    def GetJValue(self, Index: int, *, metadata) -> List[float]:
        return self.controller.get_J_value(Index=Index)

    # --- V-Variablen ---
    def SetVValue(self, Index: int, Value: List[float], *, metadata):
        self.controller.set_V_value(Index=Index, value=Value)

    def GetVValue(self, Index: int, *, metadata) -> List[float]:
        return self.controller.get_V_value(Index=Index)

    # --- positionValue ---
    def GetPosValue(self, *, metadata) -> List[float]:
        return self.controller.get_pos_value()

    # --- Programm hinzufügen ---
    def GetProgram(self, ProgramName: str, *, metadata):
        try:
            self.controller.get_program(program_name=ProgramName)
        except ORiNException as e:
            err_desc = ""
            try:
                err_var = self.controller.bcap.controller_getvariable(self.controller.h_ctrl, "@ERROR_DESCRIPTION", "")
                err_desc = self.controller.bcap.variable_getvalue(err_var)
            except Exception as exc:
                logging.warning(f"Fehler beim Auslesen von @ERROR_DESCRIPTION: {exc}")
            raise UndefinedExecutionError(f"ORiNException {e} - Controller-Fehler: {err_desc}")


    # --- Programm starten ---
    def StartProgram(self, ProgramName: str, Mode: str, *, metadata):
        try:
            self.controller.start_program(program_name=ProgramName, mode=Mode)
        except ORiNException as e:
            err_desc = ""
            try:
                err_var = self.controller.bcap.controller_getvariable(self.controller.h_ctrl, "@ERROR_DESCRIPTION", "")
                err_desc = self.controller.bcap.variable_getvalue(err_var)
            except Exception as exc:
                logging.warning(f"Fehler beim Auslesen von @ERROR_DESCRIPTION: {exc}")
            raise UndefinedExecutionError(f"ORiNException {e} - Controller-Fehler: {err_desc}")

    # --- Programm stoppen ---
    def StopProgram(self, ProgramName: str, Mode: str, *, metadata):
        try:
            self.controller.stop_program(program_name=ProgramName, mode=Mode)
        except ORiNException as e:
            err_desc = ""
            try:
                err_var = self.controller.bcap.controller_getvariable(self.controller.h_ctrl, "@ERROR_DESCRIPTION", "")
                err_desc = self.controller.bcap.variable_getvalue(err_var)
            except Exception as exc:
                logging.warning(f"Fehler beim Auslesen von @ERROR_DESCRIPTION: {exc}")
            raise UndefinedExecutionError(f"ORiNException {e} - Controller-Fehler: {err_desc}")


    # --- Lifecycle Hooks ---
    def start(self):
        super().start()
        print("🟢 Feature DensoRC8 gestartet")

    def stop(self):
        print("🔴 Feature DensoRC8 gestoppt")
        super().stop()
