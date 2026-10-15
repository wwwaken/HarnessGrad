#!/usr/bin/env python3
"""Record public response preimages without interpreting provenance claims."""
import hashlib,json,sys,time,urllib.request,urllib.error
from pathlib import Path
ROOT=Path(__file__).resolve().parent

def get(name,url,method="GET",limit=20_000_000):
    if (ROOT/"responses"/(name+".receipt.json")).exists():
        raise SystemExit("Refusing response overwrite")
    req=urllib.request.Request(url,headers={"User-Agent":"HarnessGrad-provenance-audit","Accept":"application/vnd.github+json"},method=method)
    info={"url":url,"method":method,"started_utc":time.strftime("%Y-%m-%dT%H:%M:%SZ",time.gmtime())}
    try:
        opener = urllib.request.build_opener(urllib.request.ProxyHandler({"https":"http://127.0.0.1:17891"})) if name.endswith("-proxy") else urllib.request.build_opener()
        if name.endswith("-proxy"): info["transport_proxy"]="http://127.0.0.1:17891"
        r=opener.open(req,timeout=30)
    except urllib.error.HTTPError as e:
        r=e
    except Exception as e:
        info["error"]=repr(e)
        (ROOT/"responses"/(name+".receipt.json")).write_text(json.dumps(info,indent=2)+"\n")
        print(json.dumps(info));return
    info.update(status=r.status,final_url=r.url)
    headers=str(r.headers).encode()
    body=r.read(limit+1)
    info.update(bytes=len(body),sha256=hashlib.sha256(body).hexdigest(),limit_exceeded=len(body)>limit)
    (ROOT/"responses"/(name+".headers")).write_bytes(headers)
    (ROOT/"responses"/(name+".body")).write_bytes(body)
    (ROOT/"responses"/(name+".receipt.json")).write_text(json.dumps(info,indent=2)+"\n")
    print(json.dumps(info))

if __name__=="__main__":
    get(*sys.argv[1:])
