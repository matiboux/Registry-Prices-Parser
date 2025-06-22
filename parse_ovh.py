import os
import sys
import json
import re

from bs4 import BeautifulSoup

from .src.money import parse_price


SERVICE_NAME = 'ovh'

def get_tld_result(
	registration,
	renewal,
	transfer,
):
	return {
		'registration': registration,
		'renewal': renewal,
		'transfer': transfer
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
		tld = tld.lstrip('.').encode('idna').decode('ascii')

		registration_price = parse_price(cells[1].get_text(strip=True))
		renewal_price = parse_price(cells[2].get_text(strip=True))
		transfer_price = parse_price(cells[3].get_text(strip=True))

		tld_results[tld] = get_tld_result(
			{ registration_price['currency']: registration_price['price'] },
			{ renewal_price['currency']: renewal_price['price'] },
			{ transfer_price['currency']: transfer_price['price'] },
		)

	return tld_results

def save_results(tld_results):

	tlds_incomplete = []

	for tld, service_data in tld_results.items():

		os.makedirs('domains', exist_ok=True)
		filename = f"domains/{tld}.json"

		if any(not value for value in service_data.values()):
			tlds_incomplete.append(tld)

		data = {}
		if os.path.exists(filename):
			with open(filename, 'r', encoding='utf-8') as f:
				data = json.load(f)

		data['tld'] = tld.encode('ascii').decode('idna')

		if SERVICE_NAME not in data:
			data[SERVICE_NAME] = {}
		for key, value in service_data.items():
			if isinstance(value, dict):
				if key not in data[SERVICE_NAME]:
					data[SERVICE_NAME][key] = {}
				data[SERVICE_NAME][key].update(value)
			else:
				data[SERVICE_NAME][key] = value

		with open(filename, 'w', encoding='utf-8') as f:
			json.dump(data, f, indent = 4, ensure_ascii = False)

	print(f"Wrote {len(tld_results)} TLDs to JSON files.")

	tld_incomplete_len = len(tlds_incomplete)
	if tld_incomplete_len > 0:
		print(f"Warning: {tld_incomplete_len} TLDs have incomplete data.")

def main():

	if len(sys.argv) != 2:
		print('Usage: python parse.py <report.html>')
		sys.exit(1)

	html_path = sys.argv[1]
	with open(html_path, encoding='utf-8') as f:
		html = f.read()

	tld_results = parse_html(html)

	save_results(tld_results)

if __name__ == '__main__':
	main()
