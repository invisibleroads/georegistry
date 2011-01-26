dropdb -U postgres georegistry
createdb -U postgres -T template_postgis -O georegistry georegistry
paster setup-app development.ini
