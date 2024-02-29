# DRLTT SDK

Software Development Kit (SDK) for deploying DRLTT into real-time system, CPU-only and runtime efficient.

## Compilation

This project employs `cmake` as build system.. The compilation is recommended to be done within a Docker container.

### Build Docker image

Firstly, build an image named `drltt-sdk` for compilation with the provided Dockerfile.

```bash
docker image build --tag drltt-sdk:dev - < ./Dockerfile
```

### Compile source within Docker container

Secondly, launch compilation by running `bash ./compile-in-docker.sh`.

.. literalinclude:: ../../../sdk/compile-in-docker.sh
  :language: bash

Inside the container, it will first compile the Protobuf (this is important for Protobuf to be included successfully) and then compile source files.

.. literalinclude:: ../../../sdk/compile-source.sh
  :language: bash


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

```text
/build
├── ...
├── proto_def
├── drltt-sdk   # compiled libraries and executables
│   └── main
├── lib         # exported shared library for running
└── ...
```

### Run compiled binaries

To run sample script, launch `bash run-main.sh`:

.. literalinclude:: ../../../sdk/run-main.sh
  :language: bash

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
