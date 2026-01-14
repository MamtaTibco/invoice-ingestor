# -*- coding: utf-8 -*-
"""Unit tests for the XML parsing service."""
import re

import pytest

from src.services.parser import parse_invoices, XMLParsingError


def _strip_whitespace(xml: str) -> str:
    """Removes all whitespace from an XML string."""
    return re.sub(r"\s+", "", xml)


def test_parse_invoices_single_invoice():
    """Test that the parse_invoices function correctly parses a response with a single invoice."""
    xml = """
    <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/">
       <soapenv:Body>
          <ns1:getCommercialInvoicesByAvailableTimestampResponse xmlns:ns1="http://services.bamboorose.com">
             <ns1:return><![CDATA[<?xml version='1.0' encoding='UTF-8'?>
                <document>
                    <invoice>
                        <invoiceId>123</invoiceId>
                    </invoice>
                </document>
             ]]></ns1:return>
          </ns1:getCommercialInvoicesByAvailableTimestampResponse>
       </soapenv:Body>
    </soapenv:Envelope>
    """
    invoices = parse_invoices(xml)
    assert len(invoices) == 1
    assert _strip_whitespace(invoices[0]) == "<invoice><invoiceId>123</invoiceId></invoice>"


def test_parse_invoices_multiple_invoices():
    """Test that the parse_invoices function correctly parses a response with multiple invoices."""
    xml = """
    <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/">
       <soapenv:Body>
          <ns1:getCommercialInvoicesByAvailableTimestampResponse xmlns:ns1="http://services.bamboorose.com">
             <ns1:return><![CDATA[<?xml version='1.0' encoding='UTF-8'?>
                <document>
                    <invoice>
                        <invoiceId>123</invoiceId>
                    </invoice>
                    <invoice>
                        <invoiceId>456</invoiceId>
                    </invoice>
                </document>
             ]]></ns1:return>
          </ns1:getCommercialInvoicesByAvailableTimestampResponse>
       </soapenv:Body>
    </soapenv:Envelope>
    """
    invoices = parse_invoices(xml)
    assert len(invoices) == 2
    assert _strip_whitespace(invoices[0]) == "<invoice><invoiceId>123</invoiceId></invoice>"
    assert _strip_whitespace(invoices[1]) == "<invoice><invoiceId>456</invoiceId></invoice>"


def test_parse_invoices_no_invoices():
    """Test that the parse_invoices function correctly handles a response with no invoices."""
    xml = """
    <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/">
       <soapenv:Body>
          <ns1:getCommercialInvoicesByAvailableTimestampResponse xmlns:ns1="http://services.bamboorose.com">
             <ns1:return><![CDATA[<?xml version='1.0' encoding='UTF-8'?>
                <document>
                </document>
             ]]></ns1:return>
          </ns1:getCommercialInvoicesByAvailableTimestampResponse>
       </soapenv:Body>
    </soapenv:Envelope>
    """
    invoices = parse_invoices(xml)
    assert len(invoices) == 0


def test_parse_invoices_malformed_xml():
    """Test that the parse_invoices function raises an XMLParsingError for malformed XML."""
    xml = """
    <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/">
       <soapenv:Body>
          <ns1:getCommercialInvoicesByAvailableTimestampResponse xmlns:ns1="http://services.bamboorose.com">
             <ns1:return><![CDATA[<?xml version='1.0' encoding='UTF-8'?>
                <document>
                    <invoice>
                        <invoiceId>123</invoiceId>
                    </invoice
                </document>
             ]]></ns1:return>
          </ns1:getCommercialInvoicesByAvailableTimestampResponse>
       </soapenv:Body>
    </soapenv:Envelope>
    """
    with pytest.raises(XMLParsingError):
        parse_invoices(xml)
