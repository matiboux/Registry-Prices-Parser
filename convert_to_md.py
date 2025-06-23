import json
import os
import re
import glob
from datetime import datetime

DOMAINS_DIR = './domains'
MD_DIR = './markdown'

fmt_service_map = {
	'cloudflare': 'Cloudflare',
	'dyjix': 'Dyjix',
	'Gandi': 'Gandi',
	'internetbs': 'Internet.bs',
	'namecheap': 'Namecheap',
	'ovh': 'OVH',
	'scaleway': 'Scaleway',
}

def fmt_service(service):
	return fmt_service_map.get(service, service.capitalize())

def fmt_date(date):
	try:
		return datetime.fromisoformat(date).strftime('%Y-%m-%d')
	except Exception:
		return date.split('T')[0] if 'T' in date else date

def convert_usd_to_eur(usd_value):
	return float(usd_value) * 0.86770

def fmt_eur_from_usd(usd_value):
	usd_value = float(usd_value)
	if usd_value == 0:
		return '€ 0.00'
	return f"€ ~ {convert_usd_to_eur(usd_value):.2f}"

def fmt_price(price):
	if not price:
		return ''
	if isinstance(price, int) or (isinstance(price, str) and price.isdigit()):
		return f"${int(price)}"
	if isinstance(price, float):
		return f"${price:.2f}"
	if 'eur' in price:
		if 'usd' in price:
			return f"€ {price['eur']}<br>($ {price['usd']})"
		else:
			return f"€ {price['eur']}"
	if 'usd' in price:
		return f"{fmt_eur_from_usd(price['usd'])}<br>($ {price['usd']})"
	return json.dumps(price)

def get_price_eur_to_compare(prices):
	if not isinstance(prices, dict):
		return float('inf')
	if 'eur' in prices:
		return float(prices['eur'])
	if 'usd' in prices:
		return convert_usd_to_eur(prices['usd'])
	return float('inf')

def main():

	# List files in the domains directory
	if not os.path.exists(DOMAINS_DIR):
		print(f"Directory {DOMAINS_DIR} does not exist.")
		return

	# List files in the domains directory and subdirectories
	files = glob.glob(os.path.join(DOMAINS_DIR, '**', '*.json'), recursive = True)
	if not files:
		print(f"No files found in {DOMAINS_DIR}.")
		return

	# Iterate over JSON files
	for file in files:
		if not file.endswith('.json'):
			continue

		# Read JSON file
		file = file[len(DOMAINS_DIR) + 1:]  # Relative path from DOMAINS_DIR
		json_path = os.path.join(DOMAINS_DIR, file)
		with open(json_path, 'r') as f:
			data = json.load(f)

		# Table header
		table_header = (
			'| Service | Date |  | / Renewed year | First year | Transfer | Restoration |\n'
			'|--|--|--|--|--|--|--|'
		)

		# Fix the cheapest domain for renewal
		cheapest_service = min(
			data.keys(),
			key = lambda k: (
				get_price_eur_to_compare(data[k].get('renewal', float('inf')))
				if isinstance(data[k], dict) else
				float('inf')
			)
		)

		# Compose table rows
		rows = []
		for service_key in sorted(data.keys()):
			if service_key == 'tld':
				continue
			entry = data[service_key]
			service = fmt_service(service_key)
			date = fmt_date(entry.get('date', ''))
			emoji = '🏆' if service_key == cheapest_service else ''
			renewal = fmt_price(entry.get('renewal', ''))
			registration = fmt_price(entry.get('registration', ''))
			transfer = fmt_price(entry.get('transfer', ''))
			restore = fmt_price(entry.get('restore', ''))
			row = f'| **{service}** | {date} | {emoji} | {renewal} | {registration} | {transfer} | {restore} |'
			rows.append(row)

		table = table_header + '\n' + '\n'.join(rows)

		# Compute the markdown file path
		md_path = os.path.join(MD_DIR, f'{file[:-5].upper()}.md')

		file_updated = False
		if os.path.exists(md_path):
			with open(md_path, 'r') as f:
				raw_md = f.read()
			def sub_md(_):
				nonlocal file_updated
				file_updated = True
				return table + '\n\n'
			new_md = re.sub(
				r'\| Service.*\n\|--.*(?:\n\|.*)*(?:\n\n|$)',
				sub_md,
				raw_md,
				count = 1,
				flags = re.NOFLAG,
			)
			if not file_updated:
				# Table not found, append
				new_md = raw_md.rstrip() + '\n\n' + table + '\n'

		else:
			# Markdown file does not exist, create new
			new_md = f"""
			# Compare `.{data['tld']}` domain names

			## Summary

			Pricing (excluding taxes):

			{table}
			""".lstrip().replace('\t', '')

		# Write the updated markdown content
		os.makedirs(os.path.dirname(md_path), exist_ok = True)
		with open(md_path, 'w') as f:
			f.write(new_md)

	print(f"Wrote {len(files)} markdown files to {MD_DIR}.")

if __name__ == '__main__':
	main()
