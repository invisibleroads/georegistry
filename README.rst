GeoRegistry
===========


Installation on Fedora
----------------------


Install geospatial libraries
^^^^^^^^^^^^^^^^^^^^^^^^^^^^
::

    su
        yum install gdal gdal-python geos proj proj-epsg proj-nad
        easy_install -U geoalchemy geojson pylons shapely


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


Prepare database
^^^^^^^^^^^^^^^^
::

    createuser -U postgres SET-USERNAME-HERE
    psql -U postgres -c "alter role SET-USERNAME-HERE with password 'SET-PASSWORD-HERE';"
    createdb -U postgres -T template_postgis -O SET-USERNAME-HERE SET-DATABASE-HERE
    paster setup-app production.ini


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


Installation on WebFaction
--------------------------


Install geospatial libraries
^^^^^^^^^^^^^^^^^^^^^^^^^^^^
::

    mkdir dependencies
    cd dependencies
    export PYTHONPATH=$HOME/lib/python2.7
    export LD_LIBRARY_PATH=$HOME/lib

    wget http://download.osgeo.org/proj/proj-4.7.0.tar.gz
    wget http://download.osgeo.org/proj/proj-datumgrid-1.5.zip
    tar xzvf proj-4.7.0.tar.gz
    unzip proj-datumgrid-1.5.zip -d proj-4.7.0/nad
    pushd proj-4.7.0
    ./configure --prefix=$HOME
    make install
    popd

    wget http://download.osgeo.org/geos/geos-3.2.2.tar.bz2
    tar xjvf geos-3.2.2.tar.bz2
    pushd geos-3.2.2
    ./configure --prefix=$HOME
    make install
    popd

    wget http://download.osgeo.org/gdal/gdal-1.7.3.tar.gz
    tar xzvf gdal-1.7.3.tar.gz
    pushd gdal-1.7.3
    ./configure --prefix=$HOME PYTHON=/usr/local/bin/python2.7 --with-pymoddir=$HOME/lib/python2.7 --with-python
    make install
    cd swig/python
    easy_install-2.7 --install-dir=$HOME/lib/python2.7 --script-dir=$HOME/bin -U .
    popd

    /usr/local/bin/easy_install-2.7 --install-dir=$HOME/lib/python2.7 --script-dir=$HOME/bin -U geoalchemy geojson pylons recaptcha-client shapely sphinx

    psql -U SET-USERNAME-HERE SET-DATABASE-HERE
        INSERT INTO spatial_ref_sys (srid, auth_name, auth_srid, srtext, proj4text) VALUES (900913, 'spatialreference.org', 900913, 'PROJCS["unnamed",GEOGCS["unnamed ellipse",DATUM["unknown",SPHEROID["unnamed",6378137,0]],PRIMEM["Greenwich",0],UNIT["degree",0.0174532925199433]],PROJECTION["Mercator_2SP"],PARAMETER["standard_parallel_1",0],PARAMETER["central_meridian",0],PARAMETER["false_easting",0],PARAMETER["false_northing",0],UNIT["Meter",1],EXTENSION["PROJ4","+proj=merc +a=6378137 +b=6378137 +lat_ts=0.0 +lon_0=0.0 +x_0=0.0 +y_0=0 +k=1.0 +units=m +nadgrids=@null +wktext  +no_defs"]]', '+proj=merc +a=6378137 +b=6378137 +lat_ts=0.0 +lon_0=0.0 +x_0=0.0 +y_0=0 +k=1.0 +units=m +nadgrids=@null +wktext  +no_defs');
        INSERT INTO "spatial_ref_sys" ("srid","auth_name","auth_srid","srtext","proj4text") VALUES (3857,'EPSG',3857,'PROJCS["Popular Visualisation CRS / Mercator (deprecated)",GEOGCS["Popular Visualisation CRS",DATUM["Popular_Visualisation_Datum",SPHEROID["Popular Visualisation Sphere",6378137,0,AUTHORITY["EPSG","7059"]],TOWGS84[0,0,0,0,0,0,0],AUTHORITY["EPSG","6055"]],PRIMEM["Greenwich",0,AUTHORITY["EPSG","8901"]],UNIT["degree",0.01745329251994328,AUTHORITY["EPSG","9122"]],AUTHORITY["EPSG","4055"]],UNIT["metre",1,AUTHORITY["EPSG","9001"]],PROJECTION["Mercator_1SP"],PARAMETER["central_meridian",0],PARAMETER["scale_factor",1],PARAMETER["false_easting",0],PARAMETER["false_northing",0],AUTHORITY["EPSG","3785"],AXIS["X",EAST],AXIS["Y",NORTH]]','+proj=merc +a=6378137 +b=6378137 +lat_ts=0.0 +lon_0=0.0 +x_0=0.0 +y_0=0 +units=m +k=1.0 +nadgrids=@null +no_defs' );

    wget http://www.gadm.org/data/shp/GTM_adm.zip
    unzip GTM_adm.zip

    cd $HOME/webapps/georegistry
    paster make-config georegistry production.ini
    paster setup-app production.ini
    python2.7 utilities/loadRegions.py -c production.ini $HOME/dependencies
    paster serve --daemon production.ini
    crontab deployment/crontab.crt
