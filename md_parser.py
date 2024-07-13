import logging
import re

from sas_util import generate_signed_url


regex = r"(.*?)(gs:\/\/.*?)([\]\)>}]|\s|$)"


def convert_to_sas_uri(line: str):
    match = re.match(regex, line)
    if not match:
        return line
    _, uri, _ = match.groups()
    logging.info("Converting %s...", uri)
    return re.sub(regex, f"\\1{generate_signed_url(uri)}\\3", line)


def parse_md(md: str):
    return "\n".join([convert_to_sas_uri(line) for line in md.splitlines()])
