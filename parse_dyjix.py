import sys

from bs4 import BeautifulSoup

from src.money import parse_price
from src.save_results import save_results


SERVICE_NAME = 'dyjix'

def get_tld_result(
	registration,
	renewal,
	transfer,
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

		registration_price = parse_price_str(cells[0].get_text(strip=True))
		transfer_price = parse_price_str(cells[1].get_text(strip=True))
		renewal_price = parse_price_str(cells[2].get_text(strip=True))

		tld_results[tld] = get_tld_result(
			registration_price,
			renewal_price,
			transfer_price,
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
