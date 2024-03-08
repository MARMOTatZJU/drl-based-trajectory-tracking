#!/bin/bash

# NOTE: current directory is `./sdk/build`

project_name=drltt-sdk
package_name=$(echo ${project_name}-py | sed -r 's/-/_/g')
export_dir=./build/${package_name}
mkdir -p $export_dir

ld_lib_dir=./build/lib
cp -r $ld_lib_dir $export_dir/

sdk_so=$(ls ./build/${project_name}/trajectory_tracker/trajectory_tracker_*.so|head -n 1)
cp $sdk_so $export_dir/
pushd $export_dir/
  ln -sf $(basename $sdk_so) export_symbols.so
popd

checkpoint_dir=/drltt-work_dir/track-test/checkpoint
cp -r $checkpoint_dir $export_dir/

cp -r assets/standalone/* $export_dir/
cp -r /proto/proto_gen_py $export_dir/

# TODO: move to a more formal packaging way
pushd ./build
  tar -czf ./${package_name}.tar.gz ${package_name}/
  echo "library packed: ${package_name}.tar.gz"
popd
