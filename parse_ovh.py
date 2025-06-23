import sys

from bs4 import BeautifulSoup

from src.money import parse_price_str
from src.save_results import save_results


SERVICE_NAME = 'ovh'

def get_tld_result(
	registration,
	renewal,
	transfer,
):
	return {
		'registration': registration,
		'renewal': renewal,
		'transfer': transfer,
	}

def parse_html(html):

	soup = BeautifulSoup(html, 'html.parser')
	tld_results = {}

	tbody = soup.find('tbody')
	if not tbody:
		print("Warning: No <tbody> found in the HTML.")
		return tld_results

	for row in tbody.find_all('tr'):

		cells = row.find_all(['td', 'th'])
		if len(cells) < 4:
			continue

		tld = cells[0].get_text(strip=True).lower()
		if not tld.startswith('.'):
			continue
		tld = tld.replace('promotion', '').strip()
		tld = tld.lstrip('.').encode('idna').decode('ascii')

		registration_price = parse_price_str(cells[1].get_text(strip=True))
		renewal_price = parse_price_str(cells[2].get_text(strip=True))
		transfer_price = parse_price_str(cells[3].get_text(strip=True))

		tld_results[tld] = get_tld_result(
			{ registration_price['currency']: registration_price['price'] },
			{ renewal_price['currency']: renewal_price['price'] },
			{ transfer_price['currency']: transfer_price['price'] },
		)

	return tld_results

def main():

	if len(sys.argv) != 2:
		print('Usage: python parse.py [-f] <report.html>')
		sys.exit(1)

	argi = 1
	force_update = False
	if sys.argv[argi] == '-f':
		force_update = True
		argi += 1

	html_path = sys.argv[argi]
	with open(html_path, encoding='utf-8') as f:
		html = f.read()

	tld_results = parse_html(html)

	save_results(SERVICE_NAME, tld_results, force_update = force_update)

if __name__ == '__main__':
	main()
