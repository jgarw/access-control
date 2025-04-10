"""
hash.py

Overview:
Defines method used for hashing IDs using SHA256
"""

import hashlib

# Hashes ID passed as parameter using SHA256
def hash_tag(rfid_tag):
    return hashlib.sha256(rfid_tag.encode('utf-8')).hexdigest()