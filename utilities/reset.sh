dropdb -U postgres georegistry
createdb -U postgres -T template_postgis -O georegistry georegistry
paster serve --reload development.ini
