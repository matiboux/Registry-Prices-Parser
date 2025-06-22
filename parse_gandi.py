import sys

from bs4 import BeautifulSoup

from src.money import parse_price
from src.save_results import save_results


SERVICE_NAME = 'gandi'

def get_tld_result(
	registration,
	renewal,
	transfer,
	owner_change,
	restore,
):
	return {
		**(
			{ 'registration': { registration['currency']: registration['price'] } }
			if registration else
			{}
		),
		**(
			{ 'renewal': { renewal['currency']: renewal['price'] } }
			if renewal else
			{}
		),
		**(
			{ 'transfer': { transfer['currency']: transfer['price'] } }
			if transfer else
			{}
		),
		**(
			{ 'owner_change': { owner_change['currency']: owner_change['price'] } }
			if owner_change else
			{}
		),
		**(
			{ 'restore': { restore['currency']: restore['price'] } }
			if restore else
			{}
		),
	}

def parse_price_str(price_str):
	price_str = price_str.strip().lower()
	if not price_str or price_str == 'n/a':
		return None
	if price_str == 'free':
		price_str = '0.00'
	return parse_price(price_str)

def parse_html(html):

	soup = BeautifulSoup(html, 'html.parser')
	tld_results = {}

	tbody = soup.find('tbody')
	if not tbody:
		print("Warning: No <tbody> found in the HTML.")
		return tld_results

	for row in tbody.find_all('tr'):

		cells = row.find_all(['td', 'th'])
		if len(cells) < 6:
			continue

		tld = cells[0].get_text(strip=True).lower()
		if not tld.startswith('.'):
			continue
		tld = tld.lstrip('.').encode('idna').decode('ascii')

		registration_price = parse_price_str(cells[1].get_text(strip=True))
		renewal_price = parse_price_str(cells[2].get_text(strip=True))
		transfer_price = parse_price_str(cells[3].get_text(strip=True))
		owner_change_price = parse_price_str(cells[4].get_text(strip=True))
		restore_price = parse_price_str(cells[5].get_text(strip=True))

		tld_results[tld] = get_tld_result(
			registration_price,
			renewal_price,
			transfer_price,
			owner_change_price,
			restore_price,
		)

	return tld_results

def main():

	if len(sys.argv) != 2:
		print('Usage: python parse.py <report.html>')
		sys.exit(1)

	html_path = sys.argv[1]
	with open(html_path, encoding='utf-8') as f:
		html = f.read()

	tld_results = parse_html(html)

	save_results(SERVICE_NAME, tld_results)

if __name__ == '__main__':
	main()
