#!/usr/bin/env python

import elementtree.ElementTree as ET
from canari.config import config
from pyNexpose import adhoc_report
import os, os.path
import email.Parser
from base64 import b64decode

__author__ = 'David Bressler (@bostonlink), GuidePoint Security LLC'
__copyright__ = 'Copyright 2013, GuidePoint Security LLC'
__credits__ = ['Rapid7 LLC', 'GuidePoint Security LLC']

__license__ = 'GPL'
__version__ = '0.1'
__maintainer__ = 'David Bressler (@bostonlink), GuidePoint Security LLC'
__email__ = 'david.bressler@guidepointsecurity.com'
__status__ = 'Development'

def reportChecker(session, siteid, report):
	fullp = os.path.join(config['nexpose/reportdir'], report)
	if os.path.exists(fullp):
		# for debug purposes
		return True
	else:
		adhoc = adhoc_report(session, siteid)
		adhoc_response = str(adhoc.headers) + str(adhoc.read())
		p = email.Parser.Parser()
		msg = p.parsestr(adhoc_response)
		try:
			for part in msg.walk():
				payload = part.get_payload()
				xmlreport = b64decode(str(payload))
				f = open(os.path.join(config['nexpose/reportdir'], report), 'w')
				f.write(xmlreport)
				f.close()
			# for debug purposes
			return True
		except Exception:
			return False

def nexposeVulns(report):
	rptxml = ET.fromstring(report)
	vulnlist = []
	for vuln in rptxml.findall(".//VulnerabilityDefinitions/vulnerability"):
		vulndic = {vuln.attrib['id'] : [vuln.attrib['title'], vuln.attrib['severity'], vuln.attrib['cvssScore']]}
		vulnlist.append(vulndic)

	return vulnlist

def nexposeExploits(report):
	rptxml = ET.fromstring(report)
	exploitlist = []
	for vuln in rptxml.findall(".//VulnerabilityDefinitions/vulnerability"):
		for exploit in vuln[1]:
			vulndic = {vuln.attrib['id'] : [exploit.get('title'), exploit.get('type'), exploit.get('link'), exploit.get('skillLevel')]}
			exploitlist.append(vulndic)

	return exploitlist

def nexposeHostname(report):
	rptxml = ET.fromstring(report)
	for hostname in rptxml.findall(".//nodes/node/names/name"):
		return hostname.text

def nexposeOS(report):
	rptxml = ET.fromstring(report)
	oslist = []
	for os in rptxml.findall(".//nodes/node/fingerprints/os"):
		try:
			itemlist = [os.attrib['device-class'], os.attrib['family'], os.attrib['vendor'], os.attrib['version'], os.attrib['certainty']]
			oslist.append(itemlist)
		except Exception:
			pass

	return oslist

def nexposePort(report):
	rptxml = ET.fromstring(report)
	portlist = []
	for ports in rptxml.findall(".//nodes/node/endpoints/endpoint"):
		portdic = {ports.attrib['port'] : [ports.attrib['protocol'], ports.attrib['status']]}
		portlist.append(portdic)

	return portlist

def nexposeService(report):
	rptxml = ET.fromstring(report)
	servicedic = {}
	for port in rptxml.findall(".//nodes/node/endpoints/endpoint"):
		for service in port[0]:
			servicedic[port.attrib['port']] = service.attrib['name']

	return servicedic

def nexposeServiceVer(report):
	rptxml = ET.fromstring(report)
	serverlist = []
	for service in rptxml.findall(".//nodes/node/endpoints/endpoint/services/service"):
		for ver in service[0]:
			try:
				if 'product' in ver.attrib and 'version' in ver.attrib and 'certainty' in ver.attrib:
					product, version, certainty = ver.attrib['product'], ver.attrib['version'], ver.attrib['certainty']
					serverdic = {service.attrib['name'] : [product, version, certainty]}
					serverlist.append(serverdic)
				elif 'product' in ver.attrib and 'version' in ver.attrib:
					product, version = ver.attrib['product'], ver.attrib['version']
					serverdic = {service.attrib['name'] : [product, version]}
					serverlist.append(serverdic)
				elif 'product' in ver.attrib:
					product = ver.attrib['product']
					serverdic = {service.attrib['name'] : [product]}
					serverlist.append(serverdic)
				elif 'version' in ver.attrib:
					version = ver.attrib['version']
					serverdic = {service.attrib['name'] : [version]}
					serverlist.append(serverdic)
				else:
					pass
			except Exception, e:
				pass

	return serverlist
			
def nexposeServiceTests(report):
	rptxml = ET.fromstring(report)
	servicelst = []
	xmllst = rptxml.findall(".//nodes/node/endpoints/endpoint")
	for port in xmllst:
		for service in port[0]:
			testdic = {}
			for test in service.getiterator('test'):
				testdic[test.attrib['id']] = test.attrib['status']
			
			servicedic = {service.attrib['name'] : testdic}
			servicelst.append(servicedic)

	return servicelst

def nexposePortTests(report):
	rptxml = ET.fromstring(report)
	portlist = []
	xmllst = rptxml.findall(".//nodes/node/endpoints/endpoint")
	for ports in xmllst:
		testdic = {}
		for test in ports.getiterator('test'):
			testdic[test.attrib['id']] = test.attrib['status']
			
		portdic = {ports.attrib['port'] : testdic}
		portlist.append(portdic)

	return portlist

def nexposeHostname(report):
	rptxml = ET.fromstring(report)
	xmllst = rptxml.findall(".//nodes/node/names/name")
	namelst = []
	for name in xmllst:
		namelst.append(name.text)

	return namelst