"""Enrich the existing custody table and gap rows, preserving prior measurements."""
from collections import Counter
import json
from pathlib import Path
from collect import digest, rows, write_rows

HERE = Path(__file__).parent
RUNTIME = HERE.parent / 'hg_bfclrt'
ROOT = Path.cwd()
MARKER = '\n## w-bfclattest: exact-byte attestations, static children and scoped notices\n'


def rel(p):
    p = Path(p)
    return str(p.relative_to(ROOT)) if p.is_absolute() and p.is_relative_to(ROOT) else str(p)


def cited(path):
    return [(r, f'{rel(path)}:{i}') for i, r in enumerate(rows(path), 1)]


def main():
    archives = cited(RUNTIME / 'w-bfclmem-archives.jsonl')
    http = {(r['filename'], r['kind']): (r, c) for r, c in cited(HERE / 'http.jsonl')}
    arc_checks = {r['filename']: (r, c) for r, c in cited(HERE / 'archives.jsonl')}
    license_rows = cited(RUNTIME / 'w-bfclmem-licenses.jsonl')
    natives = [x for p in sorted(RUNTIME.glob('w-bfclmem-native-*.jsonl')) for x in cited(p)]
    native_by_cite = {c: n for n, c in natives}
    native_by_member = {(n['archive'], n['member']): (n, c) for n, c in natives}
    signatures = {r['name']: (r, c) for r, c in cited(HERE / 'signatures.jsonl')}
    system = {r['needed']: (r, c) for r, c in cited(HERE / 'system.jsonl')}
    publisher = {r['repository']: (r, c) for r, c in cited(HERE / 'publisher.jsonl') if 'license_text' in r}
    archive_by_filename = {a['filename']: a for a, _ in archives}

    def notice(archive, member):
        texts = [{'evidence': c, 'path': r['copy'], 'sha256': r['sha256'], 'bytes': r['bytes'],
                  'license_member': r['member'], 'scope': 'parent package text travels in this exact wheel'}
                 for r, c in license_rows if r['archive'] == archive]
        result = {'state': 'FOUND' if texts else 'ABSENT', 'texts': texts,
            'packaged_scope': f'all named LICENSE/LICENCE/NOTICE/COPYING/AUTHORS members in {archive}',
            'complete_compiled_component_licenses': 'UNKNOWN complete build-input inventory not attested'}
        if member.startswith('numpy.libs/'):
            root = next(t for t in texts if t['license_member'] == 'numpy-1.26.4.dist-info/LICENSE.txt')
            section = ('OpenBLAS/LAPACK', 76) if '/libopenblas' in member else (
                ('GCC runtime library', 167) if '/libgfortran' in member else ('libquadmath', 951))
            result.update({'component_scope': 'explicit bundled member glob in parent wheel notice',
                'component_text': {**root, 'section': section[0], 'line': section[1]}})
        if not texts and archive_by_filename[archive]['name'] == 'tokenizers':
            p, c = publisher['huggingface/tokenizers']
            result.update({'state': 'FOUND', 'packaged_text_state': 'ABSENT',
                'external_text': {**p['license_text'], 'evidence': c, 'url': p['url'],
                    'observed_commit': p['observed_commit'],
                    'scope': 'producer v0.23.3 tag text; does not travel in wheel'},
                'exact_wheel_source_commit_binding': 'UNKNOWN tag alone is not compiled source binding'})
        return result

    def attestation(a):
        h, hc = http[(a['filename'], 'pep740')]
        asc, ac = http[(a['filename'], 'asc')]
        state = 'FOUND' if h.get('exact_subject_binding') else ('ABSENT' if h['status'] == 404 else 'UNKNOWN')
        result = {'state': state, 'evidence': hc, 'url': h['url'], 'http_status': h['status'],
            'response_sha256': h['sha256'], 'response_bytes': h['bytes'],
            'response_path': h['response'], 'archive_filename': a['filename'],
            'archive_sha256': a['sha256'], 'archive_bytes': a['bytes'],
            'archive_member_verification': arc_checks[a['filename']][1],
            'detached_signature': {'state': asc['state'], 'evidence': ac, 'url': asc['url'], 'http_status': asc['status']},
            'scope': 'one exact PyPI /integrity/{name}/{version}/{filename}/provenance URL and one exact artifact_url + .asc URL',
            'compiled_build_attestation': 'UNKNOWN publish/v1 has null predicate; no exact CPython/toolchain/flags manifest',
            'other_public_records': 'UNKNOWN unenumerated producer CI/releases/signing endpoints not searched'}
        if h['status'] == 200:
            result['predicate_types'] = [s['statement']['predicateType'] for s in h['statements']]
            result['subjects'] = [s['statement']['subject'] for s in h['statements']]
            result['dsse_leaf_signature_evidence'] = signatures[a['name']][1]
            result['trusted_sigstore_verification'] = 'UNKNOWN chain, Rekor and publisher policy not verified'
            if not h.get('exact_subject_binding'):
                result['mismatch'] = 'same observed digest, different wheel filename/tag ordering; strict filename binding remains UNKNOWN; no different bytes inferred'
        return result

    linked = {}
    for edge, cite in cited(RUNTIME / 'w-bfclmem-links.jsonl'):
        parent = native_by_cite[edge['parent']]
        bundled = [(n, c) for n, c in natives if n['archive'] == parent['archive']
                   and Path(n['member']).name == edge['needed']]
        providers = []
        if bundled:
            for n, c in bundled:
                providers.append({'supply': 'retained wheel member', 'state': 'FOUND',
                    'archive': n['archive'], 'member': n['member'], 'sha256': n['sha256'],
                    'bytes': n['bytes'], 'evidence': c, 'license': notice(n['archive'], n['member'])})
        else:
            sys, sc = system[edge['needed']]
            for candidate in sys['candidates']:
                providers.append({'supply': 'system', 'state': 'FOUND', 'path': candidate['realpath'],
                    'sha256': candidate['sha256'], 'bytes': candidate['bytes'],
                    'retained_elf': candidate['retained_elf'], 'evidence': sc,
                    'licenses': [{'package': o['package'], 'package_info': o['info']['stdout'],
                        'notices': o['notices']} for o in candidate['ownership']]})
        linked.setdefault(edge['parent'], []).append({'needed': edge['needed'],
            'state': 'FOUND' if providers else 'ABSENT', 'prior_evidence': cite,
            'scope': '87 selected wheel ELF members plus enumerated ldconfig x86-64 cache and exact system files',
            'providers': providers, 'per_parent_loader_selection': 'UNKNOWN not executed',
            'dlopen': 'UNKNOWN no complete dynamic-call table or branch execution'})

    gap_path = RUNTIME / 'runtime-gaps-003.jsonl'
    gaps = rows(gap_path)
    assert len(gaps) == 93
    for g in gaps:
        if g['kind'] == 'compiled build identity':
            n = native_by_cite[g['evidence']]
            a = archive_by_filename[n['archive']]
            g.update({'state': 'UNKNOWN exact compiled build; bounded public-record search completed',
                'archive': n['archive'], 'bytes': n['bytes'], 'publish_attestation': attestation(a),
                'license_disposition': notice(n['archive'], n['member']),
                'linked_children': linked.get(g['evidence'], []),
                'dlopen_state': 'UNKNOWN names absent from static tables are not inferred',
                'artifact_to_close': 'Producer-authenticated build manifest naming this exact archive/member digest and CPython build implementation/version/SOABI, source revisions, toolchain/flags, all linked/dlopen inputs and component notices.'})
        elif g['kind'] == 'unresolved linked library':
            old = next(e for e, c in cited(RUNTIME / 'w-bfclmem-links.jsonl') if c == g['evidence'])
            edge = next(e for e in linked[old['parent']] if e['needed'] == g['needed'])
            g.update({'state': 'FOUND static system provider; actual per-parent loader selection UNKNOWN',
                'provider_disposition': edge, 'artifact_to_close': 'Later authorized per-parent loader trace bound to exact parent/provider digests; static SONAME availability does not prove loader selection.'})
    write_rows(gap_path, gaps)

    # Enrich only the first ten established direct archive rows; retain all others.
    gap1 = RUNTIME / 'runtime-gaps-001.jsonl'
    lines = gap1.read_text().splitlines(keepends=True)
    for i in range(10):
        g = json.loads(lines[i])
        a = next(a for a, _ in archives if a['name'] == g['name'])
        g['w_bfclattest_public_record_disposition'] = attestation(a)
        lines[i] = json.dumps(g, sort_keys=True) + '\n'
    gap1.write_text(''.join(lines))

    # Put dispositions in the existing document; supporting files are raw observations.
    doc = Path('registry/w-bfclrt-custody.md')
    text = doc.read_text().split(MARKER)[0]
    out = [MARKER, '\nThe selected scope remains the 95 exact wheels and 87 ELF members of w-bfclmem; all 7,458 member sizes/digests were rechecked without reacquisition (`tests/fixtures/hg_bfclattest/archives.jsonl:1` through `:95`). Prerequisite commit `736afcacdc125457ed77422047f990a4ada359d1` was missing from this assigned base; 143 prerequisite evidence paths were restored byte-for-byte from that object, not merged or measured again (`tests/fixtures/hg_bfclattest/prerequisite.jsonl:1` through `:143`).\n',
        '\nFOUND means observed bytes or an explicitly scoped assertion. ABSENT below means only HTTP 404 at the named exact URL or no matching member in the enumerated archive. UNKNOWN means a fact not established by these observations. No statement asserts global nonexistence of an attestation.\n',
        '\n**Attestation disposition:** before 95 UNKNOWN publication-record searches; after 42 FOUND exact filename+digest publication subjects, 52 ABSENT at the exact PyPI provenance endpoint, 1 UNKNOWN strict filename match (websockets: equal digest, reordered tags). All 95 detached `.asc` URLs returned 404. All 43 returned statements use publish/v1 with a null predicate; complete compiled-build attestations remain 87 UNKNOWN → 87 UNKNOWN. Counts and exact statuses are recomputable from `tests/fixtures/hg_bfclattest/http.jsonl:1` through `:190`; leaf signature checks: `tests/fixtures/hg_bfclattest/signatures.jsonl:1` through `:43`.\n',
        '\n**Linked-child disposition:** before 167 FOUND bundled/mapped candidates and 3 UNKNOWN candidate availability; after 170 FOUND static supply (5 retained-wheel edges, 165 system edges). The 3 formerly unresolved child rows changed to FOUND static system providers. Actual per-parent loader choices remain 170 UNKNOWN → 170 UNKNOWN; dlopen remains UNKNOWN for all 87 parents. Before evidence: `tests/fixtures/hg_bfclrt/w-bfclmem-links.jsonl:1` through `:170`; after: linked_children on `tests/fixtures/hg_bfclrt/runtime-gaps-003.jsonl:1` through `:87`.\n',
        '\n**Licence disposition:** before 86/87 native members had parent-wheel text and tokenizers had no packaged text; after those same 86 parent texts plus 1 FOUND external producer-version text (tokenizers packaged text remains ABSENT). Before 12 unique linked-provider scopes had no per-provider disposition; after 12 FOUND scoped notices (3 bundled NumPy children, 9 system names). Complete compiled/transitive licence coverage remains UNKNOWN: parent terms and SBOM identifiers do not establish all compiled input notices. Before text inventory: `tests/fixtures/hg_bfclrt/w-bfclmem-licenses.jsonl:1` through `:117`; after per-native scope: `tests/fixtures/hg_bfclrt/runtime-gaps-003.jsonl:1` through `:87`, system scope: `tests/fixtures/hg_bfclattest/system.jsonl:1` through `:9`.\n',
        '\n### Exact search commands and boundaries\n',
        '\n`TMPDIR=/tmp/bfclattest-tmp python3 -B tests/fixtures/hg_bfclattest/collect.py http` queried exactly `https://pypi.org/integrity/{name}/{version}/{filename}/provenance` and `{artifact_url}.asc` for each of the 95 enumerated archive rows. Each row of `http.jsonl` stores the exact executed curl argv, exit status, HTTP status, raw response/header paths, byte counts and SHA-256. No alternate wheel/version was downloaded. Producer CI/releases and alternate signing endpoints outside this enumeration remain UNKNOWN. The document does not equate publish attestation, SBOM or compiler comment with an exact compiled-build manifest.\n',
        '\n`TMPDIR=/tmp/bfclattest-tmp python3 -B tests/fixtures/hg_bfclattest/collect.py archives` verified existing archive/member bytes and searched every non-directory member name with `(attest|provenance|build[-_]details|sbom|RECORD\\.(jws|p7s)$)` (case-insensitive). Ten candidates comprise seven retained SBOMs and three OpenAI SDK source filenames containing provenance; the latter are API source, not build records (`tests/fixtures/hg_bfclattest/archives.jsonl:1` through `:95`). SBOMs contain 550 component declarations, not 550 measured build inputs; full component licence texts remain UNKNOWN except separately cited notices (`tests/fixtures/hg_bfclattest/sbom-components.jsonl:1` through `:550`).\n',
        '\n`TMPDIR=/tmp/bfclattest-tmp python3 -B tests/fixtures/hg_bfclattest/collect.py system` records `/sbin/ldconfig -p`, selects exact SONAME rows whose ABI tuple starts `(libc6,x86-64`, then reads exact files, SONAME/version tables, dpkg ownership/version and copyright paths. It neither invokes ldd nor executes/loads wheel ELF code. Provider evidence is static availability; RPATH/RUNPATH, loader namespaces, preload, symbol interposition and unexercised dlopen prevent a claim about actual loader selection. System ELF bytes/readelf outputs are preserved under `/mnt/20t/xubuqiang/hg-work/bfclattest/system/`; hashes and exact commands are in `system.jsonl`.\n',
        '\n`TMPDIR=/tmp/bfclattest-tmp python3 -B tests/fixtures/hg_bfclattest/signatures.py` verifies all 43 DSSE payload signatures with their supplied leaf public keys. Fulcio trust roots/chain, Rekor inclusion/checkpoints and expected publisher policy are not verified; these are UNKNOWN, not implied by `Verified OK`. The records remain FOUND public PyPI objects with measured exact subjects.\n',
        '\n### Per-archive publication and packaged-text table\n\nEach FOUND publication row requires both exact filename and SHA-256 equality. Every archive also has an ABSENT detached signature at its exact `.asc` URL. The HTTP evidence supplies response digest/bytes, exact URL/command/status and retained raw bytes. The archive/member verification supplies the already retained payload location.\n\n| Target (exact filename) | Archive SHA-256; bytes | Publication record disposition; evidence | Version-matched licence/NOTICE text |\n|---|---|---|---|\n']
    for a, ac in archives:
        at = attestation(a)
        h, hc = http[(a['filename'], 'pep740')]
        lc = [c for r, c in license_rows if r['archive'] == a['filename']]
        licence = 'FOUND parent-wheel text: ' + ', '.join(f'`{c}`' for c in lc) if lc else 'ABSENT packaged text in this wheel; full member enumeration cited by archive verification'
        if a['name'] == 'tokenizers':
            licence += '; FOUND external v0.23.3 text: `' + publisher['huggingface/tokenizers'][1] + '`'
        detail = ' same digest, different filename; strict binding UNKNOWN' if h['status'] == 200 and not h.get('exact_subject_binding') else ''
        out.append(f"| `{a['filename']}` | `{a['sha256']}`; {a['bytes']} | **{at['state']}** HTTP {h['status']}{detail}; `{hc}`; response `{h['sha256']}`, {h['bytes']} bytes | {licence} |\n")
    out.append('\n### Per-native build and licence table\n\nAll build rows remain UNKNOWN for a complete compiled build attestation; the publication record is an independent dimension. Each existing gap row now carries exact archive identity, scoped publish disposition, licence text digests/bytes, linked providers and explicit dlopen UNKNOWN. Parent licence text does not assert complete compiled component coverage.\n\n| Exact target member | Member SHA-256; bytes | Compiled build; publication record | Licence scope and canonical gap row |\n|---|---|---|---|\n')
    for i, g in enumerate(gaps[:87], 1):
        n = native_by_cite[g['evidence']]
        lc = g['license_disposition']
        scope = lc.get('component_scope', 'external producer-version text' if 'external_text' in lc else 'parent-package text carried inside exact wheel')
        out.append(f"| `{n['name']}=={n['version']}: {n['member']}` | `{n['sha256']}`; {n['bytes']} | **UNKNOWN** compiled build; **{g['publish_attestation']['state']}** publish subject | **{lc['state']}** {scope}; `tests/fixtures/hg_bfclrt/runtime-gaps-003.jsonl:{i}` |\n")
    out.append('\n### Every static linked child, per parent\n\nFOUND here means the enumerated retained tree supplies that member or the host supplies an observed exact SONAME file. It does not mean the parent loaded it. All actual per-parent selections and dynamic names outside static tables remain UNKNOWN.\n\n| Parent member | DT_NEEDED child | Provider disposition; SHA-256; bytes | Evidence |\n|---|---|---|---|\n')
    for i, g in enumerate(gaps[:87], 1):
        for edge in g['linked_children']:
            for provider in edge['providers']:
                name = provider.get('member', provider.get('path'))
                out.append(f"| `{g['member']}` | `{edge['needed']}` | **FOUND** {provider['supply']}: `{name}`; `{provider['sha256']}`; {provider['bytes']} | `{provider['evidence']}`; `tests/fixtures/hg_bfclrt/runtime-gaps-003.jsonl:{i}` |\n")
    out.append('\n### Every newly scoped linked-provider notice\n\nSystem copyright versions are matched through dpkg ownership of the exact binary and resolved copyright path. libgcc/libstdc++ copyright resolves to gcc-12-base of the same observed source package/version; these notices belong to the system, not the wheel. Referenced common licence texts are retained with individual hashes (`tests/fixtures/hg_bfclattest/common-licenses.jsonl:1` through `:8`).\n\n| Provider | Notice scope; SHA-256; bytes | Exact text and evidence |\n|---|---|---|\n')
    for needed, (sys, sc) in system.items():
        for c in sys['candidates']:
            for o in c['ownership']:
                for n in o['notices']:
                    out.append(f"| `{needed}` | **FOUND** system `{o['info']['stdout'].strip()}`; `{n['sha256']}`; {n['bytes']} | `{rel(n['copy'])}:1`; `{sc}` |\n")
    numpy_notice = next(r for r, c in license_rows if r['member'] == 'numpy-1.26.4.dist-info/LICENSE.txt')
    for name, line in [('libopenblas*.so',76), ('libgfortran*.so',167), ('libquadmath*.so',951)]:
        out.append(f"| `numpy.libs/{name}` | **FOUND** bundled-component section in NumPy 1.26.4 wheel notice; `{numpy_notice['sha256']}`; {numpy_notice['bytes']} | `{numpy_notice['copy']}:{line}` |\n")
    for repository, (r, c) in publisher.items():
        t = r['license_text']
        out.append(f"| `{repository}` at `{r['tag']}` / observed `{r['observed_commit']}` | **FOUND** external producer-version licence; `{t['sha256']}`; {t['bytes']}; not packaged text | `{rel(t['path'])}:1`; `{c}` |\n")
    out.append('\nThe OpenSSL 4.0.3 notice matches the producer-packaged SBOM version; that SBOM declares source digest and flags, but it does not measure the compiled input. Rust SBOM licence expressions are declarations, not retained full licence/NOTICE texts. Complete component coverage and exact build provenance remain UNKNOWN (`tests/fixtures/hg_bfclattest/sbom-components.jsonl:1`; seven raw SBOMs indexed by `archives.jsonl`).\n')
    out.append('\n### Exact changed entries and remaining closing artefacts\n\n`tests/fixtures/hg_bfclrt/runtime-gaps-001.jsonl:1` through `:10` gain only the public-record disposition field, on top of the restored w-bfclmem rows. Its rows 11–996 are preserved byte-for-byte from the prerequisite. `runtime-gaps-002.jsonl` is untouched: its older installed ELF objects are distinct bytes and receive no new wheel-based attestation claim. `tests/fixtures/hg_bfclrt/runtime-gaps-003.jsonl:1` through `:87` retain compiled-build UNKNOWN and gain the measured publication/static-provider/scoped-licence details; rows 88–90 gain FOUND system availability while preserving actual-loader UNKNOWN. Rows 91–93 are preserved. The prior w-bfclmem-links observations are untouched. This section updates the existing per-target record rather than replacing it with a parallel custody document.\n')
    out.append('\nUNKNOWN → single closing artefact: (1) exact compiled build: a producer-authenticated manifest naming this archive/member SHA-256, source commit, CPython build version/SOABI, compiler/flags and compiled inputs; (2) actual linked/dlopen graph: a separately authorized per-parent loader/dlopen trace naming exact parent and child hashes; (3) complete bundled/component licence coverage: an exact-build SBOM-to-full-license/NOTICE bundle covering those input digests; (4) trusted publication identity: a successful Sigstore policy-verification receipt bound to these retained attestations; (5) websockets strict filename mismatch: a producer/PyPI provenance record carrying the retained filename and same observed SHA-256. Public producer records outside the enumerated URLs are unsearched UNKNOWN.\n')
    out.append('\nNo model, GPU, server control, paid endpoint, scorer, dataset run, full-call differential, official execution, production adapter change, registry/journal edit or frozen receipt modification occurred. The blocker remains external/open; no production H0 authorization is proposed. Exact verification output, limits, file sizes and prerequisite-origin review are in `registry/w-bfclattest-validation.txt:1`.\n')
    doc.write_text(text + ''.join(out))
    summary = {'archive_publication': dict(Counter(attestation(a)['state'] for a, _ in archives)),
        'compiled_build_unknown': 87, 'native_members': len(natives),
        'linked_edges': sum(len(v) for v in linked.values()),
        'linked_static_supplies': dict(Counter(p['supply'] for v in linked.values() for e in v for p in e['providers'])),
        'native_license_scopes': dict(Counter(g['license_disposition']['state'] for g in gaps[:87])),
        'actual_loader_and_dlopen': 'UNKNOWN', 'production_authorized': False}
    write_rows(HERE / 'summary.jsonl', [summary])
    print(json.dumps(summary, sort_keys=True))


if __name__ == '__main__':
    main()
