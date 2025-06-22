import os
import json

def save_results(service_name, tld_results):

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

		if service_name not in data:
			data[service_name] = {}
		for key, value in service_data.items():
			if isinstance(value, dict):
				if key not in data[service_name]:
					data[service_name][key] = {}
				data[service_name][key].update(value)
			else:
				data[service_name][key] = value

		with open(filename, 'w', encoding='utf-8') as f:
			json.dump(data, f, indent = 4, ensure_ascii = False)

	print(f"Wrote {len(tld_results)} TLDs to JSON files.")

	tld_incomplete_len = len(tlds_incomplete)
	if tld_incomplete_len > 0:
		print(f"Warning: {tld_incomplete_len} TLDs have incomplete data.")
