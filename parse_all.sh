#!/bin/sh

RESET_DOMAINS=0
if [ $# -gt 0 ] && ([ "$1" = '-r' ] || [ "$1" = '--reset-domains' ]); then
	RESET_DOMAINS=1
fi

if [ $RESET_DOMAINS -eq 1 ]; then
	rm -rf domains/
fi

echo ''

# InternetBS
echo 'Parsing InternetBS domain prices...'
if [ -f 'internetbs.html' ]; then
	python parse_internetbs.py internetbs.html
fi
if [ -f 'internetbs_eur.html' ]; then
	python parse_internetbs.py internetbs_eur.html
fi
if [ -f 'internetbs_usd.html' ]; then
	python parse_internetbs.py internetbs_usd.html
fi
echo ''

# Scaleway
echo 'Parsing Scaleway domain prices...'
if [ -f 'scaleway.html' ]; then
	python parse_scaleway.py scaleway.html
fi
echo ''

# Namecheap
echo 'Parsing Namecheap domain prices...'
if [ -f 'namecheap.html' ]; then
	python parse_namecheap.py namecheap.html
fi
if [ -f 'namecheap_eur.html' ]; then
	python parse_namecheap.py namecheap_eur.html
fi
if [ -f 'namecheap_usd.html' ]; then
	python parse_namecheap.py namecheap_usd.html
fi
echo ''

# Gandi
if [ -f 'gandi.html' ]; then
	python parse_gandi.py gandi.html
fi

# OVH
echo 'Parsing OVH domain prices...'
if [ -f 'ovh.html' ]; then
	python parse_ovh.py ovh.html
fi
if [ -f 'ovh_fr.html' ]; then
	python parse_ovh.py ovh_fr.html
fi
if [ -f 'ovh_en.html' ]; then
	python parse_ovh.py ovh_en.html
fi
echo ''
