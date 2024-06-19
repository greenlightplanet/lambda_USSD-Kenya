def is_null_or_empty(text):
    if text is None:
        return True
    if isinstance(text, str):
        text = text.strip()
        if not text:
            return True
        else:
            return False
    return False


def equals_ignore_case(string1, string2):
    if string1.lower() == string2.lower():
        return True
    else:
        return False


def is_valid_key(dictionary, key_to_validate):
    if key_to_validate not in dictionary:
        return False
    elif is_null_or_empty(dictionary.get(key_to_validate)):
        return False
    else:
        return True


def str_to_bool(s):
    if equals_ignore_case(s, 'True'):
         return True
    elif equals_ignore_case(s, 'False'):
         return False
    else:
         raise ValueError