from struct import pack, unpack
from math import floor, sin


"""
MD5 Extension Attack
====================

@refs
https://github.com/shellfeel/hash-ext-attack
"""


class MD5:

    def __init__(self):
        self.A, self.B, self.C, self.D = \
            (0x67452301, 0xefcdab89, 0x98badcfe, 0x10325476)  # initial values
        self.r: list[int] = \
            [7, 12, 17, 22] * 4 + [5,  9, 14, 20] * 4 + \
            [4, 11, 16, 23] * 4 + [6, 10, 15, 21] * 4  # shift values
        self.k: list[int] = \
            [floor(abs(sin(i + 1)) * pow(2, 32))
             for i in range(64)]  # constants

    def _lrot(self, x: int, n: int) -> int:
        # left rotate
        return (x << n) | (x >> 32 - n)

    def update(self, chunk: bytes) -> None:
        # update the hash for a chunk of data (64 bytes)
        w = list(unpack('<'+'I'*16, chunk))
        a, b, c, d = self.A, self.B, self.C, self.D

        for i in range(64):
            if i < 16:
                f = (b & c) | ((~b) & d)
                flag = i
            elif i < 32:
                f = (b & d) | (c & (~d))
                flag = (5 * i + 1) % 16
            elif i < 48:
                f = (b ^ c ^ d)
                flag = (3 * i + 5) % 16
            else:
                f = c ^ (b | (~d))
                flag = (7 * i) % 16

            tmp = b + \
                self._lrot((a + f + self.k[i] + w[flag])
                           & 0xffffffff, self.r[i])
            a, b, c, d = d, tmp & 0xffffffff, b, c

        self.A = (self.A + a) & 0xffffffff
        self.B = (self.B + b) & 0xffffffff
        self.C = (self.C + c) & 0xffffffff
        self.D = (self.D + d) & 0xffffffff

    def extend(self, msg: bytes) -> None:
        # extend the hash with a new message (padded)
        for i in range(0, len(msg), 64):
            self.update(msg[i:i + 64])

    def padding(self, msg: bytes) -> bytes:
        # pad the message
        length = pack('<Q', len(msg) * 8)

        msg += b'\x80'
        msg += b'\x00' * (64 - len(msg)) if 56 < len(msg) < 64 else b''
        msg += b'\x00' * (56 - len(msg) % 64)
        msg += length

        return msg

    def digest(self) -> bytes:
        # return the hash
        return pack('<IIII', self.A, self.B, self.C, self.D)


def verify_md5() -> None:
    # (DEBUG function) verify the MD5 implementation
    from hashlib import md5 as md5_hashlib

    def md5_manual(msg: bytes) -> bytes:
        md5 = MD5()
        md5.extend(md5.padding(msg))
        return md5.digest()

    test_string = input("Input a string: ").strip().encode()

    print("Manual: ", md5_manual(test_string).hex())
    print("Hashlib:", md5_hashlib(test_string).hexdigest())


def attack(message_len: int, known_hash: str,
           append_str: bytes) -> tuple:
    # MD5 extension attack
    md5 = MD5()

    previous_text = md5.padding(b"*" * message_len)
    current_text = previous_text + append_str

    md5.A, md5.B, md5.C, md5.D = unpack("<IIII", bytes.fromhex(known_hash))
    md5.extend(md5.padding(current_text)[len(previous_text):])

    return current_text[message_len:], md5.digest().hex()


if __name__ == '__main__':

    message_len = int(input("[>] Input known text length: "))
    known_hash = input("[>] Input known hash: ").strip()
    append_text = input("[>] Input append text: ").strip().encode()

    print("[*] Attacking...")

    extend_str, final_hash = attack(message_len, known_hash, append_text)

    from urllib.parse import quote
    from base64 import b64encode

    print("[+] Extend text:", extend_str)
    print("[+] Extend text (URL encoded):", quote(extend_str))
    print("[+] Extend text (Base64):", b64encode(extend_str).decode())
    print("[+] Final hash:", final_hash)
