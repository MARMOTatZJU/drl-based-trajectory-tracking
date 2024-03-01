#!/bin/bash
source setup.sh

pushd docs
  make html
popd

