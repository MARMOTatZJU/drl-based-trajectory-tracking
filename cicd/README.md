# DRLTT CI/CD

DRLTT uses [gitlab-cicd](https://docs.gitlab.com/ee/ci/pipelines/) to build CI/CD.

## Build Docker image for CI/CD

Build Docker images `drltt:cicd` and `drltt:runtime` following the instructions in [Docker instructions](../docker/README.md).

## Set-up runner

Go to `https://${GITLAB_URL}/${USER}/${REPO_NAME}/-/runners/new`, create a new runner (select `Linux`/`Run untagged jobs`), and copy the runner token ${RUNNER_TOKEN}.

On the runner machine, run `start-gitlab-runner.sh`, and pass the runner token to it.

```bash
./start-gitlab-runner.sh ${GITLAB_URL} ${RUNNER_TOKEN}
```

Cleanup: To stop and clear all runners, run `stop-all-gitlab-runners.sh`.

```bash
./stop-all-gitlab-runners.sh
```

## Configure Pipelines/Jobs/etc.

See `.gitlab-ci.yml` for details.

## Check CI/CD results

Go to  `https://${GITLAB_URL}/${USER}/${REPO_NAME}/-/pipelines` to see the CI/CD and check out artifacts (generated files).
