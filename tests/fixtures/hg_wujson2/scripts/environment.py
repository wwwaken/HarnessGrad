import json
import os
import platform
import sys
import sysconfig
print(json.dumps({'python': sys.version, 'executable': sys.executable,
    'platform': platform.platform(), 'libc': platform.libc_ver(),
    'sysconfig': {k: sysconfig.get_config_var(k) for k in ('CC','CXX','CFLAGS','LDFLAGS','SOABI','EXT_SUFFIX','CONFIG_ARGS')},
    'build_env': {k: os.environ.get(k) for k in ('SETUPTOOLS_SCM_PRETEND_VERSION','SOURCE_DATE_EPOCH','PYTHONHASHSEED','TZ','LC_ALL','UJSON_BUILD_DC_LIBS','UJSON_BUILD_DC_INCLUDES','UJSON_BUILD_NO_STRIP')},
}, indent=2))
