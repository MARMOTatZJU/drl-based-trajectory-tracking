#!/bin/bash

build_dir=./build
project_name=drltt-sdk
image_name=${project_name}:dev

docker_source_dir=/${project_name}
docker_repo_work_dir=/drltt-work_dir
docker_checkpoint_dir=${docker_repo_work_dir}/track-test/checkpoint


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
    -e "SOURCE_DIR=${docker_source_dir}" \
    -e "REPO_WORK_DIR=${docker_repo_work_dir}" \
    -e "CHECKPOINT_DIR=${docker_checkpoint_dir}" \
    -e "PROJECT_NAME=${project_name}" \
    -v $PWD:/${docker_source_dir}:rw \
    -v $PWD/../common/proto:/proto:rw \
    -v $PWD/../work_dir:${docker_repo_work_dir}:ro \
    ${mount_host_libtorch_in_docker} \
    --user "$(id -u):$(id -g)" \
    ${image_name} \
    -c "cd ${docker_source_dir} && bash ./compile-source.sh && bash ./export-py-sdk.sh"
