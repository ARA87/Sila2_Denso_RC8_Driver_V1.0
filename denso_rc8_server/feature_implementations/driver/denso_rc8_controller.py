import logging
import threading
from typing import List, Dict, Optional, Any

try:
    from .pybcapclient import bcapclient
    from .pybcapclient.orinexception import ORiNException
except ImportError:
    import pybcapclient.bcapclient as bcapclient
    from pybcapclient.orinexception import ORiNException


class DensoRC8Controller:


    # ---- Konstanten ----
    _STATUS_VAR = "@STATUS"
    _ERR_CODE_VAR = "@ERROR_CODE"
    _ERR_DESC_VAR = "@ERROR_DESCRIPTION"
    _CUR_POS_VAR = "@CURRENT_POSITION"

    def __init__(self):
        # Verbindungs-Parameter
        self.ip: Optional[str] = None
        self.port: Optional[int] = None
        self.timeout: Optional[int] = None

        # b-CAP Objekte
        self.bcap: Optional[bcapclient.BCAPClient] = None
        self.h_ctrl: Any = None
        self.Robot: Any = None

        # Lazy-Cache für Variablenhandles
        # z.B. self._var_cache["IO"][1] -> Handle für "IO1"
        self._var_cache: Dict[str, Dict[int, Any]] = {
            "IO": {}, "S": {}, "I": {}, "F": {}, "P": {}, "J": {}, "V": {}
        }

        # Positionshandle (lazy)
        self._pos_handle: Any = None

        # Task- / Status-Handles
        self.task_handles: Dict[str, Any] = {}
        self.task_status_vars: Dict[str, Any] = {}
        self.current_program_name: Optional[str] = None

        # Thread-Schutz für Lazy-Caches
        self._lock = threading.RLock()

    # ---------------------- Verbindung ----------------------

    def configure_connection(self, ip: str, port: int, timeout: int):
        self.ip = ip
        self.port = port
        self.timeout = timeout

    def start(self):
        """
        Baut NUR die b-CAP Verbindung + Controller-Handle auf.
        KEIN Preload von Variablen/Roboter/Position (alles lazy).
        """
        if not all([self.ip, self.port, self.timeout]):
            raise RuntimeError("Connection not configured. Call configure_connection() first.")
        try:
            self.bcap = bcapclient.BCAPClient(host=self.ip, port=self.port, timeout=self.timeout)
            self.bcap.service_start('')

            # Provider/Machine/Option wie in deinem bisherigen Setup (unverändert):
            self.h_ctrl = self.bcap.controller_connect(
                name='',
                provider='CaoProv.DENSO.VRC',
                machine='localhost',
                option=''
            )

            logging.info("Connection started (lazy handle mode).")

        except ORiNException as e:
            logging.error(f"ORiNException during startup: {e}")
            self._log_error_description()
            raise
        except Exception:
            logging.exception("General error during startup")
            self._log_error_description()
            raise

    # ---------------------- Lazy Helpers ----------------------

    def _require(self):
        if self.bcap is None or self.h_ctrl is None:
            raise RuntimeError("Controller not started. Call start() first.")

    def _get_robot(self):
        """
        Lazy: holt bei Bedarf das Robot-Handle 'Arm'.
        """
        self._require()
        with self._lock:
            if self.Robot is None:
                self.Robot = self.bcap.controller_getrobot(self.h_ctrl, "Arm", "")
                logging.info("Robot handle resolved lazily.")
            return self.Robot

    def _get_pos_handle(self):
        """
        Lazy: holt bei Bedarf das Positionshandle @CURRENT_POSITION.
        """
        self._require()
        with self._lock:
            if self._pos_handle is None:
                robot = self._get_robot()
                self._pos_handle = self.bcap.robot_getvariable(robot, self._CUR_POS_VAR, '')
                logging.info("@CURRENT_POSITION handle resolved lazily.")
            return self._pos_handle

    def _get_var_handle(self, prefix: str, index: int):
        """
        Lazy: holt bei Bedarf ein Variablenhandle (IO/S/I/F/P/J/V).
        """
        self._require()
        if prefix not in self._var_cache:
            raise ValueError(f"Unsupported variable prefix '{prefix}'")
        with self._lock:
            cache = self._var_cache[prefix]
            h = cache.get(index)
            if h is None:
                name = f"{prefix}{index}"
                h = self.bcap.controller_getvariable(self.h_ctrl, name, '')
                cache[index] = h
                logging.debug("Handle for %s cached.", name)
            return h

    # ---------------------- Position ----------------------

    def get_pos_value(self) -> List[float]:
        h = self._get_pos_handle()
        retval = self.bcap.variable_getvalue(h)
        logging.info("Current position read: %s", retval)
        return retval


    # ---------------------- Task Names ----------------------

    def get_task_names(self) -> List[str]:
        """
        Returns the list of PAC task names that can be specified in AddTask /
        StartProgram (wraps b-CAP Controller_GetTaskNames / CaoController::get_TaskNames).
        """
        self._require()
        # Erwarteter bCAPClient-Call (analog zu Controller_GetTaskNames)
        raw = self.bcap.controller_gettasknames(self.h_ctrl)

        # raw ist typischerweise eine Python-Liste/tuple aus BSTR/str
        if isinstance(raw, (list, tuple)):
            names = [str(x) for x in raw]
        elif raw is None:
            names = []
        else:
            # Falls die Library nur einen einzelnen Wert liefert
            names = [str(raw)]

        logging.info("Available task names: %s", names)
        return names

    # ---------------------- S values ----------------------

    def set_s_value(self, Index: int, value: str):
        h = self._get_var_handle("S", Index)
        self.bcap.variable_putvalue(h, value)
        logging.info("S%d set to: %s", Index, value)

    def get_s_value(self, Index: int) -> str:
        h = self._get_var_handle("S", Index)
        retval = self.bcap.variable_getvalue(h)
        logging.info("S%d read: %s", Index, retval)
        return retval

    # ---------------------- I values ----------------------

    def set_I_value(self, Index: int, value: int):
        h = self._get_var_handle("I", Index)
        self.bcap.variable_putvalue(h, value)
        logging.info("I%d set to: %s", Index, value)

    def get_I_value(self, Index: int) -> int:
        h = self._get_var_handle("I", Index)
        retval = self.bcap.variable_getvalue(h)
        logging.info("I%d read: %s", Index, retval)
        return retval

    # ---------------------- IO values ----------------------

    def set_IO_value(self, Index: int, value: int):
        h = self._get_var_handle("IO", Index)
        self.bcap.variable_putvalue(h, value)
        logging.info("IO%d set to: %s", Index, value)

    def get_IO_value(self, Index: int) -> int:
        h = self._get_var_handle("IO", Index)
        retval = self.bcap.variable_getvalue(h)
        logging.info("IO%d read: %s", Index, retval)
        return retval

    # ---------------------- F values ----------------------

    def set_F_value(self, Index: int, value: float):
        h = self._get_var_handle("F", Index)
        self.bcap.variable_putvalue(h, value)
        logging.info("F%d set to: %s", Index, value)

    def get_F_value(self, Index: int) -> float:
        h = self._get_var_handle("F", Index)
        retval = self.bcap.variable_getvalue(h)
        logging.info("F%d read: %s", Index, retval)
        return retval

    # ---------------------- P values (List of floats) ----------------------

    def set_P_value(self, Index: int, value: List[float]):
        h = self._get_var_handle("P", Index)
        self.bcap.variable_putvalue(h, value)
        logging.info("P%d set to: %s", Index, value)

    def get_P_value(self, Index: int) -> List[float]:
        h = self._get_var_handle("P", Index)
        retval = self.bcap.variable_getvalue(h)
        logging.info("P%d read: %s", Index, retval)
        return retval

    # ---------------------- J values (List of floats) ----------------------

    def set_J_value(self, Index: int, value: List[float]):
        h = self._get_var_handle("J", Index)
        self.bcap.variable_putvalue(h, value)
        logging.info("J%d set to: %s", Index, value)

    def get_J_value(self, Index: int) -> List[float]:
        h = self._get_var_handle("J", Index)
        retval = self.bcap.variable_getvalue(h)
        logging.info("J%d read: %s", Index, retval)
        return retval

    # ---------------------- V values (List of floats) ----------------------

    def set_V_value(self, Index: int, value: List[float]):
        h = self._get_var_handle("V", Index)
        self.bcap.variable_putvalue(h, value)
        logging.info("V%d set to: %s", Index, value)

    def get_V_value(self, Index: int) -> List[float]:
        h = self._get_var_handle("V", Index)
        retval = self.bcap.variable_getvalue(h)
        logging.info("V%d read: %s", Index, retval)
        return retval

    # ---------------------- Programme / Tasks ----------------------

    def get_program(self, program_name: str):
        """
        Handle + @STATUS binden, Cache nutzen. Keine weitere Vorab-Logik.
        """
        self._require()
        if program_name.lower().endswith(".pcs"):
            program_name = program_name[:-4]

        with self._lock:
            h_cached = self.task_handles.get(program_name)
            v_cached = self.task_status_vars.get(program_name)
            if h_cached and v_cached:
                try:
                    _ = self.bcap.variable_getvalue(v_cached)
                    self.current_program_name = program_name
                    logging.info("Program '%s' reused (cached).", program_name)
                    return
                except Exception:
                    logging.info("Program '%s' cached handle stale -> resolve fresh", program_name)

            try:
                h_task = self.bcap.controller_gettask(self.h_ctrl, program_name, "")
                v_status = self.bcap.task_getvariable(h_task, self._STATUS_VAR, "")
                if not v_status:
                    raise RuntimeError(f"Task '{program_name}' has no {self._STATUS_VAR} variable.")

                self.task_handles[program_name] = h_task
                self.task_status_vars[program_name] = v_status
                self.current_program_name = program_name
                logging.info("Program '%s' resolved fresh.", program_name)

            except ORiNException as e:
                # -2147483131: "Object already exists" -> versuchen, Cache zu nutzen
                try:
                    code = int(e.args[0])
                except Exception:
                    code = None
                if code == -2147483131:
                    h_cached = self.task_handles.get(program_name)
                    v_cached = self.task_status_vars.get(program_name)
                    if h_cached and v_cached:
                        try:
                            _ = self.bcap.variable_getvalue(v_cached)
                            self.current_program_name = program_name
                            logging.info("Program '%s' reused after -2147483131.", program_name)
                            return
                        except Exception:
                            pass
                self._log_error_description()
                raise

    def start_program(self, program_name: str, mode: str):
        """
        Startet den Task (Handle muss existieren / wird via get_program() geholt).
        """
        self._require()
        mode_map = {"one_cycle": 1, "continuous": 2, "step_forward": 3}
        if mode not in mode_map:
            raise ValueError(f"Invalid Modus: {mode}. Erlaubt: {list(mode_map.keys())}")

        if program_name not in self.task_handles:
            self.get_program(program_name)

        handle = self.task_handles[program_name]
        self.current_program_name = program_name
        self.bcap.task_start(handle, mode_map[mode], "")
        logging.info("Programm '%s' gestartet im Modus '%s'", program_name, mode)

        # @STATUS ggf. nachziehen (falls vorher nicht vorhanden)
        if program_name not in self.task_status_vars:
            try:
                v_status = self.bcap.task_getvariable(handle, self._STATUS_VAR, "")
                self.task_status_vars[program_name] = v_status
            except Exception:
                pass

    def stop_program(self, program_name: str, mode: str):
        self._require()
        mode_map = {"default_stop": 0, "instant_stop": 1, "step_stop": 2, "cycle_stop": 3}
        if mode not in mode_map:
            raise ValueError(f"Invalid Mode: {mode}. allowed: {list(mode_map.keys())}")

        if program_name not in self.task_handles:
            self.get_program(program_name)

        handle = self.task_handles[program_name]
        self.current_program_name = program_name
        self.bcap.task_stop(handle, mode_map[mode], "")
        logging.info("Programm '%s' stopped in Mode '%s'", program_name, mode)

    # ---------------------- Fehler-Utilities ----------------------

    def _log_error_description(self):
        """
        Liest @ERROR_DESCRIPTION (Best Effort).
        """
        try:
            if not self.h_ctrl:
                logging.warning("No Controller-Handle for Error Message.")
                return
            h_desc = self.bcap.controller_getvariable(self.h_ctrl, self._ERR_DESC_VAR, "")
            msg = self.bcap.variable_getvalue(h_desc)
            if msg:
                logging.error("RC8 %s: %s", self._ERR_DESC_VAR, msg)
            else:
                logging.debug("No %s available.", self._ERR_DESC_VAR)
        except Exception as e:
            logging.debug("Error while reading %s: %s", self._ERR_DESC_VAR, e)

    # ---------------------- Optional: Cache-Management ----------------------

    def invalidate_variable_cache(self, prefix: Optional[str] = None):
        """
        Löscht den Cache für Variablenhandles (z. B. nach Controller-Reset).
        """
        with self._lock:
            if prefix is None:
                for k in self._var_cache:
                    self._var_cache[k].clear()
            else:
                if prefix in self._var_cache:
                    self._var_cache[prefix].clear()

    def invalidate_program_cache(self, program_name: Optional[str] = None):
        with self._lock:
            if program_name is None:
                self.task_handles.clear()
                self.task_status_vars.clear()
            else:
                self.task_handles.pop(program_name, None)
                self.task_status_vars.pop(program_name, None)
