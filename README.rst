georegistry
===========
::

    # Prepare isolated environment
    PYRAMID_ENV=$HOME/Projects/pyramid-env
    virtualenv --no-site-packages $PYRAMID_ENV 
    # Activate isolated environment
    source $PYRAMID_ENV/bin/activate
    # Install packages
    pip install ipython ipdb nose coverage

    # Enter repository
    PROJECTS=$HOME/Projects
    cd $PROJECTS/georegistry
    # Install dependencies
    python setup.py develop

    # Edit sensitive information
    vim .test.ini
    # Run tests with coverage
    nosetests --pdb --pdb-failures
    # Show URL routes
    paster proutes development.ini georegistry
    # Run shell
    paster pshell development.ini georegistry

    # Edit sensitive information
    vim .development.ini
    # Start development server
    paster serve --reload development.ini

    # Edit sensitive information
    vim .production.ini
    # Start production server
    paster serve --daemon production.ini

    # Edit and install crontab
    vim deployment/server.crt
    crontab deployment/server.crt
