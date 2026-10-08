# Build context is assembled at import time from this Dockerfile, server.sh, and the
# decrypted external data tree. The platform never builds or pulls this image during a run.
FROM docker.m.daocloud.io/library/python:3.11-slim
RUN python -m pip install --no-cache-dir "appworld==0.1.3.post1" && \
    python -m appworld.cli install --no-repo
COPY data /appworld/data
COPY server.sh /usr/local/bin/appworld-server
RUN chmod +x /usr/local/bin/appworld-server && mkdir -p /recordings/appworld/experiments && \
    chmod -R a+rwX /appworld /recordings
ENV APPWORLD_ROOT=/appworld PYTHONUNBUFFERED=1
WORKDIR /app
CMD ["appworld-server"]
