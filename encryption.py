from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad
import hashlib


def integer_to_aes_key(integer, key_size=32):
    # Convert the integer to bytes (big-endian)
    integer_bytes = integer.to_bytes(
        (integer.bit_length() + 7) // 8, byteorder='big')
    # Hash the bytes
    if key_size <= 16:  # For AES-128
        hashed_bytes = hashlib.sha256(integer_bytes).digest()[:16]
    elif key_size == 24:  # For AES-192
        hashed_bytes = hashlib.sha256(integer_bytes).digest()[:24]
    else:  # For AES-256
        hashed_bytes = hashlib.sha256(integer_bytes).digest()
    return hashed_bytes


def encrypt_message(message, key):
    cipher = AES.new(key, AES.MODE_CBC)
    ct_bytes = cipher.encrypt(pad(message.encode('utf-8'), AES.block_size))
    iv = cipher.iv
    return (iv, ct_bytes)


def decrypt_message(iv, ct_bytes, key):
    cipher = AES.new(key, AES.MODE_CBC, iv)
    pt = unpad(cipher.decrypt(ct_bytes), AES.block_size).decode('utf-8')
    return pt
