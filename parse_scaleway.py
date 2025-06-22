import os
import sys
import json

from bs4 import BeautifulSoup


SERVICE_NAME = 'scaleway'

def get_tld_result(
	registration,
	renewal,
	transfer,
	restore,
):
	return {
		SERVICE_NAME: {
			'registration': registration,
			'renewal': renewal,
			'transfer': transfer,
			'restore': restore
		}
	}

def parse_html(html):

	soup = BeautifulSoup(html, 'html.parser')
	tld_results = {}

	for row in soup.find_all('tr'):

		cells = row.find_all(['td', 'th'])
		if len(cells) < 4:
			continue

		tld = cells[0].get_text(strip=True).lstrip('.').lower()
		registration = cells[1].get_text(strip=True)
		renewal = cells[2].get_text(strip=True)
		transfer = cells[3].get_text(strip=True)
		restore = cells[4].get_text(strip=True) if len(cells) > 4 else ""

		tld_results[tld] = get_tld_result(
			registration,
			renewal,
			transfer,
			restore
		)

	return tld_results

def save_results(tld_results):

	tlds_incomplete = []

	for tld, new_data in tld_results.items():

		os.makedirs('domains', exist_ok=True)
		filename = f"domains/{tld}.json"

		data = {}
		if os.path.exists(filename):
			with open(filename, 'r', encoding='utf-8') as f:
				data = json.load(f)
		data.update(new_data)

		if any(not value for data in tld_results.values() for value in data[SERVICE_NAME].values()):
			tlds_incomplete.append(tld)

		with open(filename, 'w', encoding='utf-8') as f:
			json.dump(new_data, f, indent = 4, ensure_ascii = False)

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
