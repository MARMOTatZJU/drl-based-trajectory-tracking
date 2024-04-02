#!/bin/bash

project_name=drltt-sdk
image_name=${project_name}:dev

repo_root_dir=$(git rev-parse --show-toplevel)
repo_dirname=$(basename $repo_root_dir)
sdk_root_dir=$(dirname $0)
build_dir=${sdk_dir}/build

docker_repo_root_dir=/${repo_dirname}
docker_repo_work_dir=${docker_repo_root_dir}/work_dir
docker_checkpoint_dir=${docker_repo_work_dir}/track-test/checkpoint
docker_sdk_root_dir=${docker_repo_root_dir}/sdk  # TODO remove hardcode, use relative path
docker_proto_gen_dir=${docker_sdk_root_dir}/proto_gen
docker_build_dir=${docker_sdk_root_dir}/build

docker_usr_lib_dir=/usr/local/lib

if [[ -v HOST_LIBTORCH_DIR ]];then
    docker_libtorch_dir=/libtorch-host
    mount_host_libtorch_in_docker="-v ${HOST_LIBTORCH_DIR}:${docker_libtorch_dir}:ro"
    echo "Using libtorch mounted from host: ${HOST_LIBTORCH_DIR}"
else
    docker_libtorch_dir=/libtorch
    mount_host_libtorch_in_docker=""
    echo "Using libtorch preinstalled in docker image"
fi

if [[ -v HOST_PYTORCH_DIR ]];then
    docker_pytorch_dir=/pytorch-host
    mount_pytorch_in_docker="-v $PYTORCH_DIR:/${docker_pytorch_dir}:rw"
else
    docker_pytorch_dir=/pytorch
    mount_pytorch_in_docker=""
fi

# TODO: reorganize mouted path

nonsudo_user_arg=" --user $(id -u):$(id -g) "
nonsudo_user_source_cmd=" source /work_dir/.bashrc "

if [[ $1 == "interactive" ]]; then
    docker_arg_suffix=" -it ${image_name} "
    docker_container_cmd=" bash "
    if [[ $2 == "nonsudo" ]]; then
        docker_arg_suffix="${nonsudo_user_arg} ${docker_arg_suffix}"
        docker_container_cmd=" ${nonsudo_user_source_cmd} && bash "
    fi
else
    docker_arg_suffix="${nonsudo_user_arg} ${image_name} "
    docker_container_cmd=" ${nonsudo_user_source_cmd} && cd ${docker_sdk_root_dir} && bash ./compile-source.sh"
    if [[ ! $1 == "test" ]]; then
        docker_container_cmd="${docker_container_cmd} && bash ./export-py-sdk.sh"
    fi
fi

docker run --name drltt-sdk --entrypoint bash -e "ACCEPT_EULA=Y" --rm --network=host \
    -e "PRIVACY_CONSENT=Y" \
    -e "REPO_ROOT_DIR=${docker_repo_root_dir}" \
    -e "PROJECT_NAME=${project_name}" \
    -e "BUILD_DIR=${docker_build_dir}" \
    -e "PROTO_GEN_DIR=${docker_proto_gen_dir}" \
    -e "CHECKPOINT_DIR=${docker_checkpoint_dir}" \
    -e "USR_LIB_DIR=${docker_usr_lib_dir}" \
    -e "LIBTORCH_DIR=${docker_libtorch_dir}" \
    -e "PYTORCH_DIR=${docker_pytorch_dir}" \
    -v ${repo_root_dir}:${docker_repo_root_dir}:rw \
    ${mount_pytorch_in_docker} \
    ${mount_host_libtorch_in_docker} \
    ${docker_arg_suffix} \
    -c "${docker_container_cmd}"
