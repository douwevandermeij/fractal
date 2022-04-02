import re
import unicodedata


def camel_to_snake(name):
    name = re.sub(r"(.)([A-Z][a-z]+)", r"\1_\2", name)
    return re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", name).lower()


def snake_to_camel(name):
    return "".join(word.title() for word in name.split("_"))


def camel_case_to_spaces(value):
    """
    Split CamelCase and convert to lowercase. Strip surrounding whitespace.
    """
    re_camel_case = re.compile(r"(((?<=[a-z])[A-Z])|([A-Z](?![A-Z]|$)))")
    return re_camel_case.sub(r" \1", value).strip().lower()


def slugify(value, allow_unicode=False):
    """
    Convert to ASCII if 'allow_unicode' is False. Convert spaces to hyphens.
    Remove characters that aren't alphanumerics, underscores, or hyphens.
    Convert to lowercase. Also strip leading and trailing whitespace.
    """
    value = str(value)
    if allow_unicode:
        value = unicodedata.normalize("NFKC", value)
    else:
        value = (
            unicodedata.normalize("NFKD", value)
            .encode("ascii", "ignore")
            .decode("ascii")
        )
    value = re.sub(r"[^\w\s-]", "", value.lower()).strip()
    return re.sub(r"[-\s]+", "-", value)


def slug_is_valid(value, allow_unicode=False):
    if allow_unicode:
        slug_re = re.compile(r"^[-\w]+\Z")
    else:
        slug_re = re.compile(r"^[-a-zA-Z0-9_]+\Z")
    invalid_input = not slug_re.search(str(value))
    return not invalid_input
