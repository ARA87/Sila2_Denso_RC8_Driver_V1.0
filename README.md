# SiLA 2 Driver for Denso RC8

This driver implements a SiLA 2 interface for controlling a Denso RC8 robot via the BCAP protocol.

## Features

- Connects to the Denso RC8 robot using fixed IP address and port
- Read and write Global Controller-variables (e.g., String, Float Integer, Position, Joint,Vector)
- Start and stop robot tasks
- Error handling with ORiN exceptions

## Requirements

- Python 3.8 or higher  
- `pybcapclient` library (manually installed, not available via pip)  
- `sila2` Python library (for SiLA 2 integration)  

## Installation

1. Clone this repository or download the files.  
2. Install dependencies (if not installed):

```bash
pip install sila2
Add the pybcapclient library manually, e.g., place it as a local Python file in your project folder.

TLS Certificate
The driver uses a TLS certificate for communication between the SiLA 2 client and server, for testing purposes you can use a self signed.
The server expects cert.pem and key.pem. There are two ways to provide them:
Option A — Provide paths via CLI (recommended)
python -m sila_driver.denso_rc8_server --ip-address 0.0.0.0 --port 50052 ^
  -c "C:\path\to\cert.pem" -k "C:\path\to\key.pem"

Option B — Place files where the server looks by default

Put the files in one of these locations inside the package:

...\sila_driver\denso_rc8_server\cert.pem and key.pem, or

...\sila_driver\denso_rc8_server\server\cert.pem and key.pem

If no certificate/key can be found, the server will refuse to start in secure mode and tell you where it looked.

(Optional) Quick self-signed certificate with OpenSSL

Create a minimal config with proper SubjectAltName (adjust the host IP):

@"
[ req ]
distinguished_name = dn
x509_extensions = v3_req
prompt = no

[ dn ]
CN = DensoRC8

[ v3_req ]
subjectAltName = @alt_names

[ alt_names ]
DNS.1 = localhost
IP.1  = 127.0.0.1
IP.2  = 192.168.0.10   # <-- replace with your host IP
"@ | Out-File -Encoding ascii .\openssl.cnf


Generate cert & key:

openssl req -x509 -newkey rsa:2048 -days 365 -nodes ^
  -keyout key.pem -out cert.pem -config openssl.cnf


For production, prefer certificates issued by your organization’s CA.

Start the Server
Secure (recommended), bind to all interfaces
python -m sila_driver.denso_rc8_server --ip-address 0.0.0.0 --port 50052 ^
  -c "C:\path\to\cert.pem" -k "C:\path\to\key.pem"


Expected output:

✅ SiLA server 'DensoRC8' listening on 0.0.0.0:50052 (secure=True)


Notes

On first run with 0.0.0.0, Windows may prompt for Firewall access—allow it.

Clients should connect using the host’s LAN IP (e.g., 192.168.x.y:50052), not 127.0.0.1.

Running the Test Client
You can test the driver functionality using the included test client script:

bash
Copy
Edit
python test_client.py
Make sure to:

Configure the IP address, port, and timeout in the test client before running.

Start your SiLA 2 server (driver) before running the client.

License
MIT License

