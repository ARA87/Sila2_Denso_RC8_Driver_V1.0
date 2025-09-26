import logging
from typing import List, Dict, Optional
try:
    from .pybcapclient import bcapclient  
    from .pybcapclient.orinexception import ORiNException
except ImportError:
    
    import pybcapclient.bcapclient as bcapclient
    from pybcapclient.orinexception import ORiNException


class DensoRC8Controller:
    def __init__(self):
        self.ip: Optional[str] = None
        self.port: Optional[int] = None
        self.timeout: Optional[int] = None

        self.bcap = None
        self.h_ctrl = None
        self.h_task = None  

        # Global Variable-Handles
        self.IO = None
        self.S = None
        self.I = None
        self.F = None
        self.P = None
        self.J = None
        self.V = None

        # Robot/Position
        self.Robot = None
        self.Pos = None

        # --- observable STATUS-Property / Multi-Task ---
        self.task_handles: Dict[str, object] = {}
        self.task_status_vars: Dict[str, object] = {}
        self.current_program_name: Optional[str] = None

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

            # IO variables
            count_io_vars = 500
            self.IO = {i: self.bcap.controller_getvariable(self.h_ctrl, f"IO{i}", '') for i in range(count_io_vars)}
            logging.info("Connection started: %d IO variables loaded.", count_io_vars)

            # S variables
            count_s_vars = 48
            self.S = {i: self.bcap.controller_getvariable(self.h_ctrl, f"S{i}", '') for i in range(count_s_vars)}
            logging.info("Connection started: %d S variables loaded.", count_s_vars)

            # I variables
            count_i_vars = 98
            self.I = {i: self.bcap.controller_getvariable(self.h_ctrl, f"I{i}", '') for i in range(count_i_vars)}
            logging.info("Connection started: %d I variables loaded.", count_i_vars)

            # F variables
            count_f_vars = 98
            self.F = {i: self.bcap.controller_getvariable(self.h_ctrl, f"F{i}", '') for i in range(count_f_vars)}
            logging.info("Connection started: %d F variables loaded.", count_f_vars)

            # P variables
            count_p_vars = 98
            self.P = {i: self.bcap.controller_getvariable(self.h_ctrl, f"P{i}", '') for i in range(count_p_vars)}
            logging.info("Connection started: %d P variables loaded.", count_p_vars)

            # J variables
            count_j_vars = 98
            self.J = {i: self.bcap.controller_getvariable(self.h_ctrl, f"J{i}", '') for i in range(count_j_vars)}
            logging.info("Connection started: %d J variables loaded.", count_j_vars)

            # V variables
            count_v_vars = 48
            self.V = {i: self.bcap.controller_getvariable(self.h_ctrl, f"V{i}", '') for i in range(count_v_vars)}
            logging.info("Connection started: %d V variables loaded.", count_v_vars)

            # Robot
            self.Robot = self.bcap.controller_getrobot(self.h_ctrl, "Arm", "")

            # Current position
            self.Pos = self.bcap.robot_getvariable(self.Robot, "@CURRENT_POSITION", '')
            logging.info("Connection started: Current position handle loaded.")

        except ORiNException as e:
            logging.error(f"ORiNException during startup: {e}")
            self._log_error_description()
            raise
        except Exception:
            logging.exception("General error during startup")
            self._log_error_description()
            raise

    # --- Position ---
    def get_pos_value(self) -> List[float]:
        if self.Pos is None:
            raise RuntimeError("Position not initialized")
        retval = self.bcap.variable_getvalue(self.Pos)
        logging.info("Current position read: %s", retval)
        return retval

    # --- S values ---
    def set_s_value(self, Index: int, value: str):
        if self.S is None or Index not in self.S:
            raise RuntimeError(f"S{Index} not initialized. Call start() first.")
        self.bcap.variable_putvalue(self.S[Index], value)
        logging.info("S%d set to: %s", Index, value)

    def get_s_value(self, Index: int) -> str:
        if self.S is None or Index not in self.S:
            raise RuntimeError(f"S{Index} not initialized. Call start() first.")
        retval = self.bcap.variable_getvalue(self.S[Index])
        logging.info("S%d read: %s", Index, retval)
        return retval

    # --- I values ---
    def set_I_value(self, Index: int, value: int):
        if self.I is None or Index not in self.I:
            raise RuntimeError(f"I{Index} not initialized. Call start() first.")
        self.bcap.variable_putvalue(self.I[Index], value)
        logging.info("I%d set to: %s", Index, value)

    def get_I_value(self, Index: int) -> int:
        if self.I is None or Index not in self.I:
            raise RuntimeError(f"I{Index} not initialized. Call start() first.")
        retval = self.bcap.variable_getvalue(self.I[Index])
        logging.info("I%d read: %s", Index, retval)
        return retval

    # --- IO values ---
    def set_IO_value(self, Index: int, value: int):
        if self.IO is None or Index not in self.IO:
            raise RuntimeError(f"IO{Index} not initialized. Call start() first.")
        self.bcap.variable_putvalue(self.IO[Index], value)
        logging.info("IO%d set to: %s", Index, value)

    def get_IO_value(self, Index: int) -> int:
        if self.IO is None or Index not in self.IO:
            raise RuntimeError(f"IO{Index} not initialized. Call start() first.")
        retval = self.bcap.variable_getvalue(self.IO[Index])
        logging.info("IO%d read: %s", Index, retval)
        return retval

    # --- F values ---
    def set_F_value(self, Index: int, value: float):
        if self.F is None or Index not in self.F:
            raise RuntimeError(f"F{Index} not initialized. Call start() first.")
        self.bcap.variable_putvalue(self.F[Index], value)
        logging.info("F%d set to: %s", Index, value)

    def get_F_value(self, Index: int) -> float:
        if self.F is None or Index not in self.F:
            raise RuntimeError(f"F{Index} not initialized. Call start() first.")
        retval = self.bcap.variable_getvalue(self.F[Index])
        logging.info("F%d read: %s", Index, retval)
        return retval

    # --- P values (List of floats) ---
    def set_P_value(self, Index: int, value: List[float]):
        if self.P is None or Index not in self.P:
            raise RuntimeError(f"P{Index} not initialized. Call start() first.")
        self.bcap.variable_putvalue(self.P[Index], value)
        logging.info("P%d set to: %s", Index, value)

    def get_P_value(self, Index: int) -> List[float]:
        if self.P is None or Index not in self.P:
            raise RuntimeError(f"P{Index} not initialized. Call start() first.")
        retval = self.bcap.variable_getvalue(self.P[Index])
        logging.info("P%d read: %s", Index, retval)
        return retval

    # --- J values (List of floats) ---
    def set_J_value(self, Index: int, value: List[float]):
        if self.J is None or Index not in self.J:
            raise RuntimeError(f"J{Index} not initialized. Call start() first.")
        self.bcap.variable_putvalue(self.J[Index], value)
        logging.info("J%d set to: %s", Index, value)

    def get_J_value(self, Index: int) -> List[float]:
        if self.J is None or Index not in self.J:
            raise RuntimeError(f"J{Index} not initialized. Call start() first.")
        retval = self.bcap.variable_getvalue(self.J[Index])
        logging.info("J%d read: %s", Index, retval)
        return retval

    # --- V values (List of floats) ---
    def set_V_value(self, Index: int, value: List[float]):
        if self.V is None or Index not in self.V:
            raise RuntimeError(f"V{Index} not initialized. Call start() first.")
        self.bcap.variable_putvalue(self.V[Index], value)
        logging.info("V%d set to: %s", Index, value)

    def get_V_value(self, Index: int) -> List[float]:
        if self.V is None or Index not in self.V:
            raise RuntimeError(f"V{Index} not initialized. Call start() first.")
        retval = self.bcap.variable_getvalue(self.V[Index])
        logging.info("V%d read: %s", Index, retval)
        return retval

    def get_program(self, program_name: str):
        """
        Robust: Reuse existing (validated) handles if possible,
        otherwise resolve fresh and rebind @STATUS.
        Prevents ORiNException -2147483131 ("Object already exists").
        """
        
        if program_name.lower().endswith(".pcs"):
            program_name = program_name[:-4]

        
        h_cached = self.task_handles.get(program_name)
        v_cached = self.task_status_vars.get(program_name)
        if h_cached and v_cached:
            try:
                # read @STATUS 
                _ = self.bcap.variable_getvalue(v_cached)
                
                self.h_task = h_cached
                self.current_program_name = program_name
                logging.info("Program '%s' reused (validated cached handle + @STATUS).", program_name)
                return
            except Exception:
                #  Cache is probably stale -> we will resolve it fresh
                logging.info("Program '%s' cached handle seems stale, resolving fresh…", program_name)
                try:
                    # Optional: ignore/overwrite old handle
                    pass
                except Exception:
                    pass

        # 2) Dissolve fresh
        try:
            h_task = self.bcap.controller_gettask(self.h_ctrl, program_name, "")
            v_status = self.bcap.task_getvariable(h_task, "@STATUS", "")
            if not v_status:
                raise RuntimeError(f"Task '{program_name}' has no @STATUS variable.")

            # update Cache  
            self.task_handles[program_name] = h_task
            self.task_status_vars[program_name] = v_status
            self.h_task = h_task
            self.current_program_name = program_name
            logging.info("Program '%s' resolved fresh (handle + @STATUS).", program_name)
            return

        except ORiNException as e:
            # -2147483131: "Object already exists" -> handle already exists
            try:
                code = int(e.args[0])
            except Exception:
                code = None

            if code == -2147483131:
                logging.info("ORiN -2147483131 for '%s': reusing existing handle if possible…", program_name)
                # Try to use cache (even if validation above failed)
                h_cached = self.task_handles.get(program_name)
                v_cached = self.task_status_vars.get(program_name)
                if h_cached and v_cached:
                    try:
                        _ = self.bcap.variable_getvalue(v_cached)  # last validation
                        self.h_task = h_cached
                        self.current_program_name = program_name
                        logging.info("Program '%s' reused after ORiN -2147483131.", program_name)
                        return
                    except Exception:
                        pass
                # if cache unavailable -> ErrorMessage
                logging.error("Could not reuse handle for '%s' after -2147483131.", program_name)
                self._log_error_description()
                raise
            else:
                logging.error("ORiNException while retrieving task '%s': %s", program_name, e)
                self._log_error_description()
                raise

    def start_program(self, program_name: str, mode: str):
        """
        Startet den Task zum angegebenen Programm. Nutzt das passende Handle.
        """
        mode_map = {"one_cycle": 1, "continuous": 2, "step_forward": 3}
        if mode not in mode_map:
            raise ValueError(f"Invalid Modus: {mode}. Erlaubt: {list(mode_map.keys())}")

        # Handle 
        if program_name not in self.task_handles:
            self.get_program(program_name)

        handle = self.task_handles[program_name]
        self.h_task = handle
        self.current_program_name = program_name

        self.bcap.task_start(handle, mode_map[mode], "")
        logging.info("Programm '%s' gestartet im Modus '%s'", program_name, mode)

    def stop_program(self, program_name: str, mode: str):
        """
        Stoppt den Task. Nutzt das passende Handle.
        """
        mode_map = {"default_stop": 0, "instant_stop": 1, "step_stop": 2, "cycle_stop": 3}
        if mode not in mode_map:
            raise ValueError(f"Invalid Mode: {mode}. allowed: {list(mode_map.keys())}")

        # Handle 
        if program_name not in self.task_handles:
            self.get_program(program_name)

        handle = self.task_handles[program_name]
        self.h_task = handle
        self.current_program_name = program_name

        self.bcap.task_stop(handle, mode_map[mode], "")
        logging.info("Programm '%s' stopeed in Mode '%s'", program_name, mode)

    # --- Error Handling ---
    def _log_error_description(self):
        if not self.h_ctrl:
            logging.warning("No Controller-Handle for Error Message.")
            return
        try:
            err_var = self.bcap.controller_getvariable(self.h_ctrl, "@ERROR_DESCRIPTION", "")
            err_msg = self.bcap.variable_getvalue(err_var)
            if err_msg:
                logging.error("RC8 @ERROR_DESCRIPTION: %s", err_msg)
            else:
                logging.warning("No @ERROR_DESCRIPTION.")
        except Exception as e:
            logging.warning("Error while reading @ERROR_DESCRIPTION: %s", e)
