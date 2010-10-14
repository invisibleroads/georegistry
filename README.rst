GeoRegistry
===========

Installation
------------

Install geospatial libraries
^^^^^^^^^^^^^^^^^^^^^^^^^^^^
::

    su
        yum install gdal gdal-python geos proj
        easy_install -U geoalchemy shapely


Install PostgreSQL
^^^^^^^^^^^^^^^^^^
::

    su
        yum install postgresql postgresql-devel postgresql-server python-psycopg2 postgis
        service postgresql initdb
        service postgresql start
        passwd postgres
        su - postgres
            psql
                alter role postgres with password 'SET-PASSWORD-HERE'
            vim data/pg_hba.conf
                # "local" is for Unix domain socket connections only
                local   all         all                               md5
                # IPv4 local connections:
                host    all         all         127.0.0.1/32          md5
                # IPv6 local connections:
                host    all         all         ::1/128               md5
        service postgresql restart


Prepare database
^^^^^^^^^^^^^^^^
::
    
    su
        su - postgres
            createdb -E UTF8 SET-DATABASE-HERE
            createlang -d SET-DATABASE-HERE plpgsql
            # psql -d SET-DATABASE-HERE -f /usr/share/pgsql/contrib/postgis.sql
            psql -d SET-DATABASE-HERE -f /usr/share/pgsql/contrib/postgis-64.sql
            psql -d SET-DATABASE-HERE -f /usr/share/pgsql/contrib/spatial_ref_sys.sql

            createuser SET-USERNAME-HERE
            psql SET-DATABASE-HERE
                alter role SET-USERNAME-HERE with password 'SET-PASSWORD-HERE';
                grant all on database SET-DATABASE-HERE to "SET-USERNAME-HERE";
                grant all on spatial_ref_sys to "SET-USERNAME-HERE";
                grant all on geometry_columns to "SET-USERNAME-HERE";


Configure settings
^^^^^^^^^^^^^^^^^^
::

    cp default.cfg .production.cfg
    vim .production.cfg


Install tables
^^^^^^^^^^^^^^
::

    paster setup-app production.ini
