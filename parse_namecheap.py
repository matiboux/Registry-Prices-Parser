import sys

from bs4 import BeautifulSoup

from src.money import parse_price
from src.save_results import save_results


SERVICE_NAME = 'namecheap'

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

def find_price_str(cell):
	price_special = cell.find(class_ = 'gb-price--special')
	if not price_special:
		return cell.get_text(strip = True)
	price_through = price_special.find(class_ = 'gb-text--through')
	if not price_through:
		return price_special.get_text(strip = True)
	return price_through.get_text(strip = True)

def parse_html(html):

	soup = BeautifulSoup(html, 'html.parser')
	tld_results = {}

	container = soup.find('div', class_='gb-domains__pricing')
	if not container:
		print("Warning: Domains pricing container not found.")
		return tld_results

	tbody = container.find('tbody')
	if not tbody:
		print("Warning: No <tbody> found in the HTML.")
		return tld_results

	for row in tbody.find_all('tr'):

		cells = row.find_all('td')
		if len(cells) < 4:
			continue

		# Get tld in .gb-tld-name
		tld = cells[0].find(class_='gb-tld-name')
		tld = tld.get_text(strip = True).lower() if tld else ''
		if not tld.startswith('.'):
			continue
		tld = tld.lstrip('.').encode('idna').decode('ascii')

		registration_price = parse_price(find_price_str(cells[1]))
		renewal_price = parse_price(find_price_str(cells[2]))
		transfer_price = parse_price(find_price_str(cells[3]))

		tld_results[tld] = get_tld_result(
			{ registration_price['currency']: registration_price['price'] },
			{ renewal_price['currency']: renewal_price['price'] },
			{ transfer_price['currency']: transfer_price['price'] },
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
