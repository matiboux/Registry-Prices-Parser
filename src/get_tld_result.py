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
			{ 'registration': { (registration['currency'] or 'unknown'): registration['price'] } }
			if registration else
			{}
		),
		**(
			{ 'renewal': { (renewal['currency'] or 'unknown'): renewal['price'] } }
			if renewal else
			{}
		),
		**(
			{ 'transfer': { (transfer['currency'] or 'unknown'): transfer['price'] } }
			if transfer else
			{}
		),
		**(
			{ 'owner_change': { (owner_change['currency'] or 'unknown'): owner_change['price'] } }
			if owner_change else
			{}
		),
		**(
			{ 'restore': { (restore['currency'] or 'unknown'): restore['price'] } }
			if restore else
			{}
		),
	}
