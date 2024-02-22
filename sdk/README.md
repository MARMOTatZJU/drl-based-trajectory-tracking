

## Compilation


```
docker image build --tag drltt-sdk - < ./Dockerfile
```


Run docker container

```
#!/bin/bash
docker run --name drltt-sdk --entrypoint bash -it -e "ACCEPT_EULA=Y" --rm --network=host \
    -e "PRIVACY_CONSENT=Y" \
    -v $PWD:/drltt-sdk:rw \
    drltt-sdk
```

