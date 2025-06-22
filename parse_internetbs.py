import os
import sys
import json

from bs4 import BeautifulSoup


def main():

	if len(sys.argv) != 2:
		print('Usage: python parse.py <report.html>')
		sys.exit(1)

	html_path = sys.argv[1]
	with open(html_path, encoding='utf-8') as f:
		html = f.read()
	soup = BeautifulSoup(html, 'html.parser')

	operation_map = {
		'registration': 'registration',
		'renewal': 'renewal',
		'transfer': 'transfer',
		'restore': 'restore',
		# 'reactivate': 'restore',
	}

	tld_results = {}

	for header in soup.find_all('td', class_ = 'priceHeader'):
		operation_text = header.get_text(strip = True)
		parts = operation_text.split()
		if not parts or not parts[0].startswith('.'):
			print(f"Warning: Unexpected header format '{operation_text}'")
			continue
		tld = parts[0].lstrip('.').lower()
		op_raw = parts[1].lower()
		op_key = operation_map.get(op_raw)
		if not op_key:
			print(f"Warning: Unknown operation '{op_raw}' for TLD '{tld}'")
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
			print(f"Warning: No data row found for TLD '{tld}' and operation '{op_raw}'")
			continue

		# .find_next_sibling('tr')
		# if not tr:
		# 	print(f"Warning: No data row found for TLD '{tld}' and operation '{op_raw}'")
		# 	continue
		# tds = tr.find_all('td')
		# if len(tds) < 2:
		# 	tr = tr.find_next_sibling('tr')
		# 	if not tr:
		# 		print(f"Warning: No data row found for TLD '{tld}' and operation '{op_raw}'")
		# 		continue
		# 	tds = tr.find_all('td')
		# 	if len(tds) < 2:
		# 		print(f"Warning: Unexpected number of columns for TLD '{tld}' and operation '{op_raw}'")
		# 		continue

		# Always use the first period row (usually "1 year" or "1+ year")
		member_td = tds[1]
		# Prefer <span class="oldPrice"> if present, else fallback to text
		old_price_span = member_td.find('span', class_='oldPrice')
		if old_price_span:
			member_price = old_price_span.get_text(strip=True)
		else:
			member_price = member_td.get_text(strip=True).split()[0]

		if tld not in tld_results:
			tld_results[tld] = {
				"internetbs": {
					"registration": "",
					"renewal": "",
					"transfer": "",
					"restore": ""
				}
			}
		tld_results[tld]["internetbs"][op_key] = member_price

	for tld, data in tld_results.items():
		os.makedirs('domains', exist_ok=True)
		filename = f"domains/{tld}.json"
		# if any(not data["internetbs"][op] for op in operation_map.values()):
		# 	print(f"Warning: Incomplete data for TLD '{tld}'.")
		with open(filename, 'w', encoding='utf-8') as f:
			json.dump(data, f, indent=4, ensure_ascii=False)
		# print(f"Wrote {filename}")

if __name__ == '__main__':
    main()
