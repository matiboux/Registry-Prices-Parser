import re

def parse_currency_symbol(symbol):
	currency_symbols = {
		'€': 'eur',
		'$': 'usd',
		'us$': 'usd',
		'£': 'gbp',
		'c$': 'cad',
		'¥': 'jpy',
	}
	return currency_symbols.get(symbol, symbol)

def parse_price(price_str, force_currency=None):
	if not price_str:
		return None
	matches = re.match(r'^\s*(.*?)\s*(\d+(?:[.,]\d+)?)\s*(.*?)\s*$', price_str)
	if not matches:
		currency = force_currency.strip().lower() if force_currency else None
		return { 'currency': currency, 'price': price_str }
	if force_currency:
		currency = force_currency.strip().lower()
	else:
		currency_symbol = matches.group(1).strip() or matches.group(3).strip()
		currency = parse_currency_symbol(currency_symbol)
	price = matches.group(2).strip().replace(',', '.')
	return { 'currency': currency, 'price': price }

def parse_price_str(price_str, force_currency=None):
	price_str = price_str.strip().lower()
	if not price_str or price_str == 'n/a':
		return None
	if price_str == 'free':
		price_str = '$0.00'
	return parse_price(price_str, force_currency=force_currency)
