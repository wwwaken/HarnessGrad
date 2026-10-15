# Local Terminal-Bench bootstrap lines

Verbatim external file:line commands; continuation lines retained. Image-build and other-source matches are separate from verifier bootstrap. All 89 test.sh and Dockerfile preimages are copied beside this index.

## adaptive-rejection-sampler — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/adaptive-rejection-sampler/tests/test.sh:4
```sh
apt-get update
```

## adaptive-rejection-sampler — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/adaptive-rejection-sampler/tests/test.sh:5
```sh
apt-get install -y curl
```

## adaptive-rejection-sampler — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/adaptive-rejection-sampler/tests/test.sh:8
```sh
curl -LsSf https://astral.sh/uv/0.9.5/install.sh | sh
```

## adaptive-rejection-sampler — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/adaptive-rejection-sampler/tests/test.sh:18
```sh
uvx \
  -p 3.13 \
  -w pytest==8.4.1 \
  -w numpy==2.3.3 \
  -w scipy==1.16.2 \
  -w pytest-json-ctrf==0.3.5 \
  pytest --ctrf /logs/verifier/ctrf.json /tests/test_outputs.py -rA
```

## bn-fit-modify — image-build
/mnt/20t/xubuqiang/datasets/terminal-bench/bn-fit-modify/environment/Dockerfile:5
```sh
RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        r-base \
        python3 \
        python3-pip \
        build-essential \
        curl \
        sudo \
        gfortran \
        libblas-dev \
        liblapack-dev && \
    rm -rf /var/lib/apt/lists/*
```

## bn-fit-modify — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/bn-fit-modify/tests/test.sh:4
```sh
apt-get update
```

## bn-fit-modify — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/bn-fit-modify/tests/test.sh:5
```sh
apt-get install -y curl
```

## bn-fit-modify — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/bn-fit-modify/tests/test.sh:8
```sh
curl -LsSf https://astral.sh/uv/0.9.5/install.sh | sh
```

## bn-fit-modify — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/bn-fit-modify/tests/test.sh:18
```sh
uvx \
  -p 3.13 \
  -w pytest==8.4.1 \
  -w pandas==2.3.2 \
  -w scipy==1.16.1 \
  -w pytest-json-ctrf==0.3.5 \
  pytest --ctrf /logs/verifier/ctrf.json /tests/test_outputs.py -rA
```

## break-filter-js-from-html — image-build
/mnt/20t/xubuqiang/datasets/terminal-bench/break-filter-js-from-html/environment/Dockerfile:5
```sh
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    chromium \
    chromium-driver \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*
```

## break-filter-js-from-html — image-build
/mnt/20t/xubuqiang/datasets/terminal-bench/break-filter-js-from-html/environment/Dockerfile:15
```sh
RUN pip install --no-cache-dir selenium==4.35.0 beautifulsoup4==4.13.4
```

## break-filter-js-from-html — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/break-filter-js-from-html/tests/test.sh:4
```sh
apt-get update
```

## break-filter-js-from-html — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/break-filter-js-from-html/tests/test.sh:5
```sh
apt-get install -y curl
```

## break-filter-js-from-html — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/break-filter-js-from-html/tests/test.sh:8
```sh
curl -LsSf https://astral.sh/uv/0.9.5/install.sh | sh
```

## break-filter-js-from-html — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/break-filter-js-from-html/tests/test.sh:18
```sh
uvx \
  -p 3.13 \
  -w pytest==8.4.1 \
  -w selenium==4.35.0 \
  -w beautifulsoup4==4.13.5 \
  -w pytest-json-ctrf==0.3.5 \
  pytest --ctrf /logs/verifier/ctrf.json /tests/test_outputs.py -rA
```

## build-cython-ext — image-build
/mnt/20t/xubuqiang/datasets/terminal-bench/build-cython-ext/environment/Dockerfile:7
```sh
RUN apt-get update && \
    apt-get install -y \
        git \
        build-essential \
        libgl1-mesa-glx && \
    rm -rf /var/lib/apt/lists/*
```

## build-cython-ext — image-build
/mnt/20t/xubuqiang/datasets/terminal-bench/build-cython-ext/environment/Dockerfile:14
```sh
RUN pip install numpy==2.3.0
```

## build-cython-ext — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/build-cython-ext/tests/test.sh:9
```sh
pip install pytest==8.4.1 pytest-json-ctrf==0.3.5
```

## build-pmars — image-build
/mnt/20t/xubuqiang/datasets/terminal-bench/build-pmars/environment/Dockerfile:5
```sh
RUN apt-get update && apt-get install -y tmux asciinema
```

## build-pmars — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/build-pmars/tests/test.sh:4
```sh
apt-get update
```

## build-pmars — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/build-pmars/tests/test.sh:5
```sh
apt-get install -y curl
```

## build-pmars — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/build-pmars/tests/test.sh:8
```sh
curl -LsSf https://astral.sh/uv/0.9.5/install.sh | sh
```

## build-pmars — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/build-pmars/tests/test.sh:18
```sh
uvx \
  -p 3.13 \
  -w pytest==8.4.1 \
  -w pytest-json-ctrf==0.3.5 \
  pytest --ctrf /logs/verifier/ctrf.json /tests/test_outputs.py -rA
```

## build-pov-ray — image-build
/mnt/20t/xubuqiang/datasets/terminal-bench/build-pov-ray/environment/Dockerfile:5
```sh
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    git \
    imagemagick \
    && rm -rf /var/lib/apt/lists/*
```

## build-pov-ray — image-build
/mnt/20t/xubuqiang/datasets/terminal-bench/build-pov-ray/environment/Dockerfile:12
```sh
RUN apt-get update && apt-get purge -y povray* || true
```

## build-pov-ray — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/build-pov-ray/tests/test.sh:3
```sh
apt-get update
```

## build-pov-ray — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/build-pov-ray/tests/test.sh:4
```sh
apt-get install -y curl imagemagick
```

## build-pov-ray — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/build-pov-ray/tests/test.sh:7
```sh
curl -LsSf https://astral.sh/uv/0.9.5/install.sh | sh
```

## build-pov-ray — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/build-pov-ray/tests/test.sh:16
```sh
uvx \
  -p 3.13 \
  -w pytest==8.4.1 \
  -w pillow==11.1.0 \
  -w numpy==2.3.1 \
  -w scikit-image==0.25.0 \
  -w pytest-json-ctrf==0.3.5 \
  pytest --ctrf /logs/verifier/ctrf.json /tests/test_outputs.py -rA
```

## caffe-cifar-10 — image-build
/mnt/20t/xubuqiang/datasets/terminal-bench/caffe-cifar-10/environment/Dockerfile:5
```sh
RUN apt-get update && apt-get install -y \
    git \
    curl \
    cmake \
    wget
```

## caffe-cifar-10 — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/caffe-cifar-10/tests/test.sh:4
```sh
apt-get update
```

## caffe-cifar-10 — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/caffe-cifar-10/tests/test.sh:5
```sh
apt-get install -y curl
```

## caffe-cifar-10 — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/caffe-cifar-10/tests/test.sh:8
```sh
curl -LsSf https://astral.sh/uv/0.9.5/install.sh | sh
```

## caffe-cifar-10 — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/caffe-cifar-10/tests/test.sh:18
```sh
uvx \
  -p 3.13 \
  -w pytest==8.4.1 \
  -w pytest-json-ctrf==0.3.5 \
  pytest --ctrf /logs/verifier/ctrf.json /tests/test_outputs.py -rA
```

## cancel-async-tasks — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/cancel-async-tasks/tests/test.sh:4
```sh
apt-get update
```

## cancel-async-tasks — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/cancel-async-tasks/tests/test.sh:5
```sh
apt-get install -y curl
```

## cancel-async-tasks — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/cancel-async-tasks/tests/test.sh:8
```sh
curl -LsSf https://astral.sh/uv/0.9.5/install.sh | sh
```

## cancel-async-tasks — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/cancel-async-tasks/tests/test.sh:19
```sh
uvx \
  -p 3.13 \
  -w pytest==8.4.1 \
  -w pytest-json-ctrf==0.3.5 \
  pytest --ctrf /logs/verifier/ctrf.json /tests/test_outputs.py -rA
```

## chess-best-move — image-build
/mnt/20t/xubuqiang/datasets/terminal-bench/chess-best-move/environment/Dockerfile:5
```sh
RUN apt update -y
```

## chess-best-move — image-build
/mnt/20t/xubuqiang/datasets/terminal-bench/chess-best-move/environment/Dockerfile:6
```sh
RUN apt clean && apt update -y
```

## chess-best-move — image-build
/mnt/20t/xubuqiang/datasets/terminal-bench/chess-best-move/environment/Dockerfile:7
```sh
RUN apt install -y curl
```

## chess-best-move — image-build
/mnt/20t/xubuqiang/datasets/terminal-bench/chess-best-move/environment/Dockerfile:8
```sh
RUN apt install -y python3-pip
```

## chess-best-move — image-build
/mnt/20t/xubuqiang/datasets/terminal-bench/chess-best-move/environment/Dockerfile:9
```sh
RUN pip3 install pillow==11.2.1 --break-system-packages
```

## chess-best-move — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/chess-best-move/tests/test.sh:4
```sh
apt-get update
```

## chess-best-move — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/chess-best-move/tests/test.sh:5
```sh
apt-get install -y curl
```

## chess-best-move — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/chess-best-move/tests/test.sh:8
```sh
curl -LsSf https://astral.sh/uv/0.9.5/install.sh | sh
```

## chess-best-move — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/chess-best-move/tests/test.sh:18
```sh
uvx \
  -p 3.13 \
  -w pytest==8.4.1 \
  -w pytest-json-ctrf==0.3.5 \
  pytest --ctrf /logs/verifier/ctrf.json /tests/test_outputs.py -rA
```

## circuit-fibsqrt — image-build
/mnt/20t/xubuqiang/datasets/terminal-bench/circuit-fibsqrt/environment/Dockerfile:5
```sh
RUN apt-get update
```

## circuit-fibsqrt — image-build
/mnt/20t/xubuqiang/datasets/terminal-bench/circuit-fibsqrt/environment/Dockerfile:6
```sh
RUN apt-get install -y gcc
```

## circuit-fibsqrt — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/circuit-fibsqrt/tests/test.sh:4
```sh
apt-get update
```

## circuit-fibsqrt — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/circuit-fibsqrt/tests/test.sh:5
```sh
apt-get install -y curl
```

## circuit-fibsqrt — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/circuit-fibsqrt/tests/test.sh:8
```sh
curl -LsSf https://astral.sh/uv/0.9.5/install.sh | sh
```

## circuit-fibsqrt — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/circuit-fibsqrt/tests/test.sh:18
```sh
uvx \
  -p 3.13 \
  -w pytest==8.4.1 \
  -w pytest-json-ctrf==0.3.5 \
  pytest --ctrf /logs/verifier/ctrf.json /tests/test_outputs.py -rA
```

## cobol-modernization — image-build
/mnt/20t/xubuqiang/datasets/terminal-bench/cobol-modernization/environment/Dockerfile:11
```sh
RUN apt-get update && apt-get install -y nano
```

## cobol-modernization — image-build
/mnt/20t/xubuqiang/datasets/terminal-bench/cobol-modernization/environment/Dockerfile:13
```sh
RUN apt-get install -y gnucobol3
```

## cobol-modernization — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/cobol-modernization/tests/test.sh:4
```sh
apt-get update
```

## cobol-modernization — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/cobol-modernization/tests/test.sh:5
```sh
apt-get install -y curl
```

## cobol-modernization — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/cobol-modernization/tests/test.sh:8
```sh
curl -LsSf https://astral.sh/uv/0.9.5/install.sh | sh
```

## cobol-modernization — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/cobol-modernization/tests/test.sh:18
```sh
uvx \
  -p 3.13 \
  -w pytest==8.4.1 \
  -w pytest-json-ctrf==0.3.5 \
  pytest --ctrf /logs/verifier/ctrf.json /tests/test_outputs.py -rA
```

## code-from-image — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/code-from-image/tests/test.sh:4
```sh
apt-get update
```

## code-from-image — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/code-from-image/tests/test.sh:5
```sh
apt-get install -y curl
```

## code-from-image — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/code-from-image/tests/test.sh:8
```sh
curl -LsSf https://astral.sh/uv/0.9.5/install.sh | sh
```

## code-from-image — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/code-from-image/tests/test.sh:18
```sh
uvx \
  -p 3.13 \
  -w pytest==8.4.1 \
  -w pytest-json-ctrf==0.3.5 \
  pytest --ctrf /logs/verifier/ctrf.json /tests/test_outputs.py -rA
```

## compile-compcert — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/compile-compcert/tests/test.sh:4
```sh
apt-get update
```

## compile-compcert — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/compile-compcert/tests/test.sh:5
```sh
apt-get install -y curl binutils
```

## compile-compcert — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/compile-compcert/tests/test.sh:8
```sh
curl -LsSf https://astral.sh/uv/0.9.5/install.sh | sh
```

## compile-compcert — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/compile-compcert/tests/test.sh:18
```sh
uvx \
  -p 3.13 \
  -w pytest==8.4.1 \
  -w pytest-json-ctrf==0.3.5 \
  pytest --ctrf /logs/verifier/ctrf.json /tests/test_outputs.py -rA
```

## configure-git-webserver — image-build
/mnt/20t/xubuqiang/datasets/terminal-bench/configure-git-webserver/environment/Dockerfile:5
```sh
RUN apt update -y && apt install -y curl
```

## configure-git-webserver — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/configure-git-webserver/tests/test.sh:4
```sh
curl -LsSf https://astral.sh/uv/0.9.5/install.sh | sh
```

## configure-git-webserver — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/configure-git-webserver/tests/test.sh:14
```sh
uvx \
  -p 3.13 \
  -w pytest==8.4.1 \
  -w pytest-json-ctrf==0.3.5 \
  pytest --ctrf /logs/verifier/ctrf.json /tests/test_outputs.py -rA
```

## configure-git-webserver — other-source
/mnt/20t/xubuqiang/datasets/terminal-bench/configure-git-webserver/tests/verify.sh:5
```sh
apt-get update
```

## configure-git-webserver — other-source
/mnt/20t/xubuqiang/datasets/terminal-bench/configure-git-webserver/tests/verify.sh:6
```sh
DEBIAN_FRONTEND=noninteractive apt-get install -y expect
```

## constraints-scheduling — image-build
/mnt/20t/xubuqiang/datasets/terminal-bench/constraints-scheduling/environment/Dockerfile:7
```sh
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
      python3 \
      python3-pip \
 && rm -rf /var/lib/apt/lists/*
```

## constraints-scheduling — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/constraints-scheduling/tests/test.sh:4
```sh
apt-get update
```

## constraints-scheduling — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/constraints-scheduling/tests/test.sh:5
```sh
apt-get install -y curl
```

## constraints-scheduling — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/constraints-scheduling/tests/test.sh:8
```sh
curl -LsSf https://astral.sh/uv/0.9.5/install.sh | sh
```

## constraints-scheduling — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/constraints-scheduling/tests/test.sh:18
```sh
uvx \
  -p 3.13 \
  -w pytest==8.4.1 \
  -w pytest-json-ctrf==0.3.5 \
  pytest --ctrf /logs/verifier/ctrf.json /tests/test_outputs.py -rA
```

## count-dataset-tokens — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/count-dataset-tokens/tests/test.sh:4
```sh
apt-get update
```

## count-dataset-tokens — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/count-dataset-tokens/tests/test.sh:5
```sh
apt-get install -y curl
```

## count-dataset-tokens — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/count-dataset-tokens/tests/test.sh:8
```sh
curl -LsSf https://astral.sh/uv/0.9.5/install.sh | sh
```

## count-dataset-tokens — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/count-dataset-tokens/tests/test.sh:18
```sh
uvx \
  -p 3.13 \
  -w pytest==8.4.1 \
  -w pytest-json-ctrf==0.3.5 \
  pytest --ctrf /logs/verifier/ctrf.json /tests/test_outputs.py -rA
```

## crack-7z-hash — image-build
/mnt/20t/xubuqiang/datasets/terminal-bench/crack-7z-hash/environment/Dockerfile:5
```sh
RUN apt-get update
```

## crack-7z-hash — image-build
/mnt/20t/xubuqiang/datasets/terminal-bench/crack-7z-hash/environment/Dockerfile:6
```sh
RUN apt-get install git build-essential -y
```

## crack-7z-hash — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/crack-7z-hash/tests/test.sh:4
```sh
apt-get update
```

## crack-7z-hash — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/crack-7z-hash/tests/test.sh:5
```sh
apt-get install -y curl
```

## crack-7z-hash — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/crack-7z-hash/tests/test.sh:8
```sh
curl -LsSf https://astral.sh/uv/0.9.5/install.sh | sh
```

## crack-7z-hash — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/crack-7z-hash/tests/test.sh:18
```sh
uvx \
  -p 3.13 \
  -w pytest==8.4.1 \
  -w pytest-json-ctrf==0.3.5 \
  pytest --ctrf /logs/verifier/ctrf.json /tests/test_outputs.py -rA
```

## custom-memory-heap-crash — image-build
/mnt/20t/xubuqiang/datasets/terminal-bench/custom-memory-heap-crash/environment/Dockerfile:6
```sh
RUN apt-get update && \
    apt-get install -y \
    asciinema \
    build-essential \
    g++ \
    gcc \
    make \
    autoconf \
    automake \
    libtool \
    texinfo \
    tmux \
    python3 \
    python3-pip \
    flex \
    bison \
    git \
    wget \
    file \
    libgmp-dev \
    libmpfr-dev \
    libmpc-dev \
    valgrind \
    && rm -rf /var/lib/apt/lists/*
```

## custom-memory-heap-crash — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/custom-memory-heap-crash/tests/test.sh:6
```sh
apt-get update
```

## custom-memory-heap-crash — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/custom-memory-heap-crash/tests/test.sh:7
```sh
apt-get install -y curl
```

## custom-memory-heap-crash — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/custom-memory-heap-crash/tests/test.sh:10
```sh
curl -LsSf https://astral.sh/uv/0.9.5/install.sh | sh
```

## custom-memory-heap-crash — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/custom-memory-heap-crash/tests/test.sh:20
```sh
uvx \
  -p 3.13 \
  -w pytest==8.4.1 \
  -w pytest-json-ctrf==0.3.5 \
  pytest --ctrf /logs/verifier/ctrf.json /tests/test_outputs.py -rA
```

## db-wal-recovery — image-build
/mnt/20t/xubuqiang/datasets/terminal-bench/db-wal-recovery/environment/Dockerfile:5
```sh
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    sqlite3 \
    xxd \
    && rm -rf /var/lib/apt/lists/*
```

## db-wal-recovery — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/db-wal-recovery/tests/test.sh:4
```sh
apt-get update
```

## db-wal-recovery — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/db-wal-recovery/tests/test.sh:5
```sh
apt-get install -y curl
```

## db-wal-recovery — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/db-wal-recovery/tests/test.sh:8
```sh
curl -LsSf https://astral.sh/uv/0.9.5/install.sh | sh
```

## db-wal-recovery — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/db-wal-recovery/tests/test.sh:18
```sh
uvx \
  -p 3.13 \
  -w pytest==8.4.1 \
  -w pytest-json-ctrf==0.3.5 \
  pytest --ctrf /logs/verifier/ctrf.json /tests/test_outputs.py -rA
```

## distribution-search — image-build
/mnt/20t/xubuqiang/datasets/terminal-bench/distribution-search/environment/Dockerfile:6
```sh
RUN apt-get update
```

## distribution-search — image-build
/mnt/20t/xubuqiang/datasets/terminal-bench/distribution-search/environment/Dockerfile:8
```sh
RUN pip install numpy==2.1.2 scipy==1.15.3
```

## distribution-search — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/distribution-search/tests/test.sh:4
```sh
apt-get update
```

## distribution-search — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/distribution-search/tests/test.sh:5
```sh
apt-get install -y curl
```

## distribution-search — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/distribution-search/tests/test.sh:8
```sh
curl -LsSf https://astral.sh/uv/0.9.5/install.sh | sh
```

## distribution-search — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/distribution-search/tests/test.sh:18
```sh
uvx \
  -p 3.13 \
  -w pytest==8.4.1 \
  -w numpy==2.3.0 \
  -w pytest-json-ctrf==0.3.5 \
  pytest --ctrf /logs/verifier/ctrf.json /tests/test_outputs.py -v -rA
```

## dna-assembly — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/dna-assembly/tests/test.sh:4
```sh
apt-get update
```

## dna-assembly — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/dna-assembly/tests/test.sh:5
```sh
apt-get install -y curl primer3
```

## dna-assembly — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/dna-assembly/tests/test.sh:8
```sh
curl -LsSf https://astral.sh/uv/0.9.5/install.sh | sh
```

## dna-assembly — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/dna-assembly/tests/test.sh:18
```sh
uvx \
  -p 3.13 \
  -w pytest==8.4.1 \
  -w pytest-json-ctrf==0.3.5 \
  pytest --ctrf /logs/verifier/ctrf.json /tests/test_outputs.py -rA
```

## dna-insert — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/dna-insert/tests/test.sh:3
```sh
apt-get update
```

## dna-insert — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/dna-insert/tests/test.sh:4
```sh
apt-get install -y curl primer3
```

## dna-insert — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/dna-insert/tests/test.sh:7
```sh
curl -LsSf https://astral.sh/uv/0.9.5/install.sh | sh
```

## dna-insert — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/dna-insert/tests/test.sh:17
```sh
uvx \
  -p 3.13 \
  -w pytest==8.4.1 \
  -w pytest-json-ctrf==0.3.5 \
  pytest --ctrf /logs/verifier/ctrf.json /tests/test_outputs.py -rA
```

## extract-elf — image-build
/mnt/20t/xubuqiang/datasets/terminal-bench/extract-elf/environment/Dockerfile:5
```sh
RUN apt-get update && apt-get install -y nodejs npm gcc
```

## extract-elf — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/extract-elf/tests/test.sh:4
```sh
apt-get update
```

## extract-elf — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/extract-elf/tests/test.sh:5
```sh
apt-get install -y curl gcc
```

## extract-elf — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/extract-elf/tests/test.sh:8
```sh
curl -LsSf https://astral.sh/uv/0.9.5/install.sh | sh
```

## extract-elf — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/extract-elf/tests/test.sh:18
```sh
uvx \
  -p 3.13 \
  -w pytest==8.4.1 \
  -w pytest-json-ctrf==0.3.5 \
  pytest --ctrf /logs/verifier/ctrf.json /tests/test_outputs.py -rA
```

## extract-moves-from-video — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/extract-moves-from-video/tests/test.sh:4
```sh
apt-get update
```

## extract-moves-from-video — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/extract-moves-from-video/tests/test.sh:5
```sh
apt-get install -y curl
```

## extract-moves-from-video — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/extract-moves-from-video/tests/test.sh:8
```sh
curl -LsSf https://astral.sh/uv/0.9.5/install.sh | sh
```

## extract-moves-from-video — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/extract-moves-from-video/tests/test.sh:18
```sh
uvx \
  -p 3.13 \
  -w pytest==8.4.1 \
  -w pytest-json-ctrf==0.3.5 \
  pytest --ctrf /logs/verifier/ctrf.json /tests/test_outputs.py -rA
```

## feal-differential-cryptanalysis — image-build
/mnt/20t/xubuqiang/datasets/terminal-bench/feal-differential-cryptanalysis/environment/Dockerfile:6
```sh
RUN pip install setuptools==80.9.0
```

## feal-differential-cryptanalysis — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/feal-differential-cryptanalysis/tests/test.sh:4
```sh
apt-get update
```

## feal-differential-cryptanalysis — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/feal-differential-cryptanalysis/tests/test.sh:5
```sh
apt-get install -y curl gcc
```

## feal-differential-cryptanalysis — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/feal-differential-cryptanalysis/tests/test.sh:8
```sh
curl -LsSf https://astral.sh/uv/0.9.5/install.sh | sh
```

## feal-differential-cryptanalysis — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/feal-differential-cryptanalysis/tests/test.sh:17
```sh
uvx \
  -p 3.13 \
  -w pytest==8.4.1 \
  -w setuptools==80.9.0 \
  -w pytest-json-ctrf==0.3.5 \
  pytest --ctrf /logs/verifier/ctrf.json /tests/test_outputs.py -v -rA
```

## feal-linear-cryptanalysis — image-build
/mnt/20t/xubuqiang/datasets/terminal-bench/feal-linear-cryptanalysis/environment/Dockerfile:5
```sh
RUN apt update -y && apt install -y gcc
```

## feal-linear-cryptanalysis — image-build
/mnt/20t/xubuqiang/datasets/terminal-bench/feal-linear-cryptanalysis/environment/Dockerfile:6
```sh
RUN pip install setuptools==80.9.0
```

## feal-linear-cryptanalysis — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/feal-linear-cryptanalysis/tests/test.sh:4
```sh
apt-get update
```

## feal-linear-cryptanalysis — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/feal-linear-cryptanalysis/tests/test.sh:5
```sh
apt-get install -y curl
```

## feal-linear-cryptanalysis — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/feal-linear-cryptanalysis/tests/test.sh:8
```sh
curl -LsSf https://astral.sh/uv/0.9.5/install.sh | sh
```

## feal-linear-cryptanalysis — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/feal-linear-cryptanalysis/tests/test.sh:18
```sh
uvx \
  -p 3.13 \
  -w pytest==8.4.1 \
  -w pytest-json-ctrf==0.3.5 \
  pytest --ctrf /logs/verifier/ctrf.json /tests/test_outputs.py -v -rA
```

## filter-js-from-html — image-build
/mnt/20t/xubuqiang/datasets/terminal-bench/filter-js-from-html/environment/Dockerfile:5
```sh
RUN apt-get update && apt-get install -y \
    chromium \
    chromium-driver \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*
```

## filter-js-from-html — image-build
/mnt/20t/xubuqiang/datasets/terminal-bench/filter-js-from-html/environment/Dockerfile:12
```sh
RUN pip install --no-cache-dir selenium==4.35.0 beautifulsoup4==4.13.4
```

## filter-js-from-html — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/filter-js-from-html/tests/test.sh:4
```sh
apt-get update
```

## filter-js-from-html — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/filter-js-from-html/tests/test.sh:5
```sh
apt-get install -y curl
```

## filter-js-from-html — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/filter-js-from-html/tests/test.sh:8
```sh
curl -LsSf https://astral.sh/uv/0.9.5/install.sh | sh
```

## filter-js-from-html — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/filter-js-from-html/tests/test.sh:18
```sh
uvx \
  -p 3.13 \
  -w pytest==8.4.1 \
  -w selenium==4.38.0 \
  -w bs4==0.0.2 \
  -w pytest-json-ctrf==0.3.5 \
  pytest --ctrf /logs/verifier/ctrf.json /tests/test_outputs.py -rA
```

## financial-document-processor — image-build
/mnt/20t/xubuqiang/datasets/terminal-bench/financial-document-processor/environment/Dockerfile:4
```sh
COPY --from=ghcr.io/astral-sh/uv:0.8.14 /uv /uvx /bin/
```

## financial-document-processor — image-build
/mnt/20t/xubuqiang/datasets/terminal-bench/financial-document-processor/environment/Dockerfile:14
```sh
RUN uv run /root/randomize_filenames.py
```

## financial-document-processor — image-build
/mnt/20t/xubuqiang/datasets/terminal-bench/financial-document-processor/environment/Dockerfile:18
```sh
COPY --from=ghcr.io/astral-sh/uv:0.8.14 /uv /uvx /bin/
```

## financial-document-processor — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/financial-document-processor/tests/test.sh:4
```sh
apt-get update
```

## financial-document-processor — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/financial-document-processor/tests/test.sh:5
```sh
apt-get install -y curl
```

## financial-document-processor — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/financial-document-processor/tests/test.sh:8
```sh
curl -LsSf https://astral.sh/uv/0.9.5/install.sh | sh
```

## financial-document-processor — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/financial-document-processor/tests/test.sh:18
```sh
uvx \
  -p 3.13 \
  -w pytest==8.4.1 \
  -w pandas==2.3.2 \
  -w pytest-json-ctrf==0.3.5 \
  pytest --ctrf /logs/verifier/ctrf.json /tests/test_outputs.py -rA
```

## fix-code-vulnerability — image-build
/mnt/20t/xubuqiang/datasets/terminal-bench/fix-code-vulnerability/environment/Dockerfile:5
```sh
RUN apt-get update && apt-get install -y git nano sed tmux asciinema
```

## fix-code-vulnerability — image-build
/mnt/20t/xubuqiang/datasets/terminal-bench/fix-code-vulnerability/environment/Dockerfile:17
```sh
RUN pip install --upgrade pip==24.2 && pip install flit==3.12.0
```

## fix-code-vulnerability — image-build
/mnt/20t/xubuqiang/datasets/terminal-bench/fix-code-vulnerability/environment/Dockerfile:19
```sh
RUN pip install .
```

## fix-code-vulnerability — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/fix-code-vulnerability/tests/test.sh:9
```sh
pip install pytest==8.4.1 pytest-json-ctrf==0.3.5
```

## fix-git — image-build
/mnt/20t/xubuqiang/datasets/terminal-bench/fix-git/environment/Dockerfile:6
```sh
RUN apt-get update && apt-get install -y git
```

## fix-git — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/fix-git/tests/test.sh:4
```sh
apt-get update
```

## fix-git — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/fix-git/tests/test.sh:5
```sh
apt-get install -y curl
```

## fix-git — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/fix-git/tests/test.sh:8
```sh
curl -LsSf https://astral.sh/uv/0.9.5/install.sh | sh
```

## fix-git — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/fix-git/tests/test.sh:18
```sh
uvx \
  -p 3.13 \
  -w pytest==8.4.1 \
  -w pytest-json-ctrf==0.3.5 \
  pytest --ctrf /logs/verifier/ctrf.json /tests/test_outputs.py -rA
```

## fix-ocaml-gc — image-build
/mnt/20t/xubuqiang/datasets/terminal-bench/fix-ocaml-gc/environment/Dockerfile:6
```sh
RUN apt update && apt install -y build-essential git gdb
```

## fix-ocaml-gc — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/fix-ocaml-gc/tests/test.sh:4
```sh
apt-get update
```

## fix-ocaml-gc — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/fix-ocaml-gc/tests/test.sh:5
```sh
apt-get install -y curl
```

## fix-ocaml-gc — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/fix-ocaml-gc/tests/test.sh:8
```sh
curl -LsSf https://astral.sh/uv/0.9.5/install.sh | sh
```

## fix-ocaml-gc — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/fix-ocaml-gc/tests/test.sh:30
```sh
uvx \
  -p 3.13 \
  -w pytest==8.4.1 \
  -w pytest-json-ctrf==0.3.5 \
  pytest --ctrf /logs/verifier/ctrf.json /tests/test_outputs.py -rA
```

## gcode-to-text — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/gcode-to-text/tests/test.sh:4
```sh
apt-get update
```

## gcode-to-text — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/gcode-to-text/tests/test.sh:5
```sh
apt-get install -y curl
```

## gcode-to-text — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/gcode-to-text/tests/test.sh:8
```sh
curl -LsSf https://astral.sh/uv/0.9.5/install.sh | sh
```

## gcode-to-text — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/gcode-to-text/tests/test.sh:18
```sh
uvx \
  -p 3.13 \
  -w pytest==8.4.1 \
  -w pytest-json-ctrf==0.3.5 \
  pytest --ctrf /logs/verifier/ctrf.json /tests/test_outputs.py -rA
```

## git-leak-recovery — image-build
/mnt/20t/xubuqiang/datasets/terminal-bench/git-leak-recovery/environment/Dockerfile:7
```sh
RUN apt-get update && apt-get install -y git
```

## git-leak-recovery — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/git-leak-recovery/tests/test.sh:4
```sh
apt-get update
```

## git-leak-recovery — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/git-leak-recovery/tests/test.sh:5
```sh
apt-get install -y curl
```

## git-leak-recovery — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/git-leak-recovery/tests/test.sh:8
```sh
curl -LsSf https://astral.sh/uv/0.9.5/install.sh | sh
```

## git-leak-recovery — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/git-leak-recovery/tests/test.sh:18
```sh
uvx \
  -p 3.13 \
  -w pytest==8.4.1 \
  -w pytest-json-ctrf==0.3.5 \
  pytest --ctrf /logs/verifier/ctrf.json /tests/test_outputs.py -rA
```

## git-multibranch — image-build
/mnt/20t/xubuqiang/datasets/terminal-bench/git-multibranch/environment/Dockerfile:5
```sh
RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y \
    nginx \
    openssh-server \
    git \
    curl \
    openssl \
    python3 \
    python3-pip \
    net-tools \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*
```

## git-multibranch — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/git-multibranch/tests/test.sh:4
```sh
apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y expect curl
```

## git-multibranch — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/git-multibranch/tests/test.sh:7
```sh
curl -LsSf https://astral.sh/uv/0.9.5/install.sh | sh
```

## git-multibranch — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/git-multibranch/tests/test.sh:17
```sh
uvx \
  -p 3.13 \
  -w pytest==8.4.1 \
  -w pytest-json-ctrf==0.3.5 \
  pytest --ctrf /logs/verifier/ctrf.json /tests/test_outputs.py -rA
```

## git-multibranch — other-source
/mnt/20t/xubuqiang/datasets/terminal-bench/git-multibranch/tests/test_outputs.py:12
```sh
apt-get update
```

## git-multibranch — other-source
/mnt/20t/xubuqiang/datasets/terminal-bench/git-multibranch/tests/test_outputs.py:13
```sh
DEBIAN_FRONTEND=noninteractive apt-get install -y curl expect git openssh-client
```

## gpt2-codegolf — image-build
/mnt/20t/xubuqiang/datasets/terminal-bench/gpt2-codegolf/environment/Dockerfile:5
```sh
RUN apt-get update && apt-get install -y curl gcc
```

## gpt2-codegolf — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/gpt2-codegolf/tests/test.sh:4
```sh
apt-get update
```

## gpt2-codegolf — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/gpt2-codegolf/tests/test.sh:5
```sh
apt-get install -y curl
```

## gpt2-codegolf — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/gpt2-codegolf/tests/test.sh:8
```sh
curl -LsSf https://astral.sh/uv/0.9.5/install.sh | sh
```

## gpt2-codegolf — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/gpt2-codegolf/tests/test.sh:18
```sh
uvx \
  -p 3.13 \
  -w pytest==8.4.1 \
  -w pytest-json-ctrf==0.3.5 \
  pytest --ctrf /logs/verifier/ctrf.json /tests/test_outputs.py -rA
```

## headless-terminal — image-build
/mnt/20t/xubuqiang/datasets/terminal-bench/headless-terminal/environment/Dockerfile:5
```sh
RUN apt-get update -y && apt-get install -y tmux screen expect
```

## headless-terminal — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/headless-terminal/tests/test.sh:4
```sh
apt-get update
```

## headless-terminal — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/headless-terminal/tests/test.sh:5
```sh
apt-get install -y vim
```

## headless-terminal — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/headless-terminal/tests/test.sh:13
```sh
pip install pytest==8.4.1 requests==2.32.5 pytest-json-ctrf==0.3.5
```

## hf-model-inference — image-build
/mnt/20t/xubuqiang/datasets/terminal-bench/hf-model-inference/environment/Dockerfile:5
```sh
RUN pip install transformers==4.56.0 torch==2.7.1 flask==3.1.1
```

## hf-model-inference — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/hf-model-inference/tests/test.sh:4
```sh
pip install pytest==8.4.1 psutil==7.0.0 requests==2.32.4 pytest-json-ctrf==0.3.5
```

## install-windows-3.11 — image-build
/mnt/20t/xubuqiang/datasets/terminal-bench/install-windows-3.11/environment/Dockerfile:14
```sh
RUN apt-get update && \
    echo "tzdata tzdata/Areas select America" > ~/tx.txt && \
    echo "tzdata tzdata/Zones/America select New_York" >> ~/tx.txt && \
    debconf-set-selections ~/tx.txt && \
    apt-get install -y \
    wget \
    ratpoison \
    novnc \
    websockify \
    libxv1 \
    xauth \
    x11-utils \
    xserver-common \
    xserver-xorg-core \
    xserver-xorg-input-evdev \
    xserver-xorg-video-dummy \
    tightvncserver \
    x11-xkb-utils \
    gstreamer1.0-plugins-good \
    gstreamer1.0-pulseaudio \
    gstreamer1.0-tools \
    libgtk2.0-0 \
    libopenal1 \
    libsndfile1 \
    nginx \
    pulseaudio \
    supervisor \
    ucspi-tcp \
    vncsnapshot \
    bc \
    file \
    build-essential \
    python3 \
    pkg-config \
    libglib2.0-dev \
    libfdt-dev \
    libpixman-1-dev \
    zlib1g-dev \
    libnfs-dev \
    libiscsi-dev \
    ninja-build \
    meson \
    && rm -rf /var/lib/apt/lists/*
```

## install-windows-3.11 — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/install-windows-3.11/tests/test.sh:4
```sh
apt-get update
```

## install-windows-3.11 — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/install-windows-3.11/tests/test.sh:5
```sh
apt-get install -y curl
```

## install-windows-3.11 — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/install-windows-3.11/tests/test.sh:8
```sh
curl -LsSf https://astral.sh/uv/0.9.5/install.sh | sh
```

## install-windows-3.11 — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/install-windows-3.11/tests/test.sh:19
```sh
apt-get update -qq && apt-get install -y mtools socat vncsnapshot tesseract-ocr
```

## install-windows-3.11 — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/install-windows-3.11/tests/test.sh:21
```sh
uvx \
  -p 3.13 \
  -w pytest==8.4.1 \
  -w opencv-python==4.11.0.86 \
  -w numpy==2.3.1 \
  -w pytesseract==0.3.13 \
  -w pytest-json-ctrf==0.3.5 \
  pytest --ctrf /logs/verifier/ctrf.json /tests/test_outputs.py -rA
```

## kv-store-grpc — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/kv-store-grpc/tests/test.sh:4
```sh
pip install pytest==8.4.2 requests==2.32.5 psutil==7.0.0 pytest-json-ctrf==0.3.5
```

## large-scale-text-editing — image-build
/mnt/20t/xubuqiang/datasets/terminal-bench/large-scale-text-editing/environment/Dockerfile:7
```sh
RUN apt-get update && apt-get install -y vim && rm -rf /var/lib/apt/lists/*
```

## large-scale-text-editing — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/large-scale-text-editing/tests/test.sh:4
```sh
apt-get update
```

## large-scale-text-editing — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/large-scale-text-editing/tests/test.sh:5
```sh
apt-get install -y curl
```

## large-scale-text-editing — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/large-scale-text-editing/tests/test.sh:8
```sh
curl -LsSf https://astral.sh/uv/0.9.5/install.sh | sh
```

## large-scale-text-editing — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/large-scale-text-editing/tests/test.sh:27
```sh
uvx \
  -p 3.13 \
  -w pytest==8.4.1 \
  -w pytest-json-ctrf==0.3.5 \
  pytest --ctrf /logs/verifier/ctrf.json /tests/test_outputs.py -rA
```

## largest-eigenval — image-build
/mnt/20t/xubuqiang/datasets/terminal-bench/largest-eigenval/environment/Dockerfile:7
```sh
RUN pip install numpy==2.3.0
```

## largest-eigenval — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/largest-eigenval/tests/test.sh:9
```sh
pip install pytest==8.4.1 pytest-json-ctrf==0.3.5 --break-system-packages
```

## llm-inference-batching-scheduler — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/llm-inference-batching-scheduler/tests/test.sh:6
```sh
apt-get update
```

## llm-inference-batching-scheduler — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/llm-inference-batching-scheduler/tests/test.sh:7
```sh
apt-get install -y curl
```

## llm-inference-batching-scheduler — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/llm-inference-batching-scheduler/tests/test.sh:10
```sh
curl -LsSf https://astral.sh/uv/0.9.5/install.sh | sh
```

## llm-inference-batching-scheduler — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/llm-inference-batching-scheduler/tests/test.sh:20
```sh
uvx \
  -p 3.13 \
  -w pytest==8.4.1 \
  -w pytest-json-ctrf==0.3.5 \
  pytest --ctrf /logs/verifier/ctrf.json /tests/test_outputs.py -rA
```

## log-summary-date-ranges — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/log-summary-date-ranges/tests/test.sh:4
```sh
apt-get update
```

## log-summary-date-ranges — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/log-summary-date-ranges/tests/test.sh:5
```sh
apt-get install -y curl
```

## log-summary-date-ranges — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/log-summary-date-ranges/tests/test.sh:8
```sh
curl -LsSf https://astral.sh/uv/0.9.5/install.sh | sh
```

## log-summary-date-ranges — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/log-summary-date-ranges/tests/test.sh:18
```sh
uvx \
  -p 3.13 \
  -w pytest==8.4.1 \
  -w pytest-json-ctrf==0.3.5 \
  pytest --ctrf /logs/verifier/ctrf.json /tests/test_outputs.py -rA
```

## mailman — image-build
/mnt/20t/xubuqiang/datasets/terminal-bench/mailman/environment/Dockerfile:7
```sh
RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y -qq \
    postfix \
    mailutils \
    mailman3
```

## mailman — image-build
/mnt/20t/xubuqiang/datasets/terminal-bench/mailman/environment/Dockerfile:12
```sh
RUN apt-get install -y -qq less nano net-tools && \
    rm -rf /var/lib/apt/lists/*
```

## mailman — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/mailman/tests/test.sh:9
```sh
apt-get update
```

## mailman — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/mailman/tests/test.sh:10
```sh
apt-get install -y curl
```

## mailman — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/mailman/tests/test.sh:13
```sh
curl -LsSf https://astral.sh/uv/0.9.5/install.sh | sh
```

## mailman — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/mailman/tests/test.sh:23
```sh
uv venv -p 3.12 .tb
```

## mailman — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/mailman/tests/test.sh:26
```sh
uv pip install pytest==8.4.1 mailman==3.3.8 pytest-json-ctrf==0.3.5
```

## mailman — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/mailman/tests/test.sh:28
```sh
uv run pytest --ctrf /logs/verifier/ctrf.json /tests/test_outputs.py -rA
```

## make-doom-for-mips — image-build
/mnt/20t/xubuqiang/datasets/terminal-bench/make-doom-for-mips/environment/Dockerfile:5
```sh
RUN apt-get update -y
```

## make-doom-for-mips — image-build
/mnt/20t/xubuqiang/datasets/terminal-bench/make-doom-for-mips/environment/Dockerfile:6
```sh
RUN apt-get install -y nodejs curl git make
```

## make-doom-for-mips — image-build
/mnt/20t/xubuqiang/datasets/terminal-bench/make-doom-for-mips/environment/Dockerfile:8
```sh
RUN pip3 install numpy==2.3.1 pillow==11.2.1 --break-system-packages
```

## make-doom-for-mips — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/make-doom-for-mips/tests/test.sh:4
```sh
apt-get update
```

## make-doom-for-mips — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/make-doom-for-mips/tests/test.sh:5
```sh
apt-get install -y curl python3-pillow
```

## make-doom-for-mips — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/make-doom-for-mips/tests/test.sh:8
```sh
curl -LsSf https://astral.sh/uv/0.9.5/install.sh | sh
```

## make-doom-for-mips — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/make-doom-for-mips/tests/test.sh:18
```sh
uvx \
  -p 3.13 \
  -w pytest==8.4.1 \
  -w numpy==2.3.1 \
  -w pillow==11.2.1 \
  -w pytest-json-ctrf==0.3.5 \
  pytest --ctrf /logs/verifier/ctrf.json /tests/test_outputs.py -rA
```

## make-mips-interpreter — image-build
/mnt/20t/xubuqiang/datasets/terminal-bench/make-mips-interpreter/environment/Dockerfile:5
```sh
RUN apt-get update -y && \
    apt-get install -y nodejs curl git make && \
    apt-get install -y clang gcc-mips-linux-gnu g++-mips-linux-gnu llvm llvm-dev lld
```

## make-mips-interpreter — image-build
/mnt/20t/xubuqiang/datasets/terminal-bench/make-mips-interpreter/environment/Dockerfile:9
```sh
RUN pip3 install numpy==2.3.1 pillow==11.2.1 --break-system-packages
```

## make-mips-interpreter — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/make-mips-interpreter/tests/test.sh:4
```sh
apt-get update
```

## make-mips-interpreter — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/make-mips-interpreter/tests/test.sh:5
```sh
apt-get install -y curl python3-pillow
```

## make-mips-interpreter — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/make-mips-interpreter/tests/test.sh:8
```sh
curl -LsSf https://astral.sh/uv/0.9.5/install.sh | sh
```

## make-mips-interpreter — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/make-mips-interpreter/tests/test.sh:18
```sh
uvx \
  -p 3.13 \
  -w pytest==8.4.1 \
  -w numpy==2.3.1 \
  -w pillow==11.2.1 \
  -w pytest-json-ctrf==0.3.5 \
  pytest --ctrf /logs/verifier/ctrf.json /tests/test_outputs.py -rA
```

## mcmc-sampling-stan — image-build
/mnt/20t/xubuqiang/datasets/terminal-bench/mcmc-sampling-stan/environment/Dockerfile:4
```sh
RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        r-base \
        python3 \
        python3-pip \
        build-essential \
        curl \
        sudo && \
    rm -rf /var/lib/apt/lists/*
```

## mcmc-sampling-stan — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/mcmc-sampling-stan/tests/test.sh:7
```sh
apt-get update
```

## mcmc-sampling-stan — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/mcmc-sampling-stan/tests/test.sh:8
```sh
apt-get install -y curl
```

## mcmc-sampling-stan — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/mcmc-sampling-stan/tests/test.sh:11
```sh
curl -LsSf https://astral.sh/uv/0.9.5/install.sh | sh
```

## mcmc-sampling-stan — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/mcmc-sampling-stan/tests/test.sh:22
```sh
uvx \
  -p 3.13 \
  -w pytest==8.3.4 \
  -w pytest-json-ctrf==0.3.5 \
  pytest --ctrf /logs/verifier/ctrf.json test_outputs.py -rA
```

## merge-diff-arc-agi-task — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/merge-diff-arc-agi-task/tests/test.sh:4
```sh
apt-get update
```

## merge-diff-arc-agi-task — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/merge-diff-arc-agi-task/tests/test.sh:5
```sh
apt-get install -y curl git
```

## merge-diff-arc-agi-task — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/merge-diff-arc-agi-task/tests/test.sh:8
```sh
curl -LsSf https://astral.sh/uv/0.9.5/install.sh | sh
```

## merge-diff-arc-agi-task — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/merge-diff-arc-agi-task/tests/test.sh:18
```sh
uvx \
  -p 3.13 \
  -w pytest==8.4.1 \
  -w pytest-json-ctrf==0.3.5 \
  pytest --ctrf /logs/verifier/ctrf.json /tests/test_outputs.py -rA
```

## model-extraction-relu-logits — image-build
/mnt/20t/xubuqiang/datasets/terminal-bench/model-extraction-relu-logits/environment/Dockerfile:9
```sh
RUN pip install numpy==2.2.5
```

## model-extraction-relu-logits — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/model-extraction-relu-logits/tests/test.sh:4
```sh
apt-get update
```

## model-extraction-relu-logits — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/model-extraction-relu-logits/tests/test.sh:5
```sh
apt-get install -y curl
```

## model-extraction-relu-logits — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/model-extraction-relu-logits/tests/test.sh:8
```sh
curl -LsSf https://astral.sh/uv/0.9.5/install.sh | sh
```

## model-extraction-relu-logits — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/model-extraction-relu-logits/tests/test.sh:18
```sh
uvx \
  -p 3.13 \
  -w pytest==8.4.1 \
  -w numpy==2.3.1 \
  -w pytest-json-ctrf==0.3.5 \
  pytest --ctrf /logs/verifier/ctrf.json /tests/test_outputs.py -rA
```

## modernize-scientific-stack — image-build
/mnt/20t/xubuqiang/datasets/terminal-bench/modernize-scientific-stack/environment/Dockerfile:7
```sh
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    gfortran \
    libblas-dev \
    liblapack-dev \
    libhdf5-dev \
    pkg-config \
    git \
    curl \
    wget \
    && rm -rf /var/lib/apt/lists/*
```

## modernize-scientific-stack — image-build
/mnt/20t/xubuqiang/datasets/terminal-bench/modernize-scientific-stack/environment/Dockerfile:22
```sh
RUN pip install --no-cache-dir \
    numpy==2.3.2 \
    pandas==2.3.2 \
    matplotlib==3.10.6 \
    scipy==1.16.1
```

## modernize-scientific-stack — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/modernize-scientific-stack/tests/test.sh:4
```sh
apt-get update
```

## modernize-scientific-stack — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/modernize-scientific-stack/tests/test.sh:5
```sh
apt-get install -y curl
```

## modernize-scientific-stack — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/modernize-scientific-stack/tests/test.sh:8
```sh
curl -LsSf https://astral.sh/uv/0.9.5/install.sh | sh
```

## modernize-scientific-stack — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/modernize-scientific-stack/tests/test.sh:18
```sh
uvx \
  -p 3.13 \
  -w pytest==8.4.1 \
  -w numpy==2.3.4 \
  -w pandas==2.3.3 \
  -w matplotlib==3.10.7 \
  -w scipy==1.16.3 \
  -w pytest-json-ctrf==0.3.5 \
  pytest --ctrf /logs/verifier/ctrf.json /tests/test_outputs.py -rA
```

## mteb-leaderboard — image-build
/mnt/20t/xubuqiang/datasets/terminal-bench/mteb-leaderboard/environment/Dockerfile:4
```sh
RUN apt-get update && apt-get install -y \
    tmux asciinema gcc g++ git wget \
    && rm -rf /var/lib/apt/lists/*
```

## mteb-leaderboard — image-build
/mnt/20t/xubuqiang/datasets/terminal-bench/mteb-leaderboard/environment/Dockerfile:10
```sh
RUN pip install mteb==1.38.41
```

## mteb-leaderboard — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/mteb-leaderboard/tests/test.sh:4
```sh
apt-get update
```

## mteb-leaderboard — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/mteb-leaderboard/tests/test.sh:5
```sh
apt-get install -y curl
```

## mteb-leaderboard — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/mteb-leaderboard/tests/test.sh:8
```sh
curl -LsSf https://astral.sh/uv/0.9.5/install.sh | sh
```

## mteb-leaderboard — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/mteb-leaderboard/tests/test.sh:18
```sh
uvx \
  -p 3.13 \
  -w pytest==8.4.1 \
  -w pytest-json-ctrf==0.3.5 \
  pytest --ctrf /logs/verifier/ctrf.json /tests/test_outputs.py -rA
```

## mteb-retrieve — image-build
/mnt/20t/xubuqiang/datasets/terminal-bench/mteb-retrieve/environment/Dockerfile:4
```sh
RUN apt-get update && apt-get install -y \
    tmux asciinema gcc g++\
    && rm -rf /var/lib/apt/lists/*
```

## mteb-retrieve — image-build
/mnt/20t/xubuqiang/datasets/terminal-bench/mteb-retrieve/environment/Dockerfile:10
```sh
RUN apt-get update && apt-get install -y wget
```

## mteb-retrieve — image-build
/mnt/20t/xubuqiang/datasets/terminal-bench/mteb-retrieve/environment/Dockerfile:12
```sh
RUN pip install mteb==1.36.8
```

## mteb-retrieve — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/mteb-retrieve/tests/test.sh:4
```sh
apt-get update
```

## mteb-retrieve — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/mteb-retrieve/tests/test.sh:5
```sh
apt-get install -y curl
```

## mteb-retrieve — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/mteb-retrieve/tests/test.sh:8
```sh
curl -LsSf https://astral.sh/uv/0.9.5/install.sh | sh
```

## mteb-retrieve — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/mteb-retrieve/tests/test.sh:18
```sh
uvx \
  -p 3.13 \
  -w pytest==8.4.1 \
  -w mteb==1.36.8 \
  -w pytest-json-ctrf==0.3.5 \
  pytest --ctrf /logs/verifier/ctrf.json /tests/test_outputs.py -rA
```

## multi-source-data-merger — image-build
/mnt/20t/xubuqiang/datasets/terminal-bench/multi-source-data-merger/environment/Dockerfile:5
```sh
RUN apt-get update && apt-get install -y \
    tmux \
    asciinema \
    && rm -rf /var/lib/apt/lists/*
```

## multi-source-data-merger — image-build
/mnt/20t/xubuqiang/datasets/terminal-bench/multi-source-data-merger/environment/Dockerfile:11
```sh
RUN pip install pandas==2.2.3 pyarrow==17.0.0
```

## multi-source-data-merger — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/multi-source-data-merger/tests/test.sh:4
```sh
apt-get update
```

## multi-source-data-merger — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/multi-source-data-merger/tests/test.sh:5
```sh
apt-get install -y curl
```

## multi-source-data-merger — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/multi-source-data-merger/tests/test.sh:8
```sh
curl -LsSf https://astral.sh/uv/0.9.5/install.sh | sh
```

## multi-source-data-merger — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/multi-source-data-merger/tests/test.sh:18
```sh
uvx \
  -p 3.13 \
  -w pytest==8.4.1 \
  -w pandas==2.3.3 \
  -w pyarrow==22.0.0 \
  -w pytest-json-ctrf==0.3.5 \
  pytest --ctrf /logs/verifier/ctrf.json /tests/test_outputs.py -rA
```

## nginx-request-logging — image-build
/mnt/20t/xubuqiang/datasets/terminal-bench/nginx-request-logging/environment/Dockerfile:5
```sh
RUN pip install requests==2.32.4
```

## nginx-request-logging — image-build
/mnt/20t/xubuqiang/datasets/terminal-bench/nginx-request-logging/environment/Dockerfile:7
```sh
RUN apt-get update && apt-get install -y curl
```

## nginx-request-logging — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/nginx-request-logging/tests/test.sh:4
```sh
apt-get update
```

## nginx-request-logging — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/nginx-request-logging/tests/test.sh:5
```sh
apt-get install -y curl
```

## nginx-request-logging — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/nginx-request-logging/tests/test.sh:8
```sh
curl -LsSf https://astral.sh/uv/0.9.5/install.sh | sh
```

## nginx-request-logging — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/nginx-request-logging/tests/test.sh:17
```sh
uvx \
  -p 3.13 \
  -w pytest==8.4.1 \
  -w requests==2.32.4 \
  -w pytest-json-ctrf==0.3.5 \
  pytest --ctrf /logs/verifier/ctrf.json /tests/test_outputs.py -v -rA
```

## openssl-selfsigned-cert — image-build
/mnt/20t/xubuqiang/datasets/terminal-bench/openssl-selfsigned-cert/environment/Dockerfile:5
```sh
RUN apt-get update && apt-get install -y \
    openssl \
    && rm -rf /var/lib/apt/lists/*
```

## openssl-selfsigned-cert — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/openssl-selfsigned-cert/tests/test.sh:4
```sh
apt-get update
```

## openssl-selfsigned-cert — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/openssl-selfsigned-cert/tests/test.sh:5
```sh
apt-get install -y curl
```

## openssl-selfsigned-cert — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/openssl-selfsigned-cert/tests/test.sh:8
```sh
curl -LsSf https://astral.sh/uv/0.9.5/install.sh | sh
```

## openssl-selfsigned-cert — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/openssl-selfsigned-cert/tests/test.sh:18
```sh
uvx \
  -p 3.13 \
  -w pytest==8.4.1 \
  -w pytest-json-ctrf==0.3.5 \
  pytest --ctrf /logs/verifier/ctrf.json /tests/test_outputs.py -rA
```

## overfull-hbox — image-build
/mnt/20t/xubuqiang/datasets/terminal-bench/overfull-hbox/environment/Dockerfile:6
```sh
RUN apt-get update && \
    apt-get install -y --no-install-recommends texlive-latex-base=2023.20240207-1 && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*
```

## overfull-hbox — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/overfull-hbox/tests/test.sh:9
```sh
apt-get update
```

## overfull-hbox — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/overfull-hbox/tests/test.sh:10
```sh
apt-get install -y curl
```

## overfull-hbox — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/overfull-hbox/tests/test.sh:13
```sh
curl -LsSf https://astral.sh/uv/0.9.5/install.sh | sh
```

## overfull-hbox — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/overfull-hbox/tests/test.sh:23
```sh
uvx \
  -p 3.13 \
  -w pytest==8.4.1 \
  -w pytest-json-ctrf==0.3.5 \
  pytest --ctrf /logs/verifier/ctrf.json /tests/test_outputs.py -rA
```

## overfull-hbox — other-source
/mnt/20t/xubuqiang/datasets/terminal-bench/overfull-hbox/tests/test_outputs.py:18
```sh
    os.system('apt install -y --reinstall texlive-latex-base')
```

## password-recovery — image-build
/mnt/20t/xubuqiang/datasets/terminal-bench/password-recovery/environment/Dockerfile:5
```sh
RUN apt-get update -y \
    && apt-get install -y \
    extundelete \
    foremost \
    sleuthkit \
    e2fsprogs \
    binutils \
    zip \
    unzip \
    && rm -rf /var/lib/apt/lists/*
```

## password-recovery — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/password-recovery/tests/test.sh:4
```sh
apt-get update
```

## password-recovery — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/password-recovery/tests/test.sh:5
```sh
apt-get install -y curl
```

## password-recovery — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/password-recovery/tests/test.sh:8
```sh
curl -LsSf https://astral.sh/uv/0.9.5/install.sh | sh
```

## password-recovery — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/password-recovery/tests/test.sh:18
```sh
uvx \
  -p 3.13 \
  -w pytest==8.4.1 \
  -w pytest-json-ctrf==0.3.5 \
  pytest --ctrf /logs/verifier/ctrf.json /tests/test_outputs.py -rA
```

## path-tracing — image-build
/mnt/20t/xubuqiang/datasets/terminal-bench/path-tracing/environment/Dockerfile:5
```sh
RUN apt-get update -y --fix-missing && \
    apt-get install -y ffmpeg gcc curl
```

## path-tracing — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/path-tracing/tests/test.sh:4
```sh
apt-get update
```

## path-tracing — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/path-tracing/tests/test.sh:5
```sh
apt-get install -y curl
```

## path-tracing — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/path-tracing/tests/test.sh:8
```sh
curl -LsSf https://astral.sh/uv/0.9.5/install.sh | sh
```

## path-tracing — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/path-tracing/tests/test.sh:18
```sh
uvx \
  -p 3.13 \
  -w pytest==8.4.1 \
  -w pillow==11.2.1 \
  -w numpy==2.3.1 \
  -w pytest-json-ctrf==0.3.5 \
  pytest --ctrf /logs/verifier/ctrf.json /tests/test_outputs.py -rA
```

## path-tracing-reverse — image-build
/mnt/20t/xubuqiang/datasets/terminal-bench/path-tracing-reverse/environment/Dockerfile:5
```sh
RUN apt-get update && apt-get install -y gcc g++ curl zlib1g-dev libjpeg-dev
```

## path-tracing-reverse — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/path-tracing-reverse/tests/test.sh:4
```sh
apt-get update
```

## path-tracing-reverse — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/path-tracing-reverse/tests/test.sh:5
```sh
apt-get install -y curl
```

## path-tracing-reverse — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/path-tracing-reverse/tests/test.sh:8
```sh
curl -LsSf https://astral.sh/uv/0.9.5/install.sh | sh
```

## path-tracing-reverse — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/path-tracing-reverse/tests/test.sh:18
```sh
uvx \
  -p 3.13 \
  -w pytest==8.4.1 \
  -w pillow==11.2.1 \
  -w numpy==2.3.1 \
  -w pytest-json-ctrf==0.3.5 \
  pytest --ctrf /logs/verifier/ctrf.json /tests/test_outputs.py -rA
```

## polyglot-c-py — image-build
/mnt/20t/xubuqiang/datasets/terminal-bench/polyglot-c-py/environment/Dockerfile:6
```sh
RUN apt update -y && apt install -y gcc
```

## polyglot-c-py — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/polyglot-c-py/tests/test.sh:4
```sh
apt-get update
```

## polyglot-c-py — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/polyglot-c-py/tests/test.sh:5
```sh
apt-get install -y curl
```

## polyglot-c-py — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/polyglot-c-py/tests/test.sh:8
```sh
curl -LsSf https://astral.sh/uv/0.9.5/install.sh | sh
```

## polyglot-c-py — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/polyglot-c-py/tests/test.sh:18
```sh
uvx \
  -p 3.13 \
  -w pytest==8.4.1 \
  -w pytest-json-ctrf==0.3.5 \
  pytest --ctrf /logs/verifier/ctrf.json /tests/test_outputs.py -rA
```

## polyglot-rust-c — image-build
/mnt/20t/xubuqiang/datasets/terminal-bench/polyglot-rust-c/environment/Dockerfile:5
```sh
RUN apt update -y && apt install -y rustc g++ && \
    rm -rf /var/lib/apt/lists/*
```

## polyglot-rust-c — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/polyglot-rust-c/tests/test.sh:4
```sh
apt-get update
```

## polyglot-rust-c — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/polyglot-rust-c/tests/test.sh:5
```sh
apt-get install -y curl
```

## polyglot-rust-c — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/polyglot-rust-c/tests/test.sh:8
```sh
curl -LsSf https://astral.sh/uv/0.9.5/install.sh | sh
```

## polyglot-rust-c — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/polyglot-rust-c/tests/test.sh:18
```sh
uvx \
  -p 3.13 \
  -w pytest==8.4.1 \
  -w pytest-json-ctrf==0.3.5 \
  pytest --ctrf /logs/verifier/ctrf.json /tests/test_outputs.py -rA
```

## portfolio-optimization — image-build
/mnt/20t/xubuqiang/datasets/terminal-bench/portfolio-optimization/environment/Dockerfile:6
```sh
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    build-essential \
    && rm -rf /var/lib/apt/lists/*
```

## portfolio-optimization — image-build
/mnt/20t/xubuqiang/datasets/terminal-bench/portfolio-optimization/environment/Dockerfile:18
```sh
RUN pip install --no-cache-dir \
    numpy==2.3.2 \
    setuptools==78.1.1
```

## portfolio-optimization — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/portfolio-optimization/tests/test.sh:4
```sh
apt-get update
```

## portfolio-optimization — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/portfolio-optimization/tests/test.sh:5
```sh
apt-get install -y curl
```

## portfolio-optimization — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/portfolio-optimization/tests/test.sh:8
```sh
curl -LsSf https://astral.sh/uv/0.9.5/install.sh | sh
```

## portfolio-optimization — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/portfolio-optimization/tests/test.sh:18
```sh
uvx \
  -p 3.13 \
  -w pytest==8.4.1 \
  -w numpy==2.3.2 \
  -w setuptools==78.1.1 \
  -w pytest-json-ctrf==0.3.5 \
  pytest --ctrf /logs/verifier/ctrf.json /tests/test_outputs.py -rA
```

## protein-assembly — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/protein-assembly/tests/test.sh:4
```sh
apt-get update
```

## protein-assembly — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/protein-assembly/tests/test.sh:5
```sh
apt-get install -y curl
```

## protein-assembly — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/protein-assembly/tests/test.sh:8
```sh
curl -LsSf https://astral.sh/uv/0.9.5/install.sh | sh
```

## protein-assembly — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/protein-assembly/tests/test.sh:18
```sh
uvx \
  -p 3.13 \
  -w pytest==8.4.1 \
  -w biopython==1.85 \
  -w pytest-json-ctrf==0.3.5 \
  pytest --ctrf /logs/verifier/ctrf.json /tests/test_outputs.py -rA
```

## prove-plus-comm — image-build
/mnt/20t/xubuqiang/datasets/terminal-bench/prove-plus-comm/environment/Dockerfile:5
```sh
RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y \
    coq \
    && rm -rf /var/lib/apt/lists/*
```

## prove-plus-comm — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/prove-plus-comm/tests/test.sh:4
```sh
apt-get update
```

## prove-plus-comm — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/prove-plus-comm/tests/test.sh:5
```sh
apt-get install -y curl
```

## prove-plus-comm — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/prove-plus-comm/tests/test.sh:8
```sh
curl -LsSf https://astral.sh/uv/0.9.5/install.sh | sh
```

## prove-plus-comm — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/prove-plus-comm/tests/test.sh:18
```sh
uvx \
  -p 3.13 \
  -w pytest==8.4.1 \
  -w pytest-json-ctrf==0.3.5 \
  pytest --ctrf /logs/verifier/ctrf.json /tests/test_outputs.py -rA
```

## pypi-server — image-build
/mnt/20t/xubuqiang/datasets/terminal-bench/pypi-server/environment/Dockerfile:5
```sh
RUN apt update -y && apt install -y curl vim
```

## pypi-server — image-build
/mnt/20t/xubuqiang/datasets/terminal-bench/pypi-server/environment/Dockerfile:10
```sh
RUN python3 -m pip install --upgrade pip==25.2
```

## pypi-server — image-build
/mnt/20t/xubuqiang/datasets/terminal-bench/pypi-server/environment/Dockerfile:11
```sh
RUN python3 -m pip install --upgrade setuptools==75.6.0 wheel==0.45.1
```

## pypi-server — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/pypi-server/tests/test.sh:4
```sh
apt-get update
```

## pypi-server — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/pypi-server/tests/test.sh:5
```sh
apt-get install -y curl
```

## pypi-server — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/pypi-server/tests/test.sh:8
```sh
curl -LsSf https://astral.sh/uv/0.9.5/install.sh | sh
```

## pypi-server — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/pypi-server/tests/test.sh:18
```sh
uvx \
  -p 3.13 \
  -w pytest==8.4.1 \
  -w pip==25.2 \
  -w pytest-json-ctrf==0.3.5 \
  pytest --ctrf /logs/verifier/ctrf.json /tests/test_outputs.py -rA
```

## pypi-server — other-source
/mnt/20t/xubuqiang/datasets/terminal-bench/pypi-server/tests/test_outputs.py:21
```sh
        subprocess.CalledProcessError: If pip uninstall or install commands fail.
```

## pypi-server — other-source
/mnt/20t/xubuqiang/datasets/terminal-bench/pypi-server/tests/test_outputs.py:23
```sh
    uninstallcmd = ["python", "-m", "pip", "uninstall", "-y", "vectorops"]
```

## pypi-server — other-source
/mnt/20t/xubuqiang/datasets/terminal-bench/pypi-server/tests/test_outputs.py:27
```sh
        "pip",
```

## pypi-server — other-source
/mnt/20t/xubuqiang/datasets/terminal-bench/pypi-server/tests/test_outputs.py:58
```sh
        ["python", "-m", "pip", "show", "vectorops"],
```

## pytorch-model-cli — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/pytorch-model-cli/tests/test.sh:4
```sh
apt-get update
```

## pytorch-model-cli — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/pytorch-model-cli/tests/test.sh:5
```sh
apt-get install -y curl ffmpeg libsm6 libxext6
```

## pytorch-model-cli — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/pytorch-model-cli/tests/test.sh:8
```sh
curl -LsSf https://astral.sh/uv/0.9.5/install.sh | sh
```

## pytorch-model-cli — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/pytorch-model-cli/tests/test.sh:17
```sh
uvx \
  --index https://download.pytorch.org/whl/cpu \
  --index-strategy unsafe-best-match \
  -p 3.13 \
  -w torch==2.7.1 \
  -w torchvision==0.22.1 \
  -w numpy==2.3.1 \
  -w opencv-python==4.11.0.86 \
  -w pytest==8.4.1 \
  -w pytest-json-ctrf==0.3.5 \
  pytest --ctrf /logs/verifier/ctrf.json /tests/test_outputs.py -v -rA
```

## pytorch-model-recovery — image-build
/mnt/20t/xubuqiang/datasets/terminal-bench/pytorch-model-recovery/environment/Dockerfile:10
```sh
RUN apt-get update && apt-get install -y nano
```

## pytorch-model-recovery — image-build
/mnt/20t/xubuqiang/datasets/terminal-bench/pytorch-model-recovery/environment/Dockerfile:12
```sh
RUN pip install torch==2.7.1
```

## pytorch-model-recovery — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/pytorch-model-recovery/tests/test.sh:4
```sh
apt-get update
```

## pytorch-model-recovery — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/pytorch-model-recovery/tests/test.sh:5
```sh
apt-get install -y curl
```

## pytorch-model-recovery — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/pytorch-model-recovery/tests/test.sh:8
```sh
curl -LsSf https://astral.sh/uv/0.9.5/install.sh | sh
```

## pytorch-model-recovery — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/pytorch-model-recovery/tests/test.sh:18
```sh
uvx \
  -p 3.13 \
  -w pytest==8.4.1 \
  -w torch==2.7.1 \
  -w pytest-json-ctrf==0.3.5 \
  pytest --ctrf /logs/verifier/ctrf.json /tests/test_outputs.py -rA
```

## qemu-alpine-ssh — image-build
/mnt/20t/xubuqiang/datasets/terminal-bench/qemu-alpine-ssh/environment/Dockerfile:5
```sh
RUN apt-get update && apt-get install -y \
    qemu-system-x86 \
    qemu-utils \
    wget \
    ca-certificates \
    openssh-client \
    && rm -rf /var/lib/apt/lists/*
```

## qemu-alpine-ssh — image-build
/mnt/20t/xubuqiang/datasets/terminal-bench/qemu-alpine-ssh/environment/Dockerfile:22
```sh
RUN apt update -y
```

## qemu-alpine-ssh — image-build
/mnt/20t/xubuqiang/datasets/terminal-bench/qemu-alpine-ssh/environment/Dockerfile:23
```sh
RUN apt install -y telnet netcat expect tmux asciinema
```

## qemu-alpine-ssh — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/qemu-alpine-ssh/tests/test.sh:4
```sh
apt-get update
```

## qemu-alpine-ssh — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/qemu-alpine-ssh/tests/test.sh:5
```sh
apt-get install -y curl sshpass
```

## qemu-alpine-ssh — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/qemu-alpine-ssh/tests/test.sh:8
```sh
curl -LsSf https://astral.sh/uv/0.9.5/install.sh | sh
```

## qemu-alpine-ssh — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/qemu-alpine-ssh/tests/test.sh:18
```sh
uvx \
  -p 3.13 \
  -w pytest==8.4.1 \
  -w pytest-json-ctrf==0.3.5 \
  pytest --ctrf /logs/verifier/ctrf.json /tests/test_outputs.py -rA
```

## qemu-startup — image-build
/mnt/20t/xubuqiang/datasets/terminal-bench/qemu-startup/environment/Dockerfile:5
```sh
RUN apt-get update && apt-get install -y \
    qemu-system-x86 \
    qemu-utils \
    wget \
    ca-certificates \
    openssh-client \
    && rm -rf /var/lib/apt/lists/*
```

## qemu-startup — image-build
/mnt/20t/xubuqiang/datasets/terminal-bench/qemu-startup/environment/Dockerfile:22
```sh
RUN apt update -y
```

## qemu-startup — image-build
/mnt/20t/xubuqiang/datasets/terminal-bench/qemu-startup/environment/Dockerfile:23
```sh
RUN apt install -y telnet netcat expect tmux asciinema
```

## qemu-startup — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/qemu-startup/tests/test.sh:4
```sh
apt-get update
```

## qemu-startup — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/qemu-startup/tests/test.sh:5
```sh
apt-get install -y curl expect
```

## qemu-startup — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/qemu-startup/tests/test.sh:8
```sh
curl -LsSf https://astral.sh/uv/0.9.5/install.sh | sh
```

## qemu-startup — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/qemu-startup/tests/test.sh:18
```sh
uvx \
  -p 3.13 \
  -w pytest==8.4.1 \
  -w pytest-json-ctrf==0.3.5 \
  pytest --ctrf /logs/verifier/ctrf.json /tests/test_outputs.py -rA
```

## query-optimize — image-build
/mnt/20t/xubuqiang/datasets/terminal-bench/query-optimize/environment/Dockerfile:6
```sh
RUN apt-get update && apt-get install -y curl
```

## query-optimize — image-build
/mnt/20t/xubuqiang/datasets/terminal-bench/query-optimize/environment/Dockerfile:8
```sh
RUN apt-get update && apt-get install -y sqlite3
```

## query-optimize — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/query-optimize/tests/test.sh:4
```sh
apt-get update
```

## query-optimize — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/query-optimize/tests/test.sh:5
```sh
apt-get install -y curl
```

## query-optimize — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/query-optimize/tests/test.sh:8
```sh
curl -LsSf https://astral.sh/uv/0.9.5/install.sh | sh
```

## query-optimize — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/query-optimize/tests/test.sh:18
```sh
uvx \
  -p 3.13 \
  -w pytest==8.4.1 \
  -w pytest-json-ctrf==0.3.5 \
  pytest --ctrf /logs/verifier/ctrf.json /tests/test_outputs.py -rA
```

## raman-fitting — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/raman-fitting/tests/test.sh:4
```sh
apt-get update
```

## raman-fitting — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/raman-fitting/tests/test.sh:5
```sh
apt-get install -y curl
```

## raman-fitting — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/raman-fitting/tests/test.sh:8
```sh
curl -LsSf https://astral.sh/uv/0.9.5/install.sh | sh
```

## raman-fitting — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/raman-fitting/tests/test.sh:18
```sh
uvx \
  -p 3.13 \
  -w pytest==8.4.1 \
  -w pytest-json-ctrf==0.3.5 \
  pytest --ctrf /logs/verifier/ctrf.json /tests/test_outputs.py -rA
```

## regex-chess — image-build
/mnt/20t/xubuqiang/datasets/terminal-bench/regex-chess/environment/Dockerfile:5
```sh
RUN pip install chess
```

## regex-chess — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/regex-chess/tests/test.sh:4
```sh
apt-get update
```

## regex-chess — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/regex-chess/tests/test.sh:5
```sh
apt-get install -y curl
```

## regex-chess — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/regex-chess/tests/test.sh:8
```sh
curl -LsSf https://astral.sh/uv/0.9.5/install.sh | sh
```

## regex-chess — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/regex-chess/tests/test.sh:18
```sh
uvx \
  -p 3.13 \
  -w pytest==8.4.1 \
  -w chess==1.11.2 \
  -w pytest-json-ctrf==0.3.5 \
  pytest --ctrf /logs/verifier/ctrf.json /tests/test_outputs.py -rA
```

## regex-log — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/regex-log/tests/test.sh:4
```sh
apt-get update
```

## regex-log — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/regex-log/tests/test.sh:5
```sh
apt-get install -y curl
```

## regex-log — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/regex-log/tests/test.sh:8
```sh
curl -LsSf https://astral.sh/uv/0.9.5/install.sh | sh
```

## regex-log — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/regex-log/tests/test.sh:18
```sh
uvx \
  -p 3.13 \
  -w pytest==8.4.1 \
  -w pytest-json-ctrf==0.3.5 \
  pytest --ctrf /logs/verifier/ctrf.json /tests/test_outputs.py -rA
```

## reshard-c4-data — image-build
/mnt/20t/xubuqiang/datasets/terminal-bench/reshard-c4-data/environment/Dockerfile:6
```sh
COPY --from=ghcr.io/astral-sh/uv:0.8.15 /uv /uvx /bin/
```

## reshard-c4-data — image-build
/mnt/20t/xubuqiang/datasets/terminal-bench/reshard-c4-data/environment/Dockerfile:9
```sh
RUN uv run setup.py
```

## reshard-c4-data — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/reshard-c4-data/tests/test.sh:9
```sh
uvx \
  -p 3.13 \
  -w pytest==8.4.1 \
  -w datasets==3.6.0 \
  -w tqdm==4.67.1 \
  -w pytest-json-ctrf==0.3.5 \
  pytest --ctrf /logs/verifier/ctrf.json /tests/test_outputs.py -rA
```

## reshard-c4-data — other-source
/mnt/20t/xubuqiang/datasets/terminal-bench/reshard-c4-data/tests/test_outputs.py:95
```sh
    print("Installing dependencies with uv sync...")
```

## reshard-c4-data — other-source
/mnt/20t/xubuqiang/datasets/terminal-bench/reshard-c4-data/tests/test_outputs.py:96
```sh
    sync_result = subprocess.run(["uv", "sync"], capture_output=True, text=True)
```

## reshard-c4-data — other-source
/mnt/20t/xubuqiang/datasets/terminal-bench/reshard-c4-data/tests/test_outputs.py:98
```sh
        print(f"uv sync failed: {sync_result.stderr}")
```

## reshard-c4-data — other-source
/mnt/20t/xubuqiang/datasets/terminal-bench/reshard-c4-data/tests/test_outputs.py:107
```sh
            ["uv", "run", COMPRESS_SCRIPT, TEST_INPUT_DIR, TEST_OUTPUT_DIR],
```

## reshard-c4-data — other-source
/mnt/20t/xubuqiang/datasets/terminal-bench/reshard-c4-data/tests/test_outputs.py:150
```sh
            ["uv", "run", DECOMPRESS_SCRIPT, TEST_OUTPUT_DIR],
```

## rstan-to-pystan — image-build
/mnt/20t/xubuqiang/datasets/terminal-bench/rstan-to-pystan/environment/Dockerfile:4
```sh
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        python3 \
        python3-pip \
        sudo && \
    rm -rf /var/lib/apt/lists/*
```

## rstan-to-pystan — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/rstan-to-pystan/tests/test.sh:4
```sh
apt-get update
```

## rstan-to-pystan — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/rstan-to-pystan/tests/test.sh:5
```sh
apt-get install -y curl
```

## rstan-to-pystan — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/rstan-to-pystan/tests/test.sh:8
```sh
curl -LsSf https://astral.sh/uv/0.9.5/install.sh | sh
```

## rstan-to-pystan — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/rstan-to-pystan/tests/test.sh:18
```sh
uvx \
  -p 3.13 \
  -w pytest==8.4.1 \
  -w pytest-json-ctrf==0.3.5 \
  pytest --ctrf /logs/verifier/ctrf.json test_outputs.py -rA
```

## sam-cell-seg — image-build
/mnt/20t/xubuqiang/datasets/terminal-bench/sam-cell-seg/environment/Dockerfile:7
```sh
RUN apt-get update && \
      apt-get install -y git  tmux asciinema && \
      rm -rf /var/lib/apt/lists/*
```

## sam-cell-seg — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/sam-cell-seg/tests/test.sh:4
```sh
apt-get update
```

## sam-cell-seg — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/sam-cell-seg/tests/test.sh:5
```sh
apt-get install -y curl git libgl1
```

## sam-cell-seg — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/sam-cell-seg/tests/test.sh:8
```sh
curl -LsSf https://astral.sh/uv/0.9.5/install.sh | sh
```

## sam-cell-seg — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/sam-cell-seg/tests/test.sh:29
```sh
uvx \
  --index https://download.pytorch.org/whl/cpu \
  --index-strategy unsafe-best-match \
  -p 3.11 \
  -w torch==2.5.1 \
  -w torchvision==0.20.1 \
  -w pandas==2.3.2 \
  -w timm==1.0.19 \
  -w opencv-python==4.12.0.88 \
  -w shapely==2.1.1 \
  -w pytest==8.4.1 \
  -w pytest-json-ctrf==0.3.5 \
  -w git+https://github.com/ChaoningZhang/MobileSAM.git@${COMMIT_HASH} \
  pytest --ctrf /logs/verifier/ctrf.json /tests/test_outputs.py -rA
```

## sanitize-git-repo — image-build
/mnt/20t/xubuqiang/datasets/terminal-bench/sanitize-git-repo/environment/Dockerfile:5
```sh
RUN apt-get update && apt-get install -y git
```

## sanitize-git-repo — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/sanitize-git-repo/tests/test.sh:4
```sh
apt-get update
```

## sanitize-git-repo — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/sanitize-git-repo/tests/test.sh:5
```sh
apt-get install -y curl
```

## sanitize-git-repo — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/sanitize-git-repo/tests/test.sh:8
```sh
curl -LsSf https://astral.sh/uv/0.9.5/install.sh | sh
```

## sanitize-git-repo — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/sanitize-git-repo/tests/test.sh:18
```sh
uvx \
  -p 3.13 \
  -w pytest==8.4.1 \
  -w gitpython==3.1.44 \
  -w pytest-json-ctrf==0.3.5 \
  pytest --ctrf /logs/verifier/ctrf.json /tests/test_outputs.py -rA
```

## schemelike-metacircular-eval — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/schemelike-metacircular-eval/tests/test.sh:4
```sh
apt-get update
```

## schemelike-metacircular-eval — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/schemelike-metacircular-eval/tests/test.sh:5
```sh
apt-get install -y curl
```

## schemelike-metacircular-eval — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/schemelike-metacircular-eval/tests/test.sh:8
```sh
curl -LsSf https://astral.sh/uv/0.9.5/install.sh | sh
```

## schemelike-metacircular-eval — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/schemelike-metacircular-eval/tests/test.sh:18
```sh
uvx \
  -p 3.13 \
  -w pytest==8.4.1 \
  -w pytest-json-ctrf==0.3.5 \
  pytest --ctrf /logs/verifier/ctrf.json /tests/test_outputs.py -rA
```

## sparql-university — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/sparql-university/tests/test.sh:4
```sh
apt-get update
```

## sparql-university — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/sparql-university/tests/test.sh:5
```sh
apt-get install -y curl
```

## sparql-university — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/sparql-university/tests/test.sh:8
```sh
curl -LsSf https://astral.sh/uv/0.9.5/install.sh | sh
```

## sparql-university — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/sparql-university/tests/test.sh:18
```sh
uvx \
  -p 3.13 \
  -w pytest==8.4.1 \
  -w rdflib==7.1.4 \
  -w pytest-json-ctrf==0.3.5 \
  pytest --ctrf /logs/verifier/ctrf.json /tests/test_outputs.py -rA
```

## sqlite-db-truncate — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/sqlite-db-truncate/tests/test.sh:4
```sh
apt-get update
```

## sqlite-db-truncate — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/sqlite-db-truncate/tests/test.sh:5
```sh
apt-get install -y curl
```

## sqlite-db-truncate — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/sqlite-db-truncate/tests/test.sh:8
```sh
curl -LsSf https://astral.sh/uv/0.9.5/install.sh | sh
```

## sqlite-db-truncate — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/sqlite-db-truncate/tests/test.sh:18
```sh
uvx \
  -p 3.13 \
  -w pytest==8.4.1 \
  -w pytest-json-ctrf==0.3.5 \
  pytest --ctrf /logs/verifier/ctrf.json /tests/test_outputs.py -rA
```

## sqlite-with-gcov — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/sqlite-with-gcov/tests/test.sh:4
```sh
apt-get update
```

## sqlite-with-gcov — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/sqlite-with-gcov/tests/test.sh:5
```sh
apt-get install -y curl
```

## sqlite-with-gcov — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/sqlite-with-gcov/tests/test.sh:8
```sh
curl -LsSf https://astral.sh/uv/0.9.5/install.sh | sh
```

## sqlite-with-gcov — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/sqlite-with-gcov/tests/test.sh:18
```sh
uvx \
  -p 3.13 \
  -w pytest==8.4.1 \
  -w pytest-json-ctrf==0.3.5 \
  pytest --ctrf /logs/verifier/ctrf.json /tests/test_outputs.py -rA
```

## torch-pipeline-parallelism — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/torch-pipeline-parallelism/tests/test.sh:4
```sh
apt-get update
```

## torch-pipeline-parallelism — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/torch-pipeline-parallelism/tests/test.sh:5
```sh
apt-get install -y curl
```

## torch-pipeline-parallelism — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/torch-pipeline-parallelism/tests/test.sh:8
```sh
curl -LsSf https://astral.sh/uv/0.9.5/install.sh | sh
```

## torch-pipeline-parallelism — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/torch-pipeline-parallelism/tests/test.sh:18
```sh
uvx \
  -p 3.13 \
  -w pytest==8.4.1 \
  -w torch==2.7.0 \
  -w transformers==4.55.0 \
  -w pytest-json-ctrf==0.3.5 \
  pytest --ctrf /logs/verifier/ctrf.json /tests/test_outputs.py -rA
```

## torch-tensor-parallelism — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/torch-tensor-parallelism/tests/test.sh:4
```sh
apt-get update
```

## torch-tensor-parallelism — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/torch-tensor-parallelism/tests/test.sh:5
```sh
apt-get install -y curl
```

## torch-tensor-parallelism — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/torch-tensor-parallelism/tests/test.sh:8
```sh
curl -LsSf https://astral.sh/uv/0.9.5/install.sh | sh
```

## torch-tensor-parallelism — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/torch-tensor-parallelism/tests/test.sh:18
```sh
uvx \
  -p 3.13 \
  -w pytest==8.4.1 \
  -w torch==2.7.0 \
  -w pytest-json-ctrf==0.3.5 \
  pytest --ctrf /logs/verifier/ctrf.json /tests/test_outputs.py -rA
```

## train-fasttext — image-build
/mnt/20t/xubuqiang/datasets/terminal-bench/train-fasttext/environment/Dockerfile:5
```sh
RUN apt-get update && apt-get install -y wget
```

## train-fasttext — image-build
/mnt/20t/xubuqiang/datasets/terminal-bench/train-fasttext/environment/Dockerfile:12
```sh
RUN pip install pandas==2.3.0 pyarrow==20.0.0
```

## train-fasttext — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/train-fasttext/tests/test.sh:4
```sh
apt-get update
```

## train-fasttext — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/train-fasttext/tests/test.sh:5
```sh
apt-get install -y curl
```

## train-fasttext — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/train-fasttext/tests/test.sh:8
```sh
curl -LsSf https://astral.sh/uv/0.9.5/install.sh | sh
```

## train-fasttext — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/train-fasttext/tests/test.sh:20
```sh
uvx \
  -p 3.11 \
  -w pytest==8.4.1 \
  -w scikit-learn==1.7.0 \
  -w fasttext-wheel==0.9.2 \
  -w numpy==1.24.0 \
  -w pytest-json-ctrf==0.3.5 \
  pytest --ctrf /logs/verifier/ctrf.json /tests/test_outputs.py -rA
```

## tune-mjcf — image-build
/mnt/20t/xubuqiang/datasets/terminal-bench/tune-mjcf/environment/Dockerfile:5
```sh
RUN pip install --no-cache-dir mujoco==3.3.5
```

## tune-mjcf — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/tune-mjcf/tests/test.sh:4
```sh
apt-get update
```

## tune-mjcf — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/tune-mjcf/tests/test.sh:5
```sh
apt-get install -y curl
```

## tune-mjcf — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/tune-mjcf/tests/test.sh:8
```sh
curl -LsSf https://astral.sh/uv/0.9.5/install.sh | sh
```

## tune-mjcf — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/tune-mjcf/tests/test.sh:18
```sh
uvx \
  -p 3.13 \
  -w pytest==8.4.1 \
  -w mujoco==3.3.5 \
  -w pytest-json-ctrf==0.3.5 \
  pytest --ctrf /logs/verifier/ctrf.json /tests/test_outputs.py -rA
```

## video-processing — image-build
/mnt/20t/xubuqiang/datasets/terminal-bench/video-processing/environment/Dockerfile:6
```sh
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*
```

## video-processing — image-build
/mnt/20t/xubuqiang/datasets/terminal-bench/video-processing/environment/Dockerfile:16
```sh
RUN pip install "opencv-contrib-python>=4.11.0.86"
```

## video-processing — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/video-processing/tests/test.sh:4
```sh
apt-get update
```

## video-processing — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/video-processing/tests/test.sh:5
```sh
apt-get install -y curl
```

## video-processing — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/video-processing/tests/test.sh:8
```sh
curl -LsSf https://astral.sh/uv/0.9.5/install.sh | sh
```

## video-processing — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/video-processing/tests/test.sh:18
```sh
uvx \
  -p 3.13 \
  -w pytest==8.4.1 \
  -w toml==0.10.2 \
  -w opencv-contrib-python==4.11.0.86 \
  -w pytest-json-ctrf==0.3.5 \
  pytest --ctrf /logs/verifier/ctrf.json /tests/test_outputs.py -rA
```

## vulnerable-secret — image-build
/mnt/20t/xubuqiang/datasets/terminal-bench/vulnerable-secret/environment/Dockerfile:6
```sh
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*
```

## vulnerable-secret — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/vulnerable-secret/tests/test.sh:7
```sh
apt-get update
```

## vulnerable-secret — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/vulnerable-secret/tests/test.sh:8
```sh
apt-get install -y curl
```

## vulnerable-secret — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/vulnerable-secret/tests/test.sh:11
```sh
curl -LsSf https://astral.sh/uv/0.9.5/install.sh | sh
```

## vulnerable-secret — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/vulnerable-secret/tests/test.sh:21
```sh
uvx \
  -p 3.13 \
  -w pytest==8.4.1 \
  -w pytest-json-ctrf==0.3.5 \
  pytest --ctrf /logs/verifier/ctrf.json /tests/test_outputs.py -rA
```

## winning-avg-corewars — image-build
/mnt/20t/xubuqiang/datasets/terminal-bench/winning-avg-corewars/environment/Dockerfile:5
```sh
RUN apt-get update && apt-get install -y \
    tmux \
    asciinema \
    build-essential \
    libncurses-dev \
    ca-certificates \
    dpkg-dev \
    devscripts
```

## winning-avg-corewars — image-build
/mnt/20t/xubuqiang/datasets/terminal-bench/winning-avg-corewars/environment/Dockerfile:15
```sh
RUN echo 'deb-src http://deb.debian.org/debian stable main' >> /etc/apt/sources.list.d/deb-src.list
```

## winning-avg-corewars — image-build
/mnt/20t/xubuqiang/datasets/terminal-bench/winning-avg-corewars/environment/Dockerfile:16
```sh
RUN apt-get update
```

## winning-avg-corewars — image-build
/mnt/20t/xubuqiang/datasets/terminal-bench/winning-avg-corewars/environment/Dockerfile:21
```sh
RUN apt-get source pmars && \
    cd /app/pmars-*/src && \
    sed -i 's/-DXWINGRAPHX//g' Makefile && \
    sed -i 's/^LIB *=.*/LIB = -lncurses/' Makefile && \
    make clean && make && \
    install -m 0755 pmars /usr/local/bin/pmars
```

## winning-avg-corewars — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/winning-avg-corewars/tests/test.sh:4
```sh
apt-get update
```

## winning-avg-corewars — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/winning-avg-corewars/tests/test.sh:5
```sh
apt-get install -y curl
```

## winning-avg-corewars — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/winning-avg-corewars/tests/test.sh:8
```sh
curl -LsSf https://astral.sh/uv/0.9.5/install.sh | sh
```

## winning-avg-corewars — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/winning-avg-corewars/tests/test.sh:18
```sh
uvx \
  -p 3.13 \
  -w pytest==8.4.1 \
  -w pytest-json-ctrf==0.3.5 \
  pytest --ctrf /logs/verifier/ctrf.json /tests/test_outputs.py -rA
```

## write-compressor — image-build
/mnt/20t/xubuqiang/datasets/terminal-bench/write-compressor/environment/Dockerfile:5
```sh
RUN apt-get update && apt-get install -y gcc rustc bc
```

## write-compressor — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/write-compressor/tests/test.sh:4
```sh
apt-get update
```

## write-compressor — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/write-compressor/tests/test.sh:5
```sh
apt-get install -y curl
```

## write-compressor — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/write-compressor/tests/test.sh:8
```sh
curl -LsSf https://astral.sh/uv/0.9.5/install.sh | sh
```

## write-compressor — verifier-bootstrap
/mnt/20t/xubuqiang/datasets/terminal-bench/write-compressor/tests/test.sh:18
```sh
uvx \
  -p 3.13 \
  -w pytest==8.4.1 \
  -w pytest-json-ctrf==0.3.5 \
  pytest --ctrf /logs/verifier/ctrf.json /tests/test_outputs.py -rA
```
