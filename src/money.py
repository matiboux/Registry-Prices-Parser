import re

def parse_currency_symbol(symbol):
	currency_symbols = {
		'€': 'eur',
		'$': 'usd',
		'us$': 'usd',
		'£': 'gbp',
	}
	return currency_symbols.get(symbol, symbol)

def parse_price(price_str):
	if not price_str:
		return None
	matches = re.match(r'^\s*(.*?)\s*(\d+(?:[.,]\d+)?)\s*(.*?)\s*$', price_str)
	if not matches:
		return { 'currency': None, 'price': price_str }
	currency_symbol = matches.group(1).strip() or matches.group(3).strip()
	currency = parse_currency_symbol(currency_symbol)
	price = matches.group(2).strip().replace(',', '.')
	return { 'currency': currency, 'price': price }
