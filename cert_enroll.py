# -*- coding: utf-8 -*-
import argparse
import requests
import sys
import os
from lxml import html

parser = argparse.ArgumentParser()
parser.add_argument('-ca', '--authority', help='Address of your MS Certification Authority', required=True)
parser.add_argument('-r', '--request', help='Input request file', required=True)
parser.add_argument('-c', '--certificate', help='Output certificate filename', required=True)
parser.add_argument('-p', '--proxy', help='Proxy with port without protocol')
parser.add_argument('--chain', action='store_true', help='Get p7b chain')
parser.add_argument('--base64', action='store_true', help='Get base64 encoded certificate or p7b chain')
parser.add_argument('--secured', action='store_true',
                    help='Use this option if your CA is secured (using https potocol)')
args = parser.parse_args()
proxy = None
request_data = []

if os.path.isfile(args.request):
    with open(args.request) as req_file:
        request_data = [req_file.read()]
elif os.path.isdir(args.request):
    for req_file in os.listdir(args.request):
        file_name, extension = os.path.splitext(req_file)
        if extension == '.p10':
            with open(req_file) as r_file:
                request_data.append(r_file.read())
else:
    print "Error reading request file(s)"
    sys.exit(1)

if args.proxy:
    proxy = {'https': args.proxy} if args.secured else {'http': args.proxy}
if requests.get('http://{}'.format(args.authority), proxies=proxy).status_code != 200:
    print "Certification Authority server is unavailable"
    sys.exit(1)

for req in request_data:
    data = {'Mode': 'newreq',
            'CertRequest': req,
            'CertAttrib': 'UserAgent:Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko',
            'ThumbPrint': '',
            'TargetStoreFlags': '0',
            'SaveCert': 'yes'}

    certpage = requests.post('http://{}/certsrv/certfnsh.asp'.format(args.authority), data=data, proxies=proxy)
    page = html.fromstring(certpage.content)
    srv, cert_bin, cert_b64, cert_chain_bin, cert_chain_b64 = page.xpath('//a/@href')

    if args.chain:
        certificate_url = cert_chain_b64 if args.base64 else cert_chain_bin
    else:
        certificate_url = cert_b64 if args.base64 else cert_bin

    request = requests.get('http://{}/certsrv/{}'.format(args.authority, certificate_url), proxies=proxy)

    file_format = 'p7b' if args.chain else 'cer'

    if request.status_code == 200:
        certificate = request.content
        with open('{}.{}'.format(args.certificate, file_format), 'w+') as cert:
            cert.write(certificate)
    else:
        print "Bad certificate url"
        sys.exit(1)
