from cryptography import x509
from cryptography.x509.oid import NameOID, ObjectIdentifier
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from datetime import datetime, timedelta
import argparse
import uuid

def generate_certificate(uuid_str, host="localhost", cert_path="cert.pem", key_path="key.pem"):
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)

    subject = issuer = x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, u"DE"),
        x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, u"Berlin"),
        x509.NameAttribute(NameOID.LOCALITY_NAME, u"Berlin"),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, u"My SiLA2 Server"),
        x509.NameAttribute(NameOID.COMMON_NAME, host),
    ])

    uuid_bytes = uuid.UUID(uuid_str).bytes

    # Offizielle OID für SiLA2 UUID: 1.3.6.1.4.1.58583
    sila_uuid_oid = ObjectIdentifier("1.3.6.1.4.1.58583")

    cert = x509.CertificateBuilder()\
        .subject_name(subject)\
        .issuer_name(issuer)\
        .public_key(private_key.public_key())\
        .serial_number(x509.random_serial_number())\
        .not_valid_before(datetime.utcnow())\
        .not_valid_after(datetime.utcnow() + timedelta(days=365))\
        .add_extension(
            x509.UnrecognizedExtension(sila_uuid_oid, uuid_bytes),
            critical=False
        )\
        .sign(private_key, hashes.SHA256())

    with open(cert_path, "wb") as f:
        f.write(cert.public_bytes(serialization.Encoding.PEM))

    with open(key_path, "wb") as f:
        f.write(private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption()
        ))

    print(f"✅ Zertifikat mit UUID ({uuid_str}) erfolgreich erzeugt.")
    print(f"🔐 Gespeichert als: {cert_path}, {key_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--uuid", required=True, help="UUID for the SiLA2 server")
    parser.add_argument("--host", default="localhost", help="Hostname")
    parser.add_argument("--cert", default="cert.pem", help="Path to certificate")
    parser.add_argument("--key", default="key.pem", help="Path to private key")
    args = parser.parse_args()

    generate_certificate(args.uuid, args.host, args.cert, args.key)
