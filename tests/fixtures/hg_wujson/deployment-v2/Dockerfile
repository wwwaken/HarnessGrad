FROM --platform=linux/amd64 python@sha256:5560e9ab8709f459489e5b8aa696eda8a07ef821e14bb122be62d91234bfa98b
COPY . /opt/hg-wujson/
RUN --network=none set -eu; \
    cd /opt/hg-wujson; \
    sha256sum -c INPUTS.sha256; \
    python -I -B -m venv /opt/ujson-runtime; \
    PIP_CONFIG_FILE=/dev/null /opt/ujson-runtime/bin/python -I -B -m pip \
      --isolated --disable-pip-version-check --no-cache-dir install \
      --no-index --find-links=/opt/hg-wujson --require-hashes --only-binary=:all: \
      --no-deps --no-compile --report=/opt/hg-wujson/build-install-report.json \
      -r /opt/hg-wujson/requirements.txt; \
    mkdir -p /usr/local/share/licenses/hg-wujson; \
    cp /opt/hg-wujson/notices/ujson-LICENSE.txt /usr/local/share/licenses/hg-wujson/; \
    cp /opt/hg-wujson/notices/double-conversion-LICENSE /usr/local/share/licenses/hg-wujson/
ENV PATH="/opt/ujson-runtime/bin:${PATH}"
CMD ["python", "-I", "-B", "-c", "import ujson; print(ujson.__version__, ujson.__file__)"]
