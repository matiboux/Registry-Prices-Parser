import sys

from bs4 import BeautifulSoup

from src.money import parse_price_str
from src.get_tld_result import get_tld_result
from src.save_results import save_results


SERVICE_NAME = 'dyjix'

def parse_html(html, force_currency = None):

	soup = BeautifulSoup(html, 'html.parser')
	tld_results = {}

	container = soup.find('div', class_ = 'domain-pricing')
	if not container:
		print("Warning: Domains pricing container not found.")
		return tld_results

	for row in container.find_all('div', class_='tld-row'):

		tld = row.find('div', class_ = 'col-md-4')
		tld = tld.get_text(strip=True).lower() if tld else ''
		if not tld.startswith('.'):
			continue
		tld = tld.lstrip('.').encode('idna').decode('ascii')

		prices_container = row.find('div', class_ = 'col-md-8')
		if not prices_container:
			continue

		cells = prices_container.find_all('div', class_='col-xs-4')

		registration_price = parse_price_str(cells[0].get_text(strip=True), force_currency = force_currency)
		transfer_price = parse_price_str(cells[1].get_text(strip=True), force_currency = force_currency)
		renewal_price = parse_price_str(cells[2].get_text(strip=True), force_currency = force_currency)

		tld_results[tld] = get_tld_result(
			registration = registration_price,
			renewal = renewal_price,
			transfer = transfer_price,
		)

	return tld_results

def main():

	if len(sys.argv) != 2:
		print('Usage: python parse.py [-f] <report.html> [force_currency]')
		sys.exit(1)

	argi = 1
	argc = len(sys.argv)

	force_update = False
	if sys.argv[argi] == '-f':
		force_update = True
		argi += 1

	html_path = sys.argv[argi]
	with open(html_path, encoding='utf-8') as f:
		html = f.read()
	argi += 1

	force_currency = None
	if argc > argi:
		force_currency = sys.argv[argi]
		argi += 1

	tld_results = parse_html(html, force_currency = force_currency)

	save_results(SERVICE_NAME, tld_results, force_update = force_update)

if __name__ == '__main__':
	main()
