import logging
import re

from sas_util import generate_signed_url


regex = r"(.*?)(gs:\/\/.*?)([\]\)>}]|\s|$)"


def convert_to_sas_uri(line: str):
    # this function takes a line of markdown and converts any gs:// URIs to signed URLs
    # it uses a regex to match the gs:// URIs and then uses the generate_signed_url function to generate a signed URL
    # the signed URL is then used to replace the gs:// URI in the line of markdown
    # the function returns the line of markdown with the gs:// URIs replaced with signed URLs
    match = re.match(regex, line)
    if not match:
        return line
    _, uri, _ = match.groups()
    logging.info("Converting %s...", uri)
    return re.sub(regex, f"\\1{generate_signed_url(uri)}\\3", line)


def parse_md(md: str):
    return "\n".join([convert_to_sas_uri(line) for line in md.splitlines()])
