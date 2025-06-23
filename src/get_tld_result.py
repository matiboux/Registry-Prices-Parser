def get_tld_result(
	*,
	registration = None,
	renewal = None,
	transfer = None,
	owner_change = None,
	restore = None,
):
	return {
		**(
			{ 'registration': { (registration['currency'] or ''): registration['price'] } }
			if registration else
			{}
		),
		**(
			{ 'renewal': { (renewal['currency'] or ''): renewal['price'] } }
			if renewal else
			{}
		),
		**(
			{ 'transfer': { (transfer['currency'] or ''): transfer['price'] } }
			if transfer else
			{}
		),
		**(
			{ 'owner_change': { (owner_change['currency'] or ''): owner_change['price'] } }
			if owner_change else
			{}
		),
		**(
			{ 'restore': { (restore['currency'] or ''): restore['price'] } }
			if restore else
			{}
		),
	}
