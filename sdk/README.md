# DRLTT SDK

Software Development Kit (SDK) for deploying DRLTT into real-time system, CPU-only and runtime efficient.

## Compilation

The compilation is recomended to be done within a Docker container.

Firstly, build an image named `drltt-sdk` for compilation with the provided Dockerfile.

```
docker image build --tag drltt-sdk - < ./Dockerfile
```

Secondly, launch compilation by running `sdk/compile-in-docker.sh`. Inside the container, it will first compile the Protobuf (this is important for Protobuf to be included successfully) and then compile source files with cmake as build system.

```bash
bash ./compile-in-docker.sh
```

## Development

### Code format

This project uses `clang-format` to format CXX code.

```
clang-format -style=llvm -dump-config > .clang-format
find . -regex '.*\.\(cpp\|hpp\|cu\|cuh\|c\|h\)' -exec clang-format --style=file -i {} \;
```

References:

- https://clang.llvm.org/get_started.html
- https://www.kernel.org/doc/html/next/process/clang-format.html
- https://leimao.github.io/blog/Clang-Format-Quick-Tutorial/
