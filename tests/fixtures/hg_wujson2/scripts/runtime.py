"""Bind a fresh native import to every installed non-RECORD wheel member."""
import ctypes
import hashlib
import importlib.machinery
import importlib.util
import json
from pathlib import Path
import platform
import sys
import zipfile

import ujson

path = Path(sys.argv[1])
base = Path(ujson.__file__).parent
installed = []
with zipfile.ZipFile(path) as z:
    for info in z.infolist():
        if info.is_dir() or info.filename.endswith('/RECORD'):
            continue
        data = (base / info.filename).read_bytes()
        assert data == z.read(info), info.filename
        installed.append({'member': info.filename, 'sha256': hashlib.sha256(data).hexdigest(), 'size': len(data)})
assert ujson.__version__ == '5.10.0'
assert isinstance(importlib.util.find_spec('ujson').loader, importlib.machinery.ExtensionFileLoader)
value = {'synthetic': ['fictional azure', 0.125, 1e100, True, None, '\u96ea']}
assert ujson.loads(ujson.dumps(value)) == value

class DlInfo(ctypes.Structure):
    _fields_ = [('dli_fname', ctypes.c_char_p), ('dli_fbase', ctypes.c_void_p),
                ('dli_sname', ctypes.c_char_p), ('dli_saddr', ctypes.c_void_p)]

lib = ctypes.CDLL(ujson.__file__)
api = ctypes.CDLL(None)
api.dladdr.argtypes = [ctypes.c_void_p, ctypes.POINTER(DlInfo)]
api.dladdr.restype = ctypes.c_int
symbol = '_ZN17double_conversion6Bignum11PlusCompareERKS0_S2_S2_'
address = ctypes.cast(getattr(lib, symbol), ctypes.c_void_p)
info = DlInfo()
assert api.dladdr(address, ctypes.byref(info)) != 0
provider = info.dli_fname.decode()
assert Path(provider).resolve() == Path(ujson.__file__).resolve()
notices = {}
for name in ('ujson-LICENSE.txt', 'double-conversion-LICENSE'):
    notice = Path(sys.prefix) / 'share/licenses/hg-wujson2' / name
    data = notice.read_bytes()
    assert data == (Path('/opt/hg-wujson/notices') / name).read_bytes()
    notices[str(notice)] = hashlib.sha256(data).hexdigest()
print(json.dumps({'python': sys.version, 'platform': platform.platform(), 'glibc': platform.libc_ver(),
    'ujson': ujson.__version__, 'module': ujson.__file__,
    'wheel': str(path), 'wheel_sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
    'installed_members': installed, 'notices': notices,
    'double_conversion_symbol': symbol, 'double_conversion_symbol_provider': provider,
    'synthetic_roundtrip': value, 'passed': True}, indent=2))
