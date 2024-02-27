#!/bin/bash

work_dir=/drltt-sdk
image_name=drltt-sdk:dev

docker run --name drltt-sdk --entrypoint bash -e "ACCEPT_EULA=Y" --rm --network=host \
    -e "PRIVACY_CONSENT=Y" \
    -v $PWD:/${work_dir}:rw \
    -v $PWD/../common/proto:/proto:rw \
    --user "$(id -u):$(id -g)" \
    ${image_name} \
    -c "cd ${work_dir} && bash compile-source.sh"
