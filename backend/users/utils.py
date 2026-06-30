import phonenumbers

def normalize_phone(phone):

    try:
        parsed = phonenumbers.parse(phone, None)

        if not phonenumbers.is_valid_number(parsed):
            raise ValueError("Invalid phone number")

        return phonenumbers.format_number(
            parsed,
            phonenumbers.PhoneNumberFormat.E164
        )
    except Exception:
        raise ValueError("Invalid phone number")