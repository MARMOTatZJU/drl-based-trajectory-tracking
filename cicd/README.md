# DRLTT CI/CD

DRLTT uses [gitlab-cicd](https://docs.gitlab.com/ee/ci/pipelines/) to build CI/CD.

## Build Docker image for CI/CD

### Build Docker Image for GitLab Runner

```bash
docker image build --tag drltt-cicd:runner - < ./Dockerfile.runner
```

### Build Docker Image for GitLab Executor

```bash
docker image build --tag drltt-cicd:executor - < ./Dockerfile.executor
```

Tip: For network environments within Mainland China, you may consider using a domestic pip source to accelerate this process:

```bash
docker image build --tag drltt-cicd:executor --build-arg PIP_SRC_ARG=" -i https://pypi.tuna.tsinghua.edu.cn/simple " - < ./Dockerfile.executor
```

## Set-up runner

Go to `https://${GITLAB_URL}/${USER}/${REPO_NAME}/-/runners/new`, create a new runner (select `Linux`/`Run untagged jobs`), and copy the runner token ${RUNNER_TOKEN}.

On the runner machine, run `start-gitlab-runner.sh`, and pass the runner token to it.

```bash
./start-gitlab-runner.sh ${RUNNER_TOKEN}
```

Cleanup: To stop and clear all runners, run `stop-all-gitlab-runners.sh`.

```bash
./stop-all-gitlab-runners.sh
```

## Configure Pipelines/Jobs/etc.

See `.gitlab-ci.yml` for details.

## Check CI/CD results

Go to  `https://${GITLAB_URL}/${USER}/${REPO_NAME}/-/pipelines` to see the CI/CD and check out artifacts (generated files).
