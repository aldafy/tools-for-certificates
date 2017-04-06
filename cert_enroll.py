# -*- coding: utf-8 -*-
import argparse
import requests
import sys
from BeautifulSoup import BeautifulSoup as Soup


parser = argparse.ArgumentParser()
parser.add_argument('-ca', '--authority', help='Address of your MS Certification Authority', required=True)
parser.add_argument('-r', '--request', help='Input request file', required=True)
parser.add_argument('-c', '--certificate', help='Output certificate file', required=True)
parser.add_argument('-p', '--proxy', help='Proxy with port without protocol, optional')
parser.add_argument('--secured', action='store_true',
                    help='Use this option if your CA is secured (using https potocol)')
args = parser.parse_args()
proxy = None
try:
    with open(args.request) as req_file:
        request_data = req_file.read()
except Exception as e:
    print e
    sys.exit(-1)

if args.proxy:
    proxy = {'https': args.proxy} if args.secured else {'http': args.proxy}
if requests.get('http://{}'.format(args.authority), proxies=proxy).status_code != 200:
    print "Certification Authority server is unavailable"
    sys.exit(-1)

data = {'Mode': 'newreq',
        'CertRequest': request_data,
        'CertAttrib': 'UserAgent:Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko',
        'ThumbPrint': '',
        'TargetStoreFlags': '0',
        'SaveCert': 'yes'}

certpage = requests.post('http://{}/certsrv/certfnsh.asp'.format(args.authority), data=data, proxies=proxy)
soup = Soup(certpage.content)
certificate_url = soup.findAll('a')[1]['href']
request = requests.get('http://{}/certsrv/{}'.format(args.authority, certificate_url), proxies=proxy)

if request.status_code == 200:
    certificate = request.content
    with open(args.certificate) as cert:
        cert.write(certificate)
else:
    print "Bad certificate url"
    sys.exit(-1)
