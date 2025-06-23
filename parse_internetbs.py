import sys

from bs4 import BeautifulSoup

from src.money import parse_price_str
from src.save_results import save_results


SERVICE_NAME = 'internetbs'

TLD_OPERATION_MAP = {
	'registration': 'registration',
	'renewal': 'renewal',
	'transfer': 'transfer',
	'restore': 'restore'
}

def parse_html(html, force_currency = None):

	soup = BeautifulSoup(html, 'html.parser')
	tld_results = {}

	for header in soup.find_all('td', class_ = 'priceHeader'):
		operation_text = header.get_text(strip = True)
		parts = operation_text.split()
		if not parts or not parts[0].startswith('.'):
			print(f"Warning: Unexpected header format '{operation_text}'")
			continue
		tld = parts[0].lstrip('.').lower()
		op_key = parts[1].lower()
		if op_key not in TLD_OPERATION_MAP:
			print(f"Warning: Unknown operation '{op_key}' for TLD '{tld}'")
			continue

		# Find the data row in the next one or two rows
		tr = header.find_parent('tr')
		tds = None
		for _ in range(2):
			tr = tr.find_next_sibling('tr')
			if not tr:
				break
			tds = tr.find_all('td')
			if len(tds) >= 2:
				break
		else:
			tds = None

		if not tds:
			print(f"Warning: No data row found for TLD '{tld}' and operation '{op_key}'")
			continue

		member_td = tds[1]
		old_price_span = member_td.find('span', class_='oldPrice')
		if old_price_span:
			member_price = old_price_span.get_text(strip=True)
		else:
			member_price = member_td.get_text(strip=True).split()[0]

		member_price = parse_price_str(member_price, force_currency=force_currency)

		if tld not in tld_results:
			tld_results[tld] = {}

		tld_results[tld][op_key] = {
			member_price['currency']: member_price['price']
		}

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
