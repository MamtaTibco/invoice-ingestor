# -*- coding: utf-8 -*-
"""XML parsing service."""
from lxml import etree


class XMLParsingError(Exception):
    """Custom exception for XML parsing errors."""


def parse_invoices(xml: str) -> list[str]:
    """
    Parses the XML response from the Bamboorose API and returns a list of individual invoice XML strings.

    Args:
        xml: The XML response from the Bamboorose API.

    Returns:
        A list of individual invoice XML strings.
    
    Raises:
        XMLParsingError: If the XML is malformed.
    """
    try:
        root = etree.fromstring(xml.encode("utf-8"))
        cdata = root.xpath("//*[local-name()='return']/text()")
        if not cdata:
            return []
        
        inner_xml = etree.fromstring(cdata[0].encode("utf-8"))
        invoices = inner_xml.xpath("//*[local-name()='invoice']")
        return [etree.tostring(invoice).decode("utf-8") for invoice in invoices]
    except etree.XMLSyntaxError as e:
        raise XMLParsingError(f"Failed to parse XML: {e}") from e
