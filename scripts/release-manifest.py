"""Generate release metadata from a real ISO; optional detached GPG signature."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
from urllib.parse import urlsplit

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('iso',type=Path)
    parser.add_argument('--url',required=True,help='Actual HTTPS download location')
    parser.add_argument('--version',default='0.5.0')
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--sign-key',help='Existing GPG key fingerprint; private keys are never copied')
    args=parser.parse_args()
    url=urlsplit(args.url)
    if url.scheme!='https' or not url.hostname or url.username or url.password:
        parser.error('An HTTPS release URL without credentials is required')
    digest=hashlib.sha256()
    with args.iso.open('rb') as stream:
        while chunk:=stream.read(4*1024*1024): digest.update(chunk)
    data={'schema_version':1,'version':args.version,'os_version':'0.5','release':'Android Runtime',
          'architecture':'amd64','artifact':{'name':args.iso.name,'bytes':args.iso.stat().st_size,
          'sha256':digest.hexdigest(),'url':args.url},'automatic_install':False}
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    if args.sign_key:
        subprocess.run(['gpg','--local-user',args.sign_key,'--armor','--detach-sign',str(args.output)],check=True)

if __name__=='__main__': main()
