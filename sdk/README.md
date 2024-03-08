# DRLTT SDK

Software Development Kit (SDK) for deploying DRLTT into real-time system, CPU-only and runtime efficient.

## Compilation

This project employs `cmake` as build system.. The compilation is recommended to be done within a Docker container.

### Build Docker image

Firstly, build an image named `drltt-sdk` for compilation with the provided Dockerfile.

```bash
docker image build --tag drltt-sdk:dev - < ./Dockerfile
```

Tip: To remove unused images/cached, run:

```bash
docker system prune
```

Tip 2: To save docker image for transferring and save time:

```
docker image save drltt-sdk:dev -o ./drltt-sdk.image
```


Tip 3: For network environments within Mainland China, you may consider using a domestic apt source to accelerate this process by appending the following part to the `./Dockerfile`:


```dockerfile
# Example using TUNA apt source
ARG APT_SOURCE_LIST=/etc/apt/sources.list
RUN \
    mv ${APT_SOURCE_LIST} ${APT_SOURCE_LIST}.bak && \
    touch ${APT_SOURCE_LIST} && \
    printf "deb https://mirrors.tuna.tsinghua.edu.cn/ubuntu/ jammy main restricted universe multiverse" >> ${APT_SOURCE_LIST} && \
    printf "deb https://mirrors.tuna.tsinghua.edu.cn/ubuntu/ jammy-updates main restricted universe multiverse" >> ${APT_SOURCE_LIST} && \
    printf "deb https://mirrors.tuna.tsinghua.edu.cn/ubuntu/ jammy-backports main restricted universe multiverse" >> ${APT_SOURCE_LIST} && \
    printf "deb http://security.ubuntu.com/ubuntu/ jammy-security main restricted universe multiverse" >> ${APT_SOURCE_LIST} && \
    cat ${APT_SOURCE_LIST}
```

### Compile source within Docker container

Secondly, launch compilation by running `bash ./compile-in-docker.sh`.

.. literalinclude:: ../../../sdk/compile-in-docker.sh
  :language: bash

Inside the container, it will first compile the Protobuf (this is important for Protobuf to be included successfully) and then compile source files.

.. literalinclude:: ../../../sdk/compile-source.sh
  :language: bash

#### Use libtorch on host

To use libtorch on host, please pass a environment variable `HOST_LIBTORCH_PATH` to `./compile-in-docker.sh`:

```
HOST_LIBTORCH_PATH=/path/to/libtorch/on/host ./compile-in-docker.sh
```

#### Tree structure within docker container

```text
/
├── usr
│   └── local
│       ├── bin
│       └── lib
├── proto -> $PROJECT_ROOT/common/proto:/proto      # protobuf source
├── drltt-sdk -> $PROJECT_ROOT/sdk/drltt-sdk        # `source_dir`
│   └── proto_gen                                   # generated protobuf
└── work_dir
```

#### `build` folder structure

Building results are exported to the `build` folder which has the following structure:


```text
/build
├── ...
├── proto_def
├── drltt-sdk   # compiled libraries and executables
│   └── main
├── lib         # exported shared library for running
└── ...
```

### Run sample program

TODO:

If you prefer to use shared libraries on your host machine, please *prepend* your shared libraries' path to `LD_LIBRARY_PATH`.

## Development

### Code format

This project uses `clang-format` to format CXX code according to *Google C/C++ Code Style settings*.

To launch code-format, run `bash format-code.sh`:

.. literalinclude:: ../../../sdk/format-code.sh
  :language: bash

To customize your own `clang-format` config file, run:

```bash
clang-format -style=llvm -dump-config > .clang-format
```


References:

- https://clang.llvm.org/get_started.html
- https://www.kernel.org/doc/html/next/process/clang-format.html
- https://leimao.github.io/blog/Clang-Format-Quick-Tutorial/
