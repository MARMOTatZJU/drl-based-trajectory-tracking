# DRLTT SDK

Software Development Kit (SDK) for deploying *DRLTT* into a real-time system, CPU-only and runtime efficient.

## Interfaces

The Interface of C++ SDK: `sdk/drltt-sdk/trajectory_tracker/trajectory_tracker.h`

The Interface of Python SDK: `sdk/assets/exported-python-sdk/trajectory_tracker.py`

## Compilation

This project employs `cmake` as build system.. The compilation is recommended to be done within a Docker container.

### Build Docker Image

Firstly, build an image named `drltt-sdk` for compilation with the provided Dockerfile.

```bash
docker image build --tag drltt-sdk:dev - < ./Dockerfile
```

Tip: To remove unused images/cached, run:

```bash
docker system prune
```

Tip 2: To save the Docker image for transferring and save time:

```
docker image save drltt-sdk:dev -o ./drltt-sdk.image
```

```
docker image load -i ./drltt-sdk.image
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

#### Debugging the building process

`./compile-in-docker.sh` can be used to debug the building process. Pass `interaction` argument to enter the container instead of launching the building process directly.

```bash
./compile-in-docker.sh interactive
```

Furthermore, pass `nonsudo` argument to avoid entering SUDO account.

```bash
./compile-in-docker.sh interactive nonsudo
```


### Compile Source and Export SDK Shared Library within Docker Container

Secondly, launch compilation and exporting by running `./compile-in-docker.sh`.

.. literalinclude:: ../../../sdk/compile-in-docker.sh
  :language: bash

To use [LibTorch](https://pytorch.org/cppdocs/installing.html) on the host during the compilation phase, please pass an environment variable `HOST_LIBTORCH_PATH` to `./compile-in-docker.sh`:

```bash
HOST_LIBTORCH_PATH=/path/to/libtorch/on/host ./compile-in-docker.sh
```

#### Compiling and exporting inside the Docker container under `./sdk/build`

Inside the container, it will first compile the Protobuf (this is important for Protobuf to be included successfully) and then compile source files.

.. literalinclude:: ../../../sdk/compile-source.sh
  :language: bash

Secondly, an optional exporting step will export a standalone Python SDK library backed with the compiled C++ SDK, along with all shared dependent libraries.

.. literalinclude:: ../../../sdk/export-py-sdk.sh
  :language: bash

The standalone library is under `./sdk/build/drltt_sdk_py.tar.gz`. Currently, the library is for **Python 3.8** (version-specific as ABI changes across versions). TOOD: Support for multiple Python versions is coming soon.


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
├── drltt-sdk             # compiled libraries and executables
│   ├── common
│   ├── inference
│   ├── trajectory_tracker
│   └── trajectory_tracker
├── lib                   # exported shared library for running
├── drltt_sdk_py          # exported standalone python sdk library
├── drltt_sdk_py.tar.gz   # packed standalone python sdk library
└── ...
```

### Run sample program

TODO: An executable sample program is coming soon.

If you prefer to use shared libraries on your host machine, please *prepend* your shared libraries' path to `LD_LIBRARY_PATH`.

## Deployment

Unpackage the exported tarball and set `LD_LIBRARY_PATH` manually (effectively modifying it during runtime is not possible):

```bash
tar xvzf drltt_sdk_py.tar.gz -C ./
LD_LIBRARY_PATH=${LD_LIBRARY_PATH}:./drltt_sdk_py/lib
```

Reference: https://man7.org/linux/man-pages/man8/ld.so.8.html

Import `drltt_sdk_py`. As no depedency required except for `Python=3.8`, you can run the trajectory tracking directly:

```python
from drltt_sdk_py import TrajectoryTracker

tracker = TrajectoryTracker()
reference_line = [(0.1 * 5.0 * step_index, 0.1 * 4.0 * step_index) for step_index in range(60)]
tracked_states, tracked_actions = tracker.track_traference_line(reference_line)
```

To check the numeric precision, run the following test:

```bash
cd drltt_sdk_py && ./test.sh
```


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
