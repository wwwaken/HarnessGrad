"""Complete-manifest pass^k reporting, explicitly selected by VERIFY.trial_protocol.

This report is additional to legacy run_reward. Missing/invalid trials never become
zero or a smaller denominator. A complete report requires every planned binary result.
"""
from __future__ import annotations
import hashlib
import json
import math
from pathlib import Path



def protocol_for(tasks, verifiers, trials):
    specs = [(verifiers.get(t['task_id']) or {}).get('trial_protocol') for t in tasks]
    if not any(s is not None for s in specs):
        return None
    if not specs or any(s != specs[0] for s in specs):
        raise ValueError('a repeated-trial evaluation requires one explicit protocol for every task')
    from data.scaffolds.runtime_extensions import validate_trials
    spec=specs[0];validate_trials(spec)
    if trials != spec['trials']:
        raise ValueError('requested trials differs from trial_protocol.trials')
    ids=[t['task_id'] for t in tasks]
    if len(set(ids)) != len(ids):
        raise ValueError('duplicate task IDs in repeated-trial manifest')
    return spec


def aggregate(manifest, rows, ks, *, groups=None):
    expected={(r['task_id'],r['trial_id']):r for r in manifest}
    if not manifest or len(expected)!=len(manifest):
        raise ValueError('empty or duplicate trial manifest')
    seen={}
    for row in rows:
        key=(row['task_id'],row['trial_id'])
        if key not in expected or key in seen:
            raise ValueError('unexpected or duplicate trial result')
        if row.get('seed') != expected[key].get('seed'):
            raise ValueError('trial result seed differs from manifest')
        seen[key]=row
    missing=[list(k) for k in expected if k not in seen]
    invalid=[list(k) for k,r in seen.items() if r.get('status')!='measured'
             or type(r.get('score')) not in (int,float) or r['score'] not in (0,1)]
    tasks=sorted({k[0] for k in expected})
    sizes={t:sum(1 for k in expected if k[0]==t) for t in tasks}
    if not ks or any(type(k) is not int or k<1 or any(k>n for n in sizes.values()) for k in ks):
        raise ValueError('pass^k requires positive k <= planned trials for every task')
    out={'schema':'harnessgrad.repeated-trials.v1','metric':'pass^k',
         'manifest':manifest,'manifest_sha256':hashlib.sha256(json.dumps(manifest,sort_keys=True).encode()).hexdigest(),
         'results':[seen[k] for k in expected if k in seen], 'missing':missing,'invalid':invalid,
         'complete':not missing and not invalid,'metrics':None,'per_task':None}
    if not out['complete']:
        return out
    per_task={}
    for task in tasks:
        n=sizes[task];successes=sum(r['score']==1 for k,r in seen.items() if k[0]==task)
        per_task[task]={str(k):math.comb(successes,k)/math.comb(n,k) if successes>=k else 0.0 for k in ks}
    out.update(per_task=per_task,metrics={str(k):sum(per_task[t][str(k)] for t in tasks)/len(tasks) for k in ks})
    if groups is not None:
        if set(groups)!=set(tasks):raise ValueError('groups must cover exactly the manifest tasks')
        out['groups']={group:{str(k):sum(per_task[t][str(k)] for t in tasks if groups[t]==group)
                                     /sum(groups[t]==group for t in tasks) for k in ks}
                       for group in sorted(set(groups.values()))}
    return out


def result_row(result, plan, provider_failure=None):
    verdict=result.get('verdict') or {}
    score=verdict.get('score',1.0 if verdict.get('passed') else 0.0)
    invalid=result.get('invalid') or verdict.get('unmeasured') or provider_failure
    # Explicit signal/timeout records remain distinct from measured benchmark failure.
    from eval.observe.tracing import process_outcome
    outcome=process_outcome(result.get('exit_code'),result.get('stderr'),wrapper=bool(result.get('sandbox')))
    if outcome in ('stopped_by_signal','relayed_signal','timeout'):
        invalid=invalid or outcome
    return {**plan,'status':'unmeasured' if invalid else 'measured',
            'score':None if invalid else score,'reason':invalid,
            'runtime_services':result.get('runtime_services'), 'judge':verdict.get('judge')}


def persist(root, report):
    if root is None:return
    root=Path(root);root.mkdir(parents=True,exist_ok=True)
    # One run/round/harness owns its directory; write atomically without replacing a
    # previously completed report. Partial updates belong to progress records.
    path=root/'repeated-trials.json'
    with path.open('x') as stream:json.dump(report,stream,ensure_ascii=False,indent=2)
