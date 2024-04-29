#!/bin/bash
source setup.sh

pushd docs
  rm -rf build
  make html SPHINXOPTS="-W"
  make_sphinx_ret_val=$?
  if [ $make_sphinx_ret_val -eq 0 ];then
    echo "Built the Sphinx documentation successfully."
  else
    echo "Sphinx documentation building failed!!!"
  fi
popd

exit $make_sphinx_ret_val
