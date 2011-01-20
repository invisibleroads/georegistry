try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

setup(
    name='georegistry',
    version='0.2',
    description='Web service for centralizing geospatial data across applications',
    author='Roy Hyunjin Han',
    author_email='service@invisibleroads.com',
    url='georegistry.org',
    install_requires=[
        'Pylons>=1.0',
        'recaptcha-client>=1.0.5',
        'SQLAlchemy>=0.6.3',
        'geoalchemy>=0.4.1',
        'geojson>=1.0.1',
    ],
    setup_requires=["PasteScript>=1.6.3"],
    packages=find_packages(exclude=['ez_setup']),
    include_package_data=True,
    test_suite='nose.collector',
    package_data={'georegistry': ['i18n/*/LC_MESSAGES/*.mo']},
    #message_extractors={'georegistry': [
    #        ('**.py', 'python', None),
    #        ('templates/**.mako', 'mako', {'input_encoding': 'utf-8'}),
    #        ('public/**', 'ignore', None)]},
    zip_safe=False,
    paster_plugins=['PasteScript', 'Pylons'],
    entry_points="""
    [paste.app_factory]
    main = georegistry.config.middleware:make_app

    [paste.app_install]
    main = pylons.util:PylonsInstaller
    """,
    classifiers=[
        'Development Status :: 1 - Planning',
        'Environment :: Web Environment',
        'Framework :: Pylons',
        'Intended Audience :: Developers',
        'Intended Audience :: Education',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Operating System :: Unix',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Internet :: WWW/HTTP :: WSGI :: Application',
        'Topic :: Scientific/Engineering :: GIS',
        'Topic :: Scientific/Engineering :: Visualization',
    ],
)
