
CIPHER_SHIFT = 7

PRINTABLE_START = 32
PRINTABLE_RANGE = 95


def encrypt_password(password: str, shift: int = CIPHER_SHIFT) -> str:
    encrypted = []
    for char in password:
        code = ord(char)
        if PRINTABLE_START <= code <= 126:
            shifted = (code - PRINTABLE_START + shift) % PRINTABLE_RANGE + PRINTABLE_START
            encrypted.append(chr(shifted))
        else:
            encrypted.append(char)
    return "".join(encrypted)


def decrypt_password(encrypted: str, shift: int = CIPHER_SHIFT) -> str:
    decrypted = []
    for char in encrypted:
        code = ord(char)
        if PRINTABLE_START <= code <= 126:
            shifted = (code - PRINTABLE_START - shift) % PRINTABLE_RANGE + PRINTABLE_START
            decrypted.append(chr(shifted))
        else:
            decrypted.append(char)
    return "".join(decrypted)