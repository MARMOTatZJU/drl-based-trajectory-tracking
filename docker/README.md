# Docker

DRLTT uses docker for SDK compiling, CI/CD, and more.

Currently supported docker images and their hierarchical relationship:

```text
`drltt`
├── `drltt:cicd`        # Docker image for setting up CI/CD
└── `drltt:runtime`     # Docker image for run DRLTT, i.e. training/testing/sdk compilation/etc.
```

## `drltt:cicd`: Build DRLTT CI/CD Docker Image

```bash
docker image build --tag drltt:cicd - < ./Dockerfile.cicd
```

## `drltt:runtime`: Build DRLTT Runtime Docker Image

```bash
docker image build --tag drltt:runtime - < ./Dockerfile.runtime
```

## Useful Tips

### Tips 1: Networking Issue

For network environments within Mainland China, you may consider using a domestic pip source to accelerate this process and setting the timeout to a larger value:

```bash
docker image build --tag drltt:runtime --build-arg PIP_ARGS=" -i https://pypi.tuna.tsinghua.edu.cn/simple --timeout 1000 " - < ./Dockerfile.runtime
```

For APT source, you may consider using a domestic apt source to accelerate this process by appending the following part to the `./Dockerfile`:

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

### Tip 2: Retrying the image building command

```bash
ret_val=1;while [ -z "${ret_val}" ] || [ 0 -ne $ret_val ]; do ret_val=$(docker image build --tag drltt:runtime --build-arg PIP_ARGS=" -i https://pypi.tuna.tsinghua.edu.cn/simple --timeout 1000 " - < ./Dockerfile.runtime); done
```

### Tip 3: Transferring Docker images

To save time by transferring the Docker images, save with the command:

```bash
docker image save drltt:runtime -o ./drltt.runtime.image
```

, and load with the command:

```bash
docker image load -i ./drltt.runtime.image
```

### Tip 4: Clearing Cache

Tip: To remove unused images/cached, run:

```bash
docker system prune
```

### Tip 5: To debug with docker images

```bash
image_name=drltt:runtime
docker run --name ${image_name}-$((RANDOM%100000)) --entrypoint bash --rm --network=host -it ${image_name} -c bash
```
