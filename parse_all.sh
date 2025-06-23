#!/bin/sh

# Requirements:
# apt update && apt install -y wget; pip install beautifulsoup4

RESET_DOMAINS=0
FORCE_DOWNLOAD=0
FORCE_UPDATE_DATES=0

while [ $# -gt 0 ]; do

	if [ "$(echo "$1" | head -c 1)" = '-' ]; then
		break
	fi

	if [ "$1" = '-h' ] || [ "$1" = '--help' ]; then
		echo 'Usage:'
		echo '  parse_all.sh [options]'
		echo ''
		echo 'Options:'
		echo '  -r, --reset-domains    Reset the domains directory before parsing.'
		echo '  -f, --force-download   Force download of HTML files even if they exist.'
		echo '  -u, --update-dates     Update the dates of all parsed domains.'
		exit 0
	fi

	if [ "$1" = '-r' ] || [ "$1" = '--reset-domains' ]; then
		RESET_DOMAINS=1
		shift
		continue
	fi

	if [ "$1" = '-f' ] || [ "$1" = '--force-download' ]; then
		FORCE_DOWNLOAD=1
		shift
		continue
	fi

	if [ "$1" = '-u' ] || [ "$1" = '--update-dates' ]; then
		FORCE_UPDATE_DATES=1
		shift
		continue
	fi

done

if [ $RESET_DOMAINS -eq 1 ]; then
	rm -rf domains/
fi

mkdir -p html/
mkdir -p domains/

PARSE_SCRIPT_OPTIONS=''
if [ $FORCE_UPDATE_DATES -eq 1 ]; then
	PARSE_SCRIPT_OPTIONS='-u'
fi

echo ''

parse_service() {
	service_name="$1"
	for file in $(find html -type f -name "${service_name}[_\.]*"); do
        currency=$(echo "$file" | sed -n "s/.*${service_name}[_\.]\(.*[_\.]\)*\([a-z]\{3\}\)\.html\?$/\2/p")
        case "$currency" in
            eur|usd|cad|gbp)
                python "parse_${service_name}.py" $PARSE_SCRIPT_OPTIONS "$file" "$currency"
                ;;
            *)
                python "parse_${service_name}.py" $PARSE_SCRIPT_OPTIONS "$file"
                ;;
        esac
	done
}

# -- Cloudflare --
echo 'Parsing Cloudflare domain prices...'
if [ $FORCE_DOWNLOAD -eq 1 ] || [ ! -f 'html/auto/cloudflare_usd.html' ]; then
	mkdir -p html/auto/
	wget -q -O 'html/auto/cloudflare_usd.html' 'https://cfdomainpricing.com/' 2>/dev/null
fi
parse_service 'cloudflare'
echo ''

# -- Dyjix --
echo 'Parsing Dyjix domain prices...'
if [ $FORCE_DOWNLOAD -eq 1 ] || [ ! -f 'html/auto/dyjix_eur.html' ]; then
	mkdir -p html/auto/
	wget -q -O 'html/auto/dyjix_eur.html' 'https://www.dyjix.eu/panel/cart.php?a=add&domain=register&language=english' 2>/dev/null
fi
parse_service 'dyjix'
echo ''

# -- Gandi --
echo 'Parsing Gandi domain prices...'
while read -r currency; do
	currency_upper=$(echo "$currency" | tr '[:lower:]' '[:upper:]')
	if [ $FORCE_DOWNLOAD -eq 1 ] || [ ! -f "html/auto/gandi_xn_${currency}.html" ]; then
		mkdir -p html/auto/
		wget -q -O "html/auto/gandi_xn_${currency}.html" "https://www.gandi.net/en/domain/tld?currency=${currency_upper}&prefix=xn--" 2>/dev/null
	fi
	while read -r letter; do
		if [ $FORCE_DOWNLOAD -eq 1 ] || [ ! -f "html/auto/gandi_${letter}_${currency}.html" ]; then
			mkdir -p html/auto/
			wget -q -O "html/auto/gandi_${letter}_${currency}.html" "https://www.gandi.net/en/domain/tld?currency=${currency_upper}&prefix=${letter}" 2>/dev/null
		fi
	done <<-EOF
	$(echo 'abcdefghijklmnopqrstuvwxyz' | fold -w 1)
	EOF
done <<-EOF
eur
usd
gbp
EOF
parse_service 'gandi'
echo ''

# -- InternetBS --
# Automatic download is not available
# https://internetbs.net/en/price.html
echo 'Parsing InternetBS domain prices...'
parse_service 'internetbs'
echo ''

# -- Namecheap --
# Automatic download is not available
# https://www.namecheap.com/domains/
# Select "Choose from ALL" and copy source code instead of downloading
echo 'Parsing Namecheap domain prices...'
parse_service 'namecheap'
echo ''

# -- OVH --
# Automatic download is not available
# https://www.ovhcloud.com/en/domains/tld/
# Toggle "Renewal" and "Transfer" checkboxes
echo 'Parsing OVH domain prices...'
parse_service 'ovh'
echo ''

# -- Scaleway --
echo 'Parsing Scaleway domain prices...'
if [ $FORCE_DOWNLOAD -eq 1 ] || [ ! -f 'html/auto/scaleway.html' ]; then
	mkdir -p html/auto/
	wget -q -O 'html/auto/scaleway.html' 'https://www.scaleway.com/en/domains-name/' 2>/dev/null
fi
parse_service 'scaleway'
echo ''
