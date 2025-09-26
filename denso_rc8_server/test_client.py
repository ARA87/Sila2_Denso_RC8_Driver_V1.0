# test_client.py
import argparse
import threading
import time
import sys
from pathlib import Path
from typing import Optional, Tuple

from sila2.client import SilaClient

# Mapping der @STATUS-Codes -> Klartext
STATUS_TEXT = {
    0: "NON_EXISTENT",
    1: "HOLD_STOPPED",
    2: "STOPPED",
    3: "RUNNING",
    4: "STEP_STOPPED",
}


class LatestStatus:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._value: Optional[int] = None
        self._seq: int = 0
        self._ev = threading.Event()

    def set(self, v: Optional[int]) -> None:
        with self._lock:
            self._value = v
            self._seq += 1
            self._ev.set()

    def snapshot(self) -> Tuple[Optional[int], int]:
        with self._lock:
            return self._value, self._seq

    def wait_next(self, since_seq: int, timeout: float) -> Optional[Tuple[int, int]]:
        end = time.time() + timeout
        while True:
            with self._lock:
                if self._seq > since_seq:
                    return self._value, self._seq
                self._ev.clear()
            remaining = end - time.time()
            if remaining <= 0:
                return None
            self._ev.wait(timeout=remaining)


def subscribe_global_status(client: SilaClient, stop_evt: threading.Event, latest: LatestStatus):
    try:
        with client.DensoRC8Control.STATUS.subscribe() as sub:
            print("🟢 GLOBAL STATUS subscription opened")
            for value in sub:
                if stop_evt.is_set():
                    break
                latest.set(value)
                txt = STATUS_TEXT.get(value, f"UNKNOWN({value})")
                print(f"📡 STATUS = {value} ({txt})")
    except Exception as e:
        print(f"ℹ️  GLOBAL STATUS subscription ended ({e})")
    finally:
        print("🔴 GLOBAL STATUS subscription closed")


def wait_for_done(instance, name: str, timeout_s: float = 300.0):
    t0 = time.time()
    last_print = 0.0
    while True:
        if instance.done:
            break
        if time.time() - t0 > timeout_s:
            print(f"⏰ {name}: Timeout nach {timeout_s}s (Command nicht beendet)")
            return False, None
        now = time.time()
        if now - last_print > 0.5:
            st = getattr(instance, "status", None)
            pr = getattr(instance, "progress", None)
            print(f"   ⏳ {name}: cmd_status={st} progress={pr}")
            last_print = now
        time.sleep(0.1)

    try:
        resp = instance.get_responses()
        print(f"✅ {name}: result -> Status={resp.Status!r}")
        return True, None
    except Exception as e:
        print(f"❌ {name}: get_responses() failed: {e!r}")
        return True, e


def main():
    ap = argparse.ArgumentParser(description="SiLA2 DensoRC8 dual StartProgram test (alternating STATUS A/B)")
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=50052)
    ap.add_argument("--insecure", action="store_true")
    ap.add_argument("--ca", type=str, default=None)
    ap.add_argument("--ip", type=str, default="127.0.0.1")
    ap.add_argument("--bcap-port", type=int, default=5007)
    ap.add_argument("--timeout", type=int, default=2000)
    ap.add_argument("--prog-a", type=str, default="Pro1")
    ap.add_argument("--prog-b", type=str, default="Pro2")
    ap.add_argument("--mode", type=str, default="one_cycle", choices=["one_cycle", "continuous", "step_forward"])
    ap.add_argument("--cmd-timeout", type=float, default=300.0)
    ap.add_argument("--alt-interval", type=float, default=0.2)
    ap.add_argument("--status-timeout", type=float, default=3.0)
    args = ap.parse_args()

    # --- TLS / insecure ---
    if args.insecure:
        client = SilaClient(args.host, args.port, insecure=True)
        print(f"🔌 Connected insecure to {args.host}:{args.port}")
    else:
        ca_path = Path(args.ca) if args.ca else (Path(__file__).parent / "server" / "cert.pem")
        if not ca_path.is_file():
            raise SystemExit("For TLS provide --ca <server-cert.pem> or place server/cert.pem next to this script.")
        root_certs = ca_path.read_bytes()
        client = SilaClient(args.host, args.port, root_certs=root_certs)
        print(f"🔐 Connected with TLS to {args.host}:{args.port} (CA: {ca_path})")

    try:
        print("⚙️  ConfigureConnection …")
        client.DensoRC8Control.ConfigureConnection(IPAddress=args.ip, Port=args.bcap_port, Timeout=args.timeout)
        print("▶️  Start …")
        client.DensoRC8Control.Start()

        progA = args.prog_a[:-4] if args.prog_a.lower().endswith(".pcs") else args.prog_a
        progB = args.prog_b[:-4] if args.prog_b.lower().endswith(".pcs") else args.prog_b
        print(f"📄 GetProgram('{progA}') …")
        client.DensoRC8Control.GetProgram(ProgramName=progA)
        print(f"📄 GetProgram('{progB}') …")
        client.DensoRC8Control.GetProgram(ProgramName=progB)

        latest = LatestStatus()
        stop_evt = threading.Event()
        t_status = threading.Thread(target=subscribe_global_status, args=(client, stop_evt, latest), daemon=False)
        t_status.start()

        print(f"🎬 StartProgram A: '{progA}', mode='{args.mode}' …")
        instA = client.DensoRC8Control.StartProgram(ProgramName=progA, Mode=args.mode)

        # ⏱️ Neue Zeile: 2 Sekunden warten, bevor Pro2 gestartet wird
        time.sleep(2.0)

        print(f"🎬 StartProgram B: '{progB}', mode='{args.mode}' …")
        instB = client.DensoRC8Control.StartProgram(ProgramName=progB, Mode=args.mode)

        # Rest wie gehabt …
        doneA = False
        doneB = False
        errA = None
        errB = None
        turn_A = True
        print("🔁 Alternierende STATUS-Abfrage (A, B, A, B, …) – bis beide Commands fertig sind")
        while not (doneA and doneB):
            _, seq_before = latest.snapshot()
            prog = progA if turn_A else progB
            label = "A" if turn_A else "B"
            client.DensoRC8Control.GetProgram(ProgramName=prog)
            time.sleep(args.alt_interval)
            res = latest.wait_next(seq_before, timeout=args.status_timeout)
            if res is None:
                print(f"⏳ STATUS[{label}] Timeout")
            else:
                val, new_seq = res
                txt = STATUS_TEXT.get(val, f"UNKNOWN({val})")
                print(f"🔎 STATUS[{label}] -> {val} ({txt}) [seq {new_seq}]")

            if not doneA and instA.done:
                doneA, errA = wait_for_done(instA, "ProA", timeout_s=0.1)
            if not doneB and instB.done:
                doneB, errB = wait_for_done(instB, "ProB", timeout_s=0.1)

            turn_A = not turn_A
            time.sleep(0.05)

        stop_evt.set()
        t_status.join(timeout=2.0)
        print("🔚 Done.")

    finally:
        try:
            close = getattr(client, "close", None)
            if callable(close):
                close()
        except Exception:
            pass
        sys.stdout.flush()


if __name__ == "__main__":
    main()
