import os
import json
import re
from datetime import datetime

def get_tld_dirname(tld):
	tld_prefix = tld[0]
	if not re.match(r'^[a-z]$', tld_prefix):
		tld_prefix = '_'
	elif tld_prefix == 'x':
		if tld.startswith('xn--'):
			tld_prefix = '_'
	return f"domains/{tld_prefix}"

def save_results(
	service_name,
	tld_results,
	force_update = False,
):

	tlds_incomplete = []

	for tld, service_data in tld_results.items():

		tld_dir = get_tld_dirname(tld)
		os.makedirs(tld_dir, exist_ok=True)
		filename = f"{tld_dir}/{tld}.json"

		if any(not value for value in service_data.values()):
			tlds_incomplete.append(tld)

		data = {}
		if os.path.exists(filename):
			with open(filename, 'r', encoding='utf-8') as f:
				data = json.load(f)

		data['tld'] = tld.encode('ascii').decode('idna')

		if service_name not in data:
			data[service_name] = {}
		if 'date' not in data[service_name] or force_update:
			data[service_name]['date'] = datetime.now().isoformat()
		is_modified = False
		for key, value in service_data.items():
			if isinstance(value, dict):
				if key not in data[service_name]:
					data[service_name][key] = {}
				for sub_key, sub_value in value.items():
					if data[service_name][key].get(sub_key) != sub_value:
						data[service_name][key][sub_key] = sub_value
						is_modified = True
			else:
				if data[service_name].get(key) != value:
					data[service_name][key] = value
					is_modified = True
		if not force_update and is_modified:
			data[service_name]['date'] = datetime.now().isoformat()

		with open(filename, 'w', encoding='utf-8') as f:
			json.dump(data, f, indent = 4, ensure_ascii = False)

	print(f"Wrote {len(tld_results)} TLDs to JSON files.")

	tld_incomplete_len = len(tlds_incomplete)
	if tld_incomplete_len > 0:
		print(f"Warning: {tld_incomplete_len} TLDs have incomplete data.")
