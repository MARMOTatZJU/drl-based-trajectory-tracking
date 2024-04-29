#!/bin/bash

runner_image_name="drltt:cicd"
executor_image_name="drltt:runtime"

token=$1

if [[ -z ${token} ]];then
  echo "No gitlab runner token provided."
  exit 1
fi

register_cmd="gitlab-runner register \
--non-interactive \
--url https://git.sjtu.edu.cn \
--token ${token} \
--executor docker \
--docker-image "${executor_image_name}" \
--docker-pull-policy if-not-present \
--name test-runner \
"

docker_container_cmd="(
    ${register_cmd};
    gitlab-runner start;
    sleep infinity;
)"

docker_arg_suffix=${runner_image_name}

docker_container_name=drltt-cicd-$(date +%s)
docker run --name ${docker_container_name} --entrypoint bash -e "ACCEPT_EULA=Y" --rm --network=host \
  -v /var/run/docker.sock:/var/run/docker.sock \
  ${docker_arg_suffix} \
  -c "${docker_container_cmd}"
