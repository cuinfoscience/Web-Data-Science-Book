"""Rebuild boulder-ca-bundle.pem, the certificate bundle chapter 9 passes to requests as verify=.

documents.bouldercolorado.gov sends its own certificate but not the intermediate certificate
that links it to a root (DigiCert Global G2 TLS RSA SHA256 2020 CA1). Browsers fetch or cache
the missing intermediate; Python doesn't, so requests fails with CERTIFICATE_VERIFY_FAILED.
This bundle is certifi's roots plus that intermediate, so verification stays on.

Run it from the repository root after certifi updates:

    python data/ch-09/make_ca_bundle.py
"""
import hashlib
import ssl
from datetime import date
from pathlib import Path

import certifi
import requests

# The address in the server certificate's Authority Information Access field, over HTTPS
INTERMEDIATE_URL = "https://cacerts.digicert.com/DigiCertGlobalG2TLSRSASHA2562020CA1-1.crt"
HEADERS = {"User-Agent": "WebDataScience/1.0 (brian.keegan@colorado.edu)"}
OUT = Path(__file__).with_name("boulder-ca-bundle.pem")

response = requests.get(INTERMEDIATE_URL, headers=HEADERS, timeout=30)
response.raise_for_status()
der = response.content
pem = ssl.DER_cert_to_PEM_cert(der)  # the file is DER (binary); a bundle needs PEM (text)

header = (
    f"# Chapter 9's bundle for documents.bouldercolorado.gov, built {date.today()} by make_ca_bundle.py\n"
    f"# certifi {certifi.__version__}'s roots, then the intermediate from {INTERMEDIATE_URL}\n"
    f"# intermediate sha256 (DER): {hashlib.sha256(der).hexdigest()}\n"
)
roots = Path(certifi.where()).read_text()
OUT.write_text(header + roots.rstrip("\n") + "\n\n# DigiCert Global G2 TLS RSA SHA256 2020 CA1\n" + pem)
print(f"wrote {OUT} ({OUT.stat().st_size:,} bytes)")
