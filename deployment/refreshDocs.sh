#!/bin/bash
pushd docs
rm -Rf _build
make html
popd
mkdir -p georegistry/public/docs
rm -Rf georegistry/public/docs/*
cp -R docs/_build/html/* georegistry/public/docs
