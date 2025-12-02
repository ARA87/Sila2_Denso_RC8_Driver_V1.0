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
        self.Robot: Any = None  # halten wir als einziges Handle dauerhaft

        # Task- / Status-Handles (werden gecached, aber nicht released)
        self.task_handles: Dict[str, Any] = {}
        self.task_status_vars: Dict[str, Any] = {}
        self.current_program_name: Optional[str] = None

        # Thread-Schutz v. a. für Task-Handles
        self._lock = threading.RLock()

    # ---------------------- Verbindung ----------------------

    def configure_connection(self, ip: str, port: int, timeout: int):
        self.ip = ip
        self.port = port
        self.timeout = timeout

    def _require(self):
        if self.bcap is None or self.h_ctrl is None:
            raise RuntimeError("Controller not started. Call start() first.")

    def start(self):
        """
        Baut die b-CAP Verbindung + Controller-Handle auf.
        KEINE Variable-Handles werden global gecached; alle Variablen-Handles
        werden bei Bedarf pro Zugriff geholt und sofort wieder freigegeben.
        """
        if not all([self.ip, self.port, self.timeout]):
            raise RuntimeError("Connection not configured. Call configure_connection() first.")
        try:
            self.bcap = bcapclient.BCAPClient(host=self.ip, port=self.port, timeout=self.timeout)
            self.bcap.service_start('')

            # Provider/Machine/Option wie bisher:
            self.h_ctrl = self.bcap.controller_connect(
                name='',
                provider='CaoProv.DENSO.VRC',
                machine='localhost',
                option=''
            )

            logging.info("Controller connected (on-demand variable handles, no caching).")

            # Robot-Handle optional lazy holen – wir machen es hier direkt,
            # behalten aber nur dieses eine Robot-Objekt.
            try:
                self.Robot = self.bcap.controller_getrobot(self.h_ctrl, "Arm", "")
                logging.info("Robot handle initialized.")
            except ORiNException as e:
                logging.warning("Could not get Robot handle at startup: %r", e)
                # Robot wird bei Bedarf in get_pos_value() nachgezogen

        except ORiNException as e:
            logging.error(f"ORiNException during startup: {e}")
            self._log_error_description()
            raise
        except Exception:
            logging.exception("General error during startup")
            self._log_error_description()
            raise

    # ---------------------- kleine Helper für Variablen ----------------------

    def _with_controller_variable(self, name: str, op, log_prefix: str = ""):
        """
        Hole einen Controller-Variablenhandle, führe Operation aus, release immer.

        op: Callable(handle) -> Any
        """
        self._require()
        h_var = None
        try:
            h_var = self.bcap.controller_getvariable(self.h_ctrl, name, "")
            return op(h_var)
        finally:
            if h_var is not None:
                try:
                    self.bcap.variable_release(h_var)
                except Exception as e:
                    logging.debug("variable_release(%s) failed: %r", name, e)

    # ---------------------- Position ----------------------

    def get_pos_value(self) -> List[float]:
        """
        Liest @CURRENT_POSITION.
        Robot-Handle wird (falls nicht vorhanden) einmalig geholt und gehalten.
        Positions-Variable wird pro Aufruf geholt und direkt wieder freigegeben.
        """
        self._require()
        # Robot-Handle lazy nachziehen, falls beim Start fehlschlug
        if self.Robot is None:
            try:
                self.Robot = self.bcap.controller_getrobot(self.h_ctrl, "Arm", "")
                logging.info("Robot handle resolved lazily in get_pos_value().")
            except ORiNException as e:
                logging.error("ORiNException while getting Robot handle: %r", e)
                self._log_error_description()
                raise

        h_pos = None
        try:
            h_pos = self.bcap.robot_getvariable(self.Robot, self._CUR_POS_VAR, "")
            retval = self.bcap.variable_getvalue(h_pos)
            logging.info("Current position read: %s", retval)
            return retval
        finally:
            if h_pos is not None:
                try:
                    self.bcap.variable_release(h_pos)
                except Exception as e:
                    logging.debug("variable_release(@CURRENT_POSITION) failed: %r", e)

    # ---------------------- Task Names ----------------------

    def get_task_names(self) -> List[str]:
        """
        Returns the list of PAC task names that can be specified in AddTask /
        StartProgram (wraps b-CAP Controller_GetTaskNames / CaoController::get_TaskNames).
        """
        self._require()
        raw = self.bcap.controller_gettasknames(self.h_ctrl)

        if isinstance(raw, (list, tuple)):
            names = [str(x) for x in raw]
        elif raw is None:
            names = []
        else:
            names = [str(raw)]

        logging.info("Available task names: %s", names)
        return names

    # ---------------------- S values ----------------------

    def set_s_value(self, Index: int, value: str):
        name = f"S{Index}"
        def _op(h):
            self.bcap.variable_putvalue(h, value)
            logging.info("%s set to: %s", name, value)
        self._with_controller_variable(name, _op, log_prefix="S")

    def get_s_value(self, Index: int) -> str:
        name = f"S{Index}"
        def _op(h):
            retval = self.bcap.variable_getvalue(h)
            logging.info("%s read: %s", name, retval)
            return retval
        return self._with_controller_variable(name, _op, log_prefix="S")

    # ---------------------- I values ----------------------

    def set_I_value(self, Index: int, value: int):
        name = f"I{Index}"
        def _op(h):
            self.bcap.variable_putvalue(h, value)
            logging.info("%s set to: %s", name, value)
        self._with_controller_variable(name, _op, log_prefix="I")

    def get_I_value(self, Index: int) -> int:
        name = f"I{Index}"
        def _op(h):
            retval = self.bcap.variable_getvalue(h)
            logging.info("%s read: %s", name, retval)
            return retval
        return self._with_controller_variable(name, _op, log_prefix="I")

    # ---------------------- IO values ----------------------

    def set_IO_value(self, Index: int, value: int):
        name = f"IO{Index}"
        def _op(h):
            self.bcap.variable_putvalue(h, value)
            logging.info("%s set to: %s", name, value)
        self._with_controller_variable(name, _op, log_prefix="IO")

    def get_IO_value(self, Index: int) -> int:
        name = f"IO{Index}"
        def _op(h):
            retval = self.bcap.variable_getvalue(h)
            logging.info("%s read: %s", name, retval)
            return retval
        return self._with_controller_variable(name, _op, log_prefix="IO")

    # ---------------------- F values ----------------------

    def set_F_value(self, Index: int, value: float):
        name = f"F{Index}"
        def _op(h):
            self.bcap.variable_putvalue(h, value)
            logging.info("%s set to: %s", name, value)
        self._with_controller_variable(name, _op, log_prefix="F")

    def get_F_value(self, Index: int) -> float:
        name = f"F{Index}"
        def _op(h):
            retval = self.bcap.variable_getvalue(h)
            logging.info("%s read: %s", name, retval)
            return retval
        return self._with_controller_variable(name, _op, log_prefix="F")

    # ---------------------- P values (List of floats) ----------------------

    def set_P_value(self, Index: int, value: List[float]):
        name = f"P{Index}"
        def _op(h):
            self.bcap.variable_putvalue(h, value)
            logging.info("%s set to: %s", name, value)
        self._with_controller_variable(name, _op, log_prefix="P")

    def get_P_value(self, Index: int) -> List[float]:
        name = f"P{Index}"
        def _op(h):
            retval = self.bcap.variable_getvalue(h)
            logging.info("%s read: %s", name, retval)
            return retval
        return self._with_controller_variable(name, _op, log_prefix="P")

    # ---------------------- J values (List of floats) ----------------------

    def set_J_value(self, Index: int, value: List[float]):
        name = f"J{Index}"
        def _op(h):
            self.bcap.variable_putvalue(h, value)
            logging.info("%s set to: %s", name, value)
        self._with_controller_variable(name, _op, log_prefix="J")

    def get_J_value(self, Index: int) -> List[float]:
        name = f"J{Index}"
        def _op(h):
            retval = self.bcap.variable_getvalue(h)
            logging.info("%s read: %s", name, retval)
            return retval
        return self._with_controller_variable(name, _op, log_prefix="J")

    # ---------------------- V values (List of floats) ----------------------

    def set_V_value(self, Index: int, value: List[float]):
        name = f"V{Index}"
        def _op(h):
            self.bcap.variable_putvalue(h, value)
            logging.info("%s set to: %s", name, value)
        self._with_controller_variable(name, _op, log_prefix="V")

    def get_V_value(self, Index: int) -> List[float]:
        name = f"V{Index}"
        def _op(h):
            retval = self.bcap.variable_getvalue(h)
            logging.info("%s read: %s", name, retval)
            return retval
        return self._with_controller_variable(name, _op, log_prefix="V")

    # ---------------------- Programme / Tasks ----------------------

    def get_program(self, program_name: str):
        """
        Handle + @STATUS binden, Cache nutzen.
        (Task-Handles bleiben gecached; die Anzahl ist typischerweise klein.)
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
            try:
                msg = self.bcap.variable_getvalue(h_desc)
            finally:
                try:
                    self.bcap.variable_release(h_desc)
                except Exception:
                    pass
            if msg:
                logging.error("RC8 %s: %s", self._ERR_DESC_VAR, msg)
            else:
                logging.debug("No %s available.", self._ERR_DESC_VAR)
        except Exception as e:
            logging.debug("Error while reading %s: %s", self._ERR_DESC_VAR, e)

    # ---------------------- Optional: Cache-Management ----------------------

    def invalidate_variable_cache(self, prefix: Optional[str] = None):
        """
        Für das neue Design ohne Variablen-Cache praktisch ein No-Op.
        Bleibt nur drin, falls von außen aufgerufen wird.
        """
        logging.info("invalidate_variable_cache(%r) called – no cached variable handles in this design.", prefix)

    def invalidate_program_cache(self, program_name: Optional[str] = None):
        with self._lock:
            if program_name is None:
                self.task_handles.clear()
                self.task_status_vars.clear()
            else:
                self.task_handles.pop(program_name, None)
                self.task_status_vars.pop(program_name, None)
