# DRLTT TEST

## DRLTT Python Test

Python testing is done with *pytest*. To launch the Python testing, run `./test/test-python.sh`:

.. literalinclude:: ../../../test/test-python.sh
  :language: bash

## DRLTT CPP Test

CPP testing is performed through *gtest* immediately after building. To launch the CPP testing, run `./test/test-cpp.sh`:

.. literalinclude:: ../../../test/test-cpp.sh
  :language: bash

Please refer to *DRTLL SDK* for details.

#### Accelerating CPP testing

To skip SDK exporting (e.g. while debugging the test running), run:

```bash
./test-cpp.sh test
```

To skip both SDK exporting and checkpoint generation (e.g. while debugging the test building), run:

```bash
./test-cpp.sh test reuse-checkpoint
```

To use a sample config with a shorter time for test data generation (a dummy training), run:

```bash
./test-cpp.sh fast test
```

TODO: refactor argument parsing logic in test scripts.

## DRLTT Documentation Test

To test the Documentation, run `./test/test-doc.sh`:
