#!/bin/bash

work_dir=./drltt-sdk

docker run --name drltt-sdk --entrypoint bash -e "ACCEPT_EULA=Y" --rm --network=host \
    -e "PRIVACY_CONSENT=Y" \
    -v $PWD:/${work_dir}:rw \
    -v $PWD/../common/proto/proto_def:/proto_src:rw \
    --user "$(id -u):$(id -g)" \
    drltt-sdk \
    -c "cd ${work_dir} && bash compile-proto-in-docker.sh && bash compile-source.sh"
