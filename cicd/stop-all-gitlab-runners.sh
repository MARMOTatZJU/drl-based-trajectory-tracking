#!/bin/bash

docker container stop $(docker container ls -q --filter name=drltt-cicd*)
