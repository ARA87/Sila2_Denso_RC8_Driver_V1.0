# driver/denso_rc8_controller.py
import logging
import pybcapclient.bcapclient as bcapclient
from pybcapclient.orinexception import ORiNException


# Logging-Konfiguration (einmalig, wird Logdatei im Projektverzeichnis erzeugen)
logging.basicConfig(
    filename="denso_rc8.log",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

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
        try:
            self.bcap = bcapclient.BCAPClient(host=self.ip, port=self.port, timeout=self.timeout)
            self.bcap.service_start('')

            self.h_ctrl = self.bcap.controller_connect(
                name='',
                provider='CaoProv.DENSO.VRC',
                machine='localhost',
                option=''
        )
        
            
            # Dynamische Zuweisung von S-Variablen
            self.S = {}
            for Index in range(0, 49):  # oder nur [10,11,...]
                var_name = f"S{Index}"
                self.S[Index] = self.bcap.controller_getvariable(self.h_ctrl, var_name, '')
                logging.info("Verbindung zum RC8 erfolgreich gestartet.")
            
        except ORiNException as e:
            logging.error("ORiNException beim Start: %s", str(e))
            self._log_error_description()
            raise

        except Exception as e:
            logging.exception("Allgemeiner Fehler beim Start")
            raise

    def set_s_value(self, Index:int, value: str):
        if self.S is None or Index not in self.S:
            raise RuntimeError(f"S{Index} not initialized. Call start() first.")
        try:    
            self.bcap.variable_putvalue(self.S[Index], value)
            logging.info("S%d gesetzt auf: %s", Index, value)

        except ORiNException as e:
            logging.error("ORiNException beim Setzen von S%d: %s", Index, str(e))
            self._log_error_description()
            raise

        except Exception as e:
            logging.exception("Fehler beim Setzen von S%d", Index)
            raise

    def get_s_value(self, Index:int) -> str:
        if self.S is None or Index not in self.S:
            raise RuntimeError(f"S{Index} not initialized. Call start() first.")
        try:
            retval = self.bcap.variable_getvalue(self.S[Index])
            logging.info("S%d gelesen: %s", Index, retval)
            return retval
            
        except ORiNException as e:
            logging.error("ORiNException beim Lesen von S%d: %s", Index, str(e))
            self._log_error_description()
            raise

        except Exception as e:
            logging.exception("Fehler beim Lesen von S%d", Index)
            raise

    def _log_error_description(self):
        """Liest @ERROR-Description vom Controller und loggt sie."""
        try:
            if self.h_ctrl:
                err_var = self.bcap.controller_getvariable(self.h_ctrl, "@ERROR-Description", "")
                err_msg = self.bcap.variable_getvalue(err_var)
                logging.error("RC8 @ERROR-Description: %s", err_msg)
            else:
                logging.warning("Kein Controller-Handle vorhanden für Fehlerbeschreibung.")
        except Exception as e:
            logging.warning("Fehler beim Auslesen von @ERROR-Description: %s", str(e))