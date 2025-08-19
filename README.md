# SiLA 2 Driver for Denso RC8

This driver implements a SiLA 2 interface for controlling a Denso RC8 robot via the BCAP protocol.

## Features

- Connects to the Denso RC8 robot using fixed IP address and port
- Read and write Global Controller-variables (e.g., String, Float Integer, Position, Joint,Vector)
- Start and control robot tasks (e.g., task "Pro1")
- Error handling with ORiN exceptions
- Logs all actions and errors to `denso_rc8.log`

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
The driver uses a self-signed TLS certificate for secure communication between the SiLA 2 client and server.

Included Certificate
The project includes a default self-signed certificate located in the certs/ folder (server.crt and server.key).

This certificate is used by the SiLA 2 server for TLS encryption.

Generating a New Self-Signed Certificate
If you want to generate a new certificate, you can do so with OpenSSL:

bash
Copy
Edit
openssl req -x509 -newkey rsa:4096 -keyout server.key -out server.crt -days 365 -nodes
When prompted, fill in the details (Country, Organization, Common Name, etc.).

Place the generated server.key and server.crt files in the certs/ folder or update your server configuration to point to their location.

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

