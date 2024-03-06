#!/bin/bash

source_dir=/drltt-sdk
image_name=drltt-sdk:dev

if [[ -z ${HOST_LIBTORCH_PATH} ]];then
    mount_host_libtorch_in_docker=""
    echo "Using libtorch preinstalled in docker image"
else
    mount_host_libtorch_in_docker="-v ${HOST_LIBTORCH_PATH}:/libtorch-host:ro"
    echo "Using libtorch mounted from host: ${HOST_LIBTORCH_PATH}"
fi

# TODO: reorganize mouted path

docker run --name drltt-sdk --entrypoint bash -e "ACCEPT_EULA=Y" --rm --network=host \
    -e "PRIVACY_CONSENT=Y" \
    -v $PWD:/${source_dir}:rw \
    -v $PWD/../common/proto:/proto:rw \
    -v $PWD/../work_dir:/drltt-work_dir:ro \
    ${mount_host_libtorch_in_docker} \
    --user "$(id -u):$(id -g)" \
    ${image_name} \
    -c "cd ${source_dir} && bash ./compile-source.sh"
