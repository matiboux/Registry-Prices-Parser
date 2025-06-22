import os
import sys
import json

from bs4 import BeautifulSoup


SERVICE_NAME = 'internetbs'

TLD_RESULT_TEMPLATE = {
	'registration': '',
	'renewal': '',
	'transfer': '',
	'restore': ''
}

TLD_OPERATION_MAP = {
	'registration': 'registration',
	'renewal': 'renewal',
	'transfer': 'transfer',
	'restore': 'restore'
}

def parse_html(html):

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

		if tld not in tld_results:
			tld_results[tld] = TLD_RESULT_TEMPLATE.copy()

		tld_results[tld][op_key] = member_price

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
		data[SERVICE_NAME] = service_data

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
