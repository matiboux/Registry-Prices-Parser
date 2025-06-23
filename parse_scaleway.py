import sys

from bs4 import BeautifulSoup

from src.money import parse_price_str
from src.get_tld_result import get_tld_result
from src.save_results import save_results


SERVICE_NAME = 'scaleway'

def parse_html(html, force_currency = None):

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
		if not tld:
			continue
		tld = tld.encode('idna').decode('ascii')

		registration_price = parse_price_str(cells[1].get_text(strip=True), force_currency = force_currency)
		renewal_price = parse_price_str(cells[2].get_text(strip=True), force_currency = force_currency)
		transfer_price = parse_price_str(cells[3].get_text(strip=True), force_currency = force_currency)
		restore_price = parse_price_str(cells[4].get_text(strip=True), force_currency = force_currency)

		tld_results[tld] = get_tld_result(
			registration = registration_price,
			renewal = renewal_price,
			transfer = transfer_price,
			restore = restore_price,
		)

	return tld_results

def main():

	if len(sys.argv) < 2:
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
