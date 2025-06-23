#!/bin/sh

# Requirements:
# apt update && apt install -y wget; pip install beautifulsoup4

RESET_DOMAINS=0
if [ $# -gt 0 ] && ([ "$1" = '-r' ] || [ "$1" = '--reset-domains' ]); then
	RESET_DOMAINS=1
fi

FORCE_DOWNLOAD=0
if [ $# -gt 0 ] && ([ "$1" = '-f' ] || [ "$1" = '--force-download' ]); then
	FORCE_DOWNLOAD=1
fi

if [ $RESET_DOMAINS -eq 1 ]; then
	rm -rf domains/
fi

mkdir -p html/
mkdir -p domains/

echo ''

# -- Cloudflare --
echo 'Parsing Cloudflare domain prices...'
if [ -f 'html/cloudflare.html' ]; then
	python parse_cloudflare.py html/cloudflare.html
fi
if [ ! -f 'html/cloudflare_usd.html' ] || [ $FORCE_DOWNLOAD -eq 1 ]; then
	wget -q -O 'html/cloudflare_usd.html' 'https://cfdomainpricing.com/' 2>/dev/null
fi
if [ -f 'html/cloudflare_usd.html' ]; then
	python parse_cloudflare.py html/cloudflare_usd.html
fi
if [ -f 'html/cloudflare_eur.html' ]; then
	python parse_cloudflare.py html/cloudflare_eur.html
fi
echo ''

# -- Dyjix --
echo 'Parsing Dyjix domain prices...'
if [ -f 'html/dyjix.html' ]; then
	python parse_dyjix.py html/dyjix.html
fi
if [ ! -f 'html/dyjix_eur.html' ] || [ $FORCE_DOWNLOAD -eq 1 ]; then
	wget -q -O 'html/dyjix_eur.html' 'https://www.dyjix.eu/panel/cart.php?a=add&domain=register&language=english' 2>/dev/null
fi
if [ -f 'html/dyjix_eur.html' ]; then
	python parse_dyjix.py html/dyjix_eur.html
fi
echo ''

# -- InternetBS --
# Automatic download is not available
echo 'Parsing InternetBS domain prices...'
if [ -f 'html/internetbs.html' ]; then
	python parse_internetbs.py html/internetbs.html
fi
if [ -f 'html/internetbs_usd.html' ]; then
	python parse_internetbs.py html/internetbs_usd.html
fi
if [ -f 'html/internetbs_eur.html' ]; then
	python parse_internetbs.py html/internetbs_eur.html
fi
echo ''

# -- Scaleway --
echo 'Parsing Scaleway domain prices...'
if [ ! -f 'html/scaleway.html' ] || [ $FORCE_DOWNLOAD -eq 1 ]; then
	wget -q -O 'html/scaleway.html' 'https://www.scaleway.com/en/domains-name/' 2>/dev/null
fi
if [ -f 'html/scaleway.html' ]; then
	python parse_scaleway.py html/scaleway.html
fi
echo ''

# -- Namecheap --
# Automatic download is not available
# https://www.namecheap.com/domains/
# Select "Choose from ALL" and copy source code instead of downloading
echo 'Parsing Namecheap domain prices...'
if [ -f 'html/namecheap.html' ]; then
	python parse_namecheap.py html/namecheap.html
fi
if [ -f 'html/namecheap_usd.html' ]; then
	python parse_namecheap.py html/namecheap_usd.html
fi
if [ -f 'html/namecheap_eur.html' ]; then
	python parse_namecheap.py html/namecheap_eur.html
fi
echo ''

# -- Gandi --
echo 'Parsing Gandi domain prices...'
if [ -f 'html/gandi.html' ]; then
	python parse_gandi.py html/gandi.html
fi
if [ ! -f 'html/gandi_xn.html' ] || [ $FORCE_DOWNLOAD -eq 1 ]; then
	wget -q -O 'html/gandi_xn.html' 'https://www.gandi.net/en/domain/tld?prefix=xn--' 2>/dev/null
fi
if [ -f 'html/gandi_xn.html' ]; then
	python parse_gandi.py html/gandi_xn.html
fi
while read -r letter; do
	if [ ! -f "html/gandi_${letter}.html" ] || [ $FORCE_DOWNLOAD -eq 1 ]; then
		wget -q -O "html/gandi_${letter}.html" "https://www.gandi.net/en/domain/tld?prefix=${letter}" 2>/dev/null
	fi
	if [ -f "html/gandi_${letter}.html" ]; then
		python parse_gandi.py "html/gandi_${letter}.html"
	fi
done <<EOF
$(echo 'abcdefghijklmnopqrstuvwxyz' | fold -w 1)
EOF
echo ''

# -- OVH --
# Automatic download is not available
# https://www.ovhcloud.com/en/domains/tld/
# Toggle "Renewal" and "Transfer" checkboxes
echo 'Parsing OVH domain prices...'
if [ -f 'html/ovh.html' ]; then
	python parse_ovh.py html/ovh.html
fi
if [ -f 'html/ovh_fr.html' ]; then
	python parse_ovh.py html/ovh_fr.html
fi
if [ -f 'html/ovh_en.html' ]; then
	python parse_ovh.py html/ovh_en.html
fi
echo ''
