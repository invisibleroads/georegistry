GeoRegistry
===========


Installation on Fedora
----------------------


Install geospatial libraries
^^^^^^^^^^^^^^^^^^^^^^^^^^^^
::

    su
        yum install gdal gdal-python geos proj proj-epsg proj-nad
        easy_install -U geoalchemy geojson pylons shapely sphinx sqlalchemy


Install PostgreSQL
^^^^^^^^^^^^^^^^^^
::

    su
        yum install postgresql postgresql-devel postgresql-server python-psycopg2 postgis
        service postgresql initdb
        service postgresql start
        passwd postgres
        su - postgres
            psql -c "alter role postgres with password 'SET-PASSWORD-HERE';"
            vim data/pg_hba.conf
                # "local" is for Unix domain socket connections only
                local   all         all                               md5
                # IPv4 local connections:
                host    all         all         127.0.0.1/32          md5
                # IPv6 local connections:
                host    all         all         ::1/128               md5
        service postgresql restart


Prepare production configuration
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
::

    paster make-config georegistry production.ini
    vim production.ini


Prepare database template
^^^^^^^^^^^^^^^^^^^^^^^^^
::

    su - postgres
        createdb -E UTF8 template_postgis
        createlang -d template_postgis plpgsql
        PGSHARE=`pg_config --sharedir`
        psql -d template_postgis -f `find $PGSHARE -name postgis.sql -o -name postgis-64.sql | tail -n 1`
        psql -d template_postgis -f `find $PGSHARE -name spatial_ref_sys.sql | tail -n 1`
        psql -d template_postgis -c 'GRANT ALL ON geometry_columns TO PUBLIC; GRANT ALL ON spatial_ref_sys TO PUBLIC;'


Prepare database and documentation
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
::

    createuser -U postgres SET-USERNAME-HERE
    psql -U postgres -c "alter role SET-USERNAME-HERE with password 'SET-PASSWORD-HERE';"
    createdb -U postgres -T template_postgis -O SET-USERNAME-HERE SET-DATABASE-HERE
    paster setup-app production.ini
    bash deployment/refreshDocs.sh


Load data
^^^^^^^^^
::

    wget http://www.gadm.org/data/shp/GTM_adm.zip -P gadm
    unzip gadm/*.zip -d gadm
    python utilities/loadGADM.py -c production.ini gadm


Launch server
^^^^^^^^^^^^^
::

    paster serve --daemon production.ini

    
Reset database
^^^^^^^^^^^^^^
::

    dropdb -U postgres SET-DATABASE-HERE
    createdb -U postgres -T template_postgis -O SET-USERNAME-HERE SET-DATABASE-HERE
    paster setup-app production.ini
