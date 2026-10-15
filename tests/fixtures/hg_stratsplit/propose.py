"""Build an append/replacement fragment; never mutate the active registry."""
import json
from pathlib import Path

old = json.loads(Path('registry/proposals/w-stratqa.json').read_text())['next_action_replacement']
start = 'Exact original split membership alignment remains undetermined:'
end = 'without reconstructing unavailable rules.'
a = old.index(start)
b = old.index(end, a) + len(end)
replacement = (
    'Original split membership sources and installed partition coverage are now bound in '
    'registry/w-stratsplit-membership.md and tests/fixtures/hg_stratsplit/binding-summary.json: '
    'the complete generation-pinned ZIP Train multiset equals both the installed 2290 rows '
    '(after literal CSV prefix removal and explicit Boolean-to-Yes/No representation mapping) '
    'and the union of the author repository unofficial train/dev memberships (2061/229). '
    'The ZIP Test membership exactly equals the official evaluator published dummy-submission '
    '490-ID key set. All installed rows are original Train; none are original Test; no installed '
    'row is unaccounted for, while all 490 original Test members are absent from the installed '
    'pool. Do not label the imposed 1520/770 hash split or the author unofficial train/dev '
    'division as original Train/Test evaluation. Two duplicate-content installed rows retain '
    'ambiguous exact qid candidates, with no partition ambiguity or invented tie-break. '
    'Direct landing-page endorsement of the ZIP remains unobserved (HTTP 403); retain the '
    'documented official-evaluator/author-content authority bridge and source namespace distinction.'
)
proposal = {
    'worker': 'w-stratsplit', 'dataset': 'strategyqa', 'blocker': 'dataset-journal-gap',
    'split_outcome': 'found', 'comparability': 'different',
    'source_definition_obligation': 'satisfied_subject_to_parent_review',
    'status_change_requested': None,
    'observed_append': (
        'Source-only w-stratsplit recovered exact memberships and installed partition binding. '
        + replacement + ' Evidence: registry/w-stratsplit-membership.md:1; '
        'tests/fixtures/hg_stratsplit/attempts.jsonl:1; zip-members.json:1; '
        'membership-ids.json:1; installed-row-binding.tsv:1; binding-summary.json:1 '
        '(all fixture basenames under tests/fixtures/hg_stratsplit/). '
        'No scorer/benchmark/model/GPU executes and no diagnostic is authorized.'
    ),
    'next_action_replacement': old[:a] + replacement + old[b:],
    'coverage': json.loads(Path('tests/fixtures/hg_stratsplit/binding-summary.json').read_text()),
    'review_focus': 'Authority bridge in report; direct landing-page ZIP endorsement remains UNKNOWN.',
    'evidence': [
        {'path': 'registry/w-stratsplit-membership.md', 'locator': '# w-stratsplit'},
        {'path': 'tests/fixtures/hg_stratsplit/binding-summary.json', 'locator': 'original_partition_coverage'},
        {'path': 'registry/w-stratsplit-validation.txt', 'locator': 'python3 tools/check_dataset_blockers.py'},
    ],
}
path = Path('registry/proposals/w-stratsplit.json')
path.write_text(json.dumps(proposal, indent=2) + '\n')
print('Created', str(path))
print('Proposed split outcome:', proposal['split_outcome'])
print('Status change requested:', proposal['status_change_requested'])
