import logging
from typing import List
import pybcapclient.bcapclient as bcapclient
from pybcapclient.orinexception import ORiNException


class DensoRC8Controller:
    def __init__(self):
        self.ip = None
        self.port = None
        self.timeout = None
        self.bcap = None
        self.h_ctrl = None
        self.S = None
        self.I = None
        self.F = None
        self.P = None
        self.J = None
        self.V = None
        self.h_task = None
        self.Robot =  None
        self.Pos = None

    def configure_connection(self, ip: str, port: int, timeout: int):
        self.ip = ip
        self.port = port
        self.timeout = timeout

    def start(self):
        if not all([self.ip, self.port, self.timeout]):
            raise RuntimeError("Connection not configured. Call configure_connection() first.")
        try:
            self.bcap = bcapclient.BCAPClient(host=self.ip, port=self.port, timeout=self.timeout)
            self.bcap.service_start('')

            self.h_ctrl = self.bcap.controller_connect(
                name='',
                provider='CaoProv.DENSO.VRC',
                machine='localhost',
                option=''
            )

            # S-Variables
            count_s_vars = 48
            self.S = {i: self.bcap.controller_getvariable(self.h_ctrl, f"S{i}", '') for i in range(count_s_vars)}
            logging.info("Verbindung gestartet: %d S-Variablen geladen.", count_s_vars)

            # I-Variables
            count_i_vars = 98
            self.I = {i: self.bcap.controller_getvariable(self.h_ctrl, f"I{i}", '') for i in range(count_i_vars)}
            logging.info("Verbindung gestartet: %d I-Variablen geladen.", count_i_vars)

            # F-Variables
            count_f_vars = 98
            self.F = {i: self.bcap.controller_getvariable(self.h_ctrl, f"F{i}", '') for i in range(count_f_vars)}
            logging.info("Verbindung gestartet: %d F-Variablen geladen.", count_f_vars)

            # P-Variables
            count_p_vars = 98
            self.P = {i: self.bcap.controller_getvariable(self.h_ctrl, f"P{i}", '') for i in range(count_p_vars)}
            logging.info("Verbindung gestartet: %d P-Variablen geladen.", count_p_vars)
            
            # J-Variables
            count_j_vars = 98
            self.J = {i: self.bcap.controller_getvariable(self.h_ctrl, f"J{i}", '') for i in range(count_j_vars)}
            logging.info("Verbindung gestartet: %d J-Variablen geladen.", count_j_vars)

            # V-Variables
            count_v_vars = 48
            self.V = {i: self.bcap.controller_getvariable(self.h_ctrl, f"V{i}", '') for i in range(count_v_vars)}
            logging.info("Verbindung gestartet: %d J-Variablen geladen.", count_j_vars)
            
            #Add_Robot
            self.Robot = self.bcap.controller_getrobot(self.h_ctrl,"Arm","")
            
            # Current_Position
            self.Pos = self.bcap.robot_getvariable(self.Robot, "@CURRENT_POSITION", '')
            logging.info("Verbindung gestartet: Curpos geladen.")

        except ORiNException as e:
            logging.error(f"ORiNException beim Starten: {e}")
            self._log_error_description()
            raise
        except Exception:
            logging.exception("Allgemeiner Fehler beim Start")
            self._log_error_description()
            raise

    def get_pos_value(self) -> List[float]:
        if self.Pos is None:
            raise RuntimeError("Position not initialized")
        
        retval = self.bcap.variable_getvalue(self.Pos)
        logging.info("retval")
        return retval

    # --- S-Values ---
    def set_s_value(self, Index: int, value: str):
        if self.S is None or Index not in self.S:
            raise RuntimeError(f"S{Index} not initialized. Call start() first.")
        self.bcap.variable_putvalue(self.S[Index], value)
        logging.info("S%d gesetzt auf: %s", Index, value)

    def get_s_value(self, Index: int) -> str:
        if self.S is None or Index not in self.S:
            raise RuntimeError(f"S{Index} not initialized. Call start() first.")
        retval = self.bcap.variable_getvalue(self.S[Index])
        logging.info("S%d gelesen: %s", Index, retval)
        return retval

    # --- I-Values ---
    def set_I_value(self, Index: int, value: int):
        if self.I is None or Index not in self.I:
            raise RuntimeError(f"I{Index} not initialized. Call start() first.")
        self.bcap.variable_putvalue(self.I[Index], value)
        logging.info("I%d gesetzt auf: %s", Index, value)

    def get_I_value(self, Index: int) -> int:
        if self.I is None or Index not in self.I:
            raise RuntimeError(f"I{Index} not initialized. Call start() first.")
        retval = self.bcap.variable_getvalue(self.I[Index])
        logging.info("I%d gelesen: %s", Index, retval)
        return retval

    # --- F-Values ---
    def set_F_value(self, Index: int, value: float):
        if self.F is None or Index not in self.F:
            raise RuntimeError(f"F{Index} not initialized. Call start() first.")
        self.bcap.variable_putvalue(self.F[Index], value)
        logging.info("F%d gesetzt auf: %s", Index, value)

    def get_F_value(self, Index: int) -> float:
        if self.F is None or Index not in self.F:
            raise RuntimeError(f"F{Index} not initialized. Call start() first.")
        retval = self.bcap.variable_getvalue(self.F[Index])
        logging.info("F%d gelesen: %s", Index, retval)
        return retval

    # --- P-Values (List from Float) ---
    def set_P_value(self, Index: int, value: List[float]):
        if self.P is None or Index not in self.P:
            raise RuntimeError(f"P{Index} not initialized. Call start() first.")
        # Direkt die Python-Liste an BCAP übergeben
        self.bcap.variable_putvalue(self.P[Index], value)
        logging.info("P%d gesetzt auf: %s", Index, value)

    def get_P_value(self, Index: int) -> List[float]:
        if self.P is None or Index not in self.P:
            raise RuntimeError(f"P{Index} not initialized. Call start() first.")
        retval = self.bcap.variable_getvalue(self.P[Index])
        logging.info("P%d gelesen: %s", Index, retval)
        return retval
        
    # --- J-Values (List from Float) ---
    def set_J_value(self, Index: int, value: List[float]):
        if self.J is None or Index not in self.J:
            raise RuntimeError(f"J{Index} not initialized. Call start() first.")
        # Direkt die Python-Liste an BCAP übergeben
        self.bcap.variable_putvalue(self.J[Index], value)
        logging.info("J%d gesetzt auf: %s", Index, value)

    def get_J_value(self, Index: int) -> List[float]:
        if self.J is None or Index not in self.J:
            raise RuntimeError(f"J{Index} not initialized. Call start() first.")
        retval = self.bcap.variable_getvalue(self.J[Index])
        logging.info("J%d gelesen: %s", Index, retval)
        return retval        

    # --- V-Values (List from Float) ---
    def set_V_value(self, Index: int, value: List[float]):
        if self.V is None or Index not in self.V:
            raise RuntimeError(f"V{Index} not initialized. Call start() first.")
        # Direkt die Python-Liste an BCAP übergeben
        self.bcap.variable_putvalue(self.V[Index], value)
        logging.info("V%d gesetzt auf: %s", Index, value)

    def get_V_value(self, Index: int) -> List[float]:
        if self.V is None or Index not in self.V:
            raise RuntimeError(f"V{Index} not initialized. Call start() first.")
        retval = self.bcap.variable_getvalue(self.V[Index])
        logging.info("J%d gelesen: %s", Index, retval)
        return retval        
        
    # --- Add Programm  ---
    def get_program(self, program_name: str):
        self.h_task = self.bcap.controller_gettask(self.h_ctrl, program_name, "")
        if not self.h_task:
            raise RuntimeError(f"Konnte Task für Programm '{program_name}' nicht abrufen")
        logging.info("Programm '%s' hinzugefügt", program_name)

    # --- start Programm ---
    def start_program(self, program_name: str, mode: str):
        mode_map = {"one_cycle": 1, "continuous": 2, "step_forward": 3}
        if mode not in mode_map:
            raise ValueError(f"Ungültiger Modus: {mode}. Erlaubt: {list(mode_map.keys())}")
        self.bcap.task_start(self.h_task, mode_map[mode], "")
        logging.info("Programm '%s' gestartet im Modus '%s'", program_name, mode)

    # --- stop Programm ---
    def stop_program(self, program_name: str, mode: str):
        mode_map = {"default_stop": 0, "instant_stop": 1, "step_stop": 2, "cycle_stop": 3}
        if mode not in mode_map:
            raise ValueError(f"Ungültiger Modus: {mode}. Erlaubt: {list(mode_map.keys())}")
        self.bcap.task_stop(self.h_task, mode_map[mode], "")
        logging.info("Programm '%s' gestoppt im Modus '%s'", program_name, mode)


    # --- Error_Handling ---
    def _log_error_description(self):
        if not self.h_ctrl:
            logging.warning("Kein Controller-Handle für Fehlerbeschreibung.")
            return
        try:
            err_var = self.bcap.controller_getvariable(self.h_ctrl, "@ERROR_DESCRIPTION", "")
            err_msg = self.bcap.variable_getvalue(err_var)
            if err_msg:
                logging.error(f"RC8 @ERROR_DESCRIPTION: {err_msg}")
            else:
                logging.warning("Keine @ERROR_DESCRIPTION vom Controller erhalten.")
        except Exception as e:
            logging.warning(f"Fehler beim Auslesen von @ERROR_DESCRIPTION: {e}")
