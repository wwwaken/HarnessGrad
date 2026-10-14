# tau-bench as one shared image: the environment for every retail and airline task.
#
# What the agent can see
# ---------------------
#   /app                         workdir; SETUP lands db.json here and `tau call`
#                                mutates it. It is the container's writable state,
#                                which is what the verifier reads from the snapshot.
#   /opt/tau/lib/tau_bench       the upstream tool implementations for both domains,
#                                with the task definitions removed. `tau` imports
#                                them; they are not secrets.
#   /opt/tau/policy              `<domain>.txt` = wiki.md + rules.py; `tau policy`.
#   /opt/tau/pristine            the clean database per domain, for reference. The
#                                task's own copy is /app/db.json, not this one.
#   /usr/local/bin/tau           the shim; the implementation is tau_cli.py beside it.
#
# What the agent must **not** see
# -------------------------------
# Nothing under `gt/` or `verify/` is copied in, and the build context excludes both.
# In particular no `tasks*.py` from the checkout travels: those files are the answer
# key, and the whole point of staging `lib/` from the tool directories is that they
# never enter this image. The verification procedure greps for them.
FROM docker.m.daocloud.io/library/python:3.11-slim

LABEL org.opencontainers.image.title="harnessgrad/tau-bench" \
      org.opencontainers.image.description="tau-bench retail+airline tools, data and policy behind the tau CLI" \
      harnessgrad.dataset="tau_bench" \
      harnessgrad.provenance="data/datasets/tau_bench/PROVENANCE.json (upstream sierra-research/tau-bench @ 59a200c)"

WORKDIR /app

# Set before anything imports the tools: a `__pycache__` written here would be a second,
# unmanaged copy of each tool module inside the image.
ENV PYTHONDONTWRITEBYTECODE=1

COPY lib /opt/tau/lib
COPY policy /opt/tau/policy
COPY db /opt/tau/pristine
COPY image/tau_cli.py /usr/local/bin/tau_cli.py

# The shim is what the goal tells the agent to call; tau_cli.py stays runnable on its
# own so a missing shim is not a dead end.
RUN printf '#!/bin/sh\nexec python3 /usr/local/bin/tau_cli.py "$@"\n' \
        > /usr/local/bin/tau \
 && chmod 0755 /usr/local/bin/tau /usr/local/bin/tau_cli.py \
 && python3 -B -c "import sys; sys.path.insert(0, '/opt/tau/lib'); \
import tau_bench.envs.retail.tools, tau_bench.envs.airline.tools; \
print('tau tools:', len(tau_bench.envs.retail.tools.ALL_TOOLS), 'retail,', \
      len(tau_bench.envs.airline.tools.ALL_TOOLS), 'airline')"
