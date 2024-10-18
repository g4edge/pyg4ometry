===============
Developer notes
===============

Building the manual
^^^^^^^^^^^^^^^^^^^

To build the documentation ::

    pip install '.[docs]' # to install docs building dependencies
    cd pyg4ometry/docs
    make
    <your browser> build/html/index.html` # to view the docs

Running tests
^^^^^^^^^^^^^

Running tests ::

    pip install '.[test]' # to install test running dependencies
    pytest

Git
^^^

pre-commit::

    pre-commit install  # to setup pre-commit in source dir (only once)
    pre-commit run --all-files # run pre-commit locally
    pre-commit run --all-files black  #run only black

Start commit message with the submodule or area changes::

    submodule : (type of change) detailed notes

for example::

    pycgal : (extra functionality) more 2d mesh processing

Pull requests. PR messages should just explain the change in a concise way as they will form part of the change log
e.g::

    FLUKA region viewer
