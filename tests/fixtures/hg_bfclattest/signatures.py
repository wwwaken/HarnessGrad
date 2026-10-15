"""Check DSSE signatures against supplied leaf keys, without claiming Sigstore trust."""
import base64
import json
from pathlib import Path
from collect import command, digest, rows, write_rows

HERE = Path(__file__).parent


def main():
    records = []
    folder = HERE / 'signatures'
    folder.mkdir(exist_ok=True)
    for http in rows(HERE / 'http.jsonl'):
        if http['kind'] != 'pep740' or http['status'] != 200:
            continue
        source = json.loads(Path(http['response']).read_bytes())
        for bi, bundle in enumerate(source['attestation_bundles']):
            for ai, att in enumerate(bundle['attestations']):
                key = f"{http['name']}-{bi}-{ai}"
                certificate = base64.b64decode(att['verification_material']['certificate'])
                statement = base64.b64decode(att['envelope']['statement'])
                signature = base64.b64decode(att['envelope']['signature'])
                pt = b'application/vnd.in-toto+json'
                pae = b'DSSEv1 ' + str(len(pt)).encode() + b' ' + pt + b' ' + str(len(statement)).encode() + b' ' + statement
                artifacts = {}
                for suffix, data in [('der', certificate), ('statement.json', statement), ('sig', signature), ('pae', pae)]:
                    p = folder / (key + '.' + suffix)
                    p.write_bytes(data)
                    artifacts[suffix] = {'path': str(p), **digest(data)}
                cert_path = artifacts['der']['path']
                text = command(['openssl', 'x509', '-inform', 'DER', '-in', cert_path, '-text', '-noout'])
                pubkey = command(['openssl', 'x509', '-inform', 'DER', '-in', cert_path, '-pubkey', '-noout'])
                key_path = folder / (key + '.pub.pem')
                key_path.write_text(pubkey['stdout'])
                verify = command(['openssl', 'dgst', '-sha256', '-verify', str(key_path),
                                  '-signature', artifacts['sig']['path'], artifacts['pae']['path']])
                records.append({'name': http['name'], 'filename': http['filename'],
                    'archive_sha256': http['archive_sha256'], 'artifacts': artifacts,
                    'publisher': bundle['publisher'], 'certificate_text': text, 'public_key': pubkey,
                    'signature_verification': verify,
                    'state': 'FOUND' if verify['returncode'] == 0 else 'UNKNOWN',
                    'scope': 'DSSE payload signature with supplied leaf key only',
                    'fulcio_chain_rekor_trust_and_publisher_policy': 'UNKNOWN not verified',
                    'exact_build_attestation': 'UNKNOWN publish predicate is not complete compiled build provenance'})
    write_rows(HERE / 'signatures.jsonl', records)
    print(json.dumps({'dsse_signatures_checked': len(records),
        'verified_with_supplied_leaf': sum(r['signature_verification']['returncode'] == 0 for r in records),
        'trusted_sigstore_verifications': 0}, sort_keys=True))


if __name__ == '__main__':
    main()
