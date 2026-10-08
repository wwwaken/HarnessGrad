"""AppWorld refusal for the pinned release.

The official v0.1.3.post1 data bundle is obtainable and decryptable, but the measured
bundle contains 732 task specs. The benchmark documentation describes 750 tasks and the
released evaluator's scenario metric groups tasks by generator id. Without an exact
release/split correspondence, publishing a 732-task curve under AppWorld's 750-task
benchmark name would be a different task set. The protected evaluator and task data are
also encrypted by design; the current bundle is retained outside git for provenance.
"""
from pathlib import Path
KIND='dataset'
DATASET_ROOT=Path('/mnt/20t/xubuqiang/datasets/appworld')
REFUSED=("appworld: the pinned v0.1.3.post1/data-0.1.0 release is not the documented "
"750-task benchmark: decrypting the official 34,280,074-byte bundle produced 14,696 "
"files but only 732 unique task specs. The official evaluator reports task_goal_completion "
"and scenario_goal_completion over its task-to-generator grouping, so silently scoring "
"the 732-task release under the 750-task benchmark name changes the task set. The protected "
"encrypted task/evaluator bundle is unreproducible as the documented full release until matched to an exact published subset; an oracle "
"control and comparable grade cannot be claimed; this adapter refuses rather than reporting "
"a nearby 732-task number.")
def downloads(): return [{'kind':'http','name':'AppWorld data bundle','version':'v0.1.3.post1/data-0.1.0','url':'https://s3.us-west-2.amazonaws.com/appworld.dev/data-0.1.0.bundle','dst':'_src/data-0.1.0.bundle','size':'34280074 bytes','sha256':'fd9f9608c2ec71ed0ac25c3633a738b9129a318a129e31230425b9188e508250','note':'Official encrypted AppWorld data bundle; measured 732 task specs, while the documented benchmark says 750, so the split must be resolved before scoring.'}]
def load(): raise ValueError(REFUSED)
def provision_status(): return {'root':str(DATASET_ROOT),'present':(DATASET_ROOT/'_src'/'data-0.1.0.bundle').is_file(),'tasks':732}
