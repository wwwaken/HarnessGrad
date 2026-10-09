# Trusted AppWorld service/verifier image.  The agent image is built separately from
# Dockerfile.agent and contains only the CLI; this image is never mounted into the agent.
FROM docker.m.daocloud.io/library/python:3.11-slim
RUN python -m pip install --no-cache-dir "appworld==0.1.3.post1" "uvicorn<1" && \
    python -m appworld.cli install --no-repo
COPY data /appworld/data
COPY service.py /usr/local/lib/python3.11/site-packages/appworld_service.py
COPY server.sh /usr/local/bin/appworld-server
RUN chmod +x /usr/local/bin/appworld-server && mkdir -p /recordings/appworld/experiments && \
    chmod -R a+rwX /appworld /recordings
ENV APPWORLD_ROOT=/appworld PYTHONUNBUFFERED=1
WORKDIR /app
CMD ["appworld-server"]
