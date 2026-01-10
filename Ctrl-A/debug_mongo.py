
import pymongo
from pymongo import MongoClient
import ssl
import certifi
import sys

uri = "mongodb+srv://aditya2006:adi2006@cluster0.xdbxki9.mongodb.net/gov_access?retryWrites=true&w=majority&appName=Cluster0"

print(f"Python: {sys.version}")
print(f"PyMongo: {pymongo.version}")
print(f"OpenSSL: {ssl.OPENSSL_VERSION}")

def test_connection(name, **kwargs):
    print(f"\n--- Testing {name} ---")
    print(f"Params: {kwargs}")
    try:
        client = MongoClient(uri, **kwargs)
        client.admin.command('ping')
        print("✅ SUCCESS!")
        return True
    except Exception as e:
        print(f"❌ FAILED: {e}")
        return False

# Test 1: Default
test_connection("Default")

# Test 2: certifi
test_connection("Certifi", tlsCAFile=certifi.where())

# Test 3: Insecure
test_connection("Insecure (tlsAllowInvalidCertificates)", tls=True, tlsAllowInvalidCertificates=True)

# Test 4: SSL (Legacy)
try:
    test_connection("SSL (Legacy)", ssl=True, ssl_cert_reqs=ssl.CERT_NONE)
except:
    print("Skipping SSL Legacy test")

