#!/bin/bash

# NOTE: current directory is `./sdk/build`

echo "Exporting Python SDK at ${export_dir}..."

project_name=${PROJECT_NAME}
package_name=$(echo ${project_name}-py | sed -r 's/-/_/g')
export_dir=${BUILD_DIR}/${package_name}
mkdir -p $export_dir

# export dependency shared library.
#   TODO: consider a more elegant way, like packaging
libtorch_lib_dir=${LIBTORCH_DIR}/lib
cp -r ${USR_LIB_DIR} $export_dir/
cp -r ${libtorch_lib_dir} $export_dir/
echo "User lib size: $(du -sh $USR_LIB_DIR)"
echo "libtorch lib size: $(du -sh $libtorch_lib_dir)"
echo "Total exported lib size: $(du -sh $export_dir/lib)"

# export sdk shared library
sdk_so=$(ls ${BUILD_DIR}/${project_name}/trajectory_tracker/trajectory_tracker_*.so|head -n 1)
cp $sdk_so $export_dir/
pushd $export_dir/
  ln -sf $(basename $sdk_so) export_symbols.so
popd

# export assets
cp -r ${CHECKPOINT_DIR} $export_dir/
cp -r assets/exported-python-sdk/* $export_dir/
cp -r /proto/proto_gen_py $export_dir/

# package into tarball
# TODO: move to a more formal packaging way
pushd ${BUILD_DIR}
  tar -czf ./${package_name}.tar.gz ${package_name}/
  echo "library packed: ${package_name}.tar.gz"
popd
