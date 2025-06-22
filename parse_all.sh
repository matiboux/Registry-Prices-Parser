#!/bin/sh

# InternetBS
if [ -f 'internetbs.html' ]; then
	python parse_internetbs.py internetbs.html
fi

# Scaleway
if [ -f 'scaleway.html' ]; then
	python parse_scaleway.py scaleway.html
fi

# Namecheap
if [ -f 'namecheap.html' ]; then
	python parse_namecheap.py namecheap.html
fi

# Gandi
if [ -f 'gandi.html' ]; then
	python parse_gandi.py gandi.html
fi

# OVH
if [ -f 'ovh.html' ]; then
	python parse_ovh.py ovh.html
fi
if [ -f 'ovh_fr.html' ]; then
	python parse_ovh.py ovh_fr.html
fi
if [ -f 'ovh_en.html' ]; then
	python parse_ovh.py ovh_en.html
fi
