from string import ascii_lowercase, ascii_uppercase


"""
USB Keyboard Traffic
====================

@refs:
https://ctf-wiki.org/misc/traffic/protocols/usb/#usb_1
https://www.usb.org/sites/default/files/documents/hut1_12v2.pdf
"""


class USBKeyboard:

    def __init__(self):
        self.keys = self._key_codes()

    def _key_codes(self) -> tuple[dict, dict]:
        # usb hid key codes
        normal_values = [
            *ascii_lowercase, *'1234567890', '\r\n', '<ESC>', '<DEL>',
            *'\t -=[]\\', '<NON>', *";'", '<GA>', *',./', '<CAP>',
            *[f'<F{i}>' for i in range(1, 13)]]
        shift_values = [
            *ascii_uppercase, *'!@#$%^&*()', '\r\n', '<ESC>', '<DEL>',
            *'\t _+{}|', '<NON>', *':"', '<GA>', *'<>?', '<CAP>',
            *[f'<F{i}>' for i in range(1, 13)]]

        normal_keys, shift_keys = {}, {}
        for i, (n, s) in enumerate(zip(normal_values, shift_values)):
            normal_keys[i+4], shift_keys[i+4] = n, s
        return normal_keys, shift_keys

    def key_bind(self, data: list[bytes]) -> list[str]:
        # bind usb hid key codes
        result = []
        for i in data:
            if i[0] in [0x00, 0x02] and i[1]:
                result.append(self.keys[i[0] == 0x02].get(
                    i[1], f'<{"NS"[i[0] == 0x02]}:{i[1]:02x}>'))
        return result

    def read_file(self, file: str) -> list[bytes]:
        # read file
        return [(lambda x: bytes([x[0], x[2]]))(bytes.fromhex(
            l.strip().replace(':', '').replace(' ', '')))
            for l in open(file, 'rt').readlines() if l.strip()]

    def _parse_capslock(self, source: list[str]) -> list[str]:
        # parse capslock
        result, caps = [], False
        for i in source:
            if i == '<CAP>':
                caps = not caps
            else:
                result.append((i.lower() if i.isupper() else i.upper())
                              if caps and len(i) == 1 else i)
        return result

    def _parse_delete(self, source: list[str]) -> list[str]:
        # parse delete
        result = []
        for i in source:
            if i == '<DEL>':
                result.pop()
            else:
                result.append(i)
        return result

    def parse(self, source: list[str]) -> list[str]:
        # parse
        source = self._parse_capslock(source)
        source = self._parse_delete(source)
        return ''.join(source)


def badusb_payload(file: str) -> str:
    # an example of custom payload parse

    source = open(file, 'rt').read().strip().split(' ')[42:-10]
    data = []
    for i in range(0, len(source), 2):
        data.append(bytes([int(source[i], 16), int(source[i+1], 16)]))

    usb = USBKeyboard()
    bind = usb.key_bind(data)
    return usb.parse(bind)


if __name__ == '__main__':

    file = input("[>] Input the file path: ").strip()

    print("[*] Processing...")

    usb = USBKeyboard()
    data = usb.read_file(file)
    bind = usb.key_bind(data)
    parsed = usb.parse(bind)

    print("[+] Key Bind:", "".join(bind).encode())
    print("[+] Parsed:", parsed)
