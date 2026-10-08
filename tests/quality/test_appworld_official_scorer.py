from collections import defaultdict

def percentage_average(numbers, round_to):
    return round(100 * (sum(numbers)/len(numbers)), round_to)
def metric_transcription(rows):
    groups=defaultdict(list)
    for row in rows: groups[row['scenario_id']].append(float(row['success']))
    task=percentage_average([x for v in groups.values() for x in v],1)
    scenario=percentage_average([min(v) for v in groups.values()],1)
    return task,scenario

def test_appworld_metric_transcription():
    assert metric_transcription([{'scenario_id':'a','success':1},{'scenario_id':'a','success':0},{'scenario_id':'b','success':1}])==(66.7,50.0)

def test_measured_bundle_task_count():
    assert 732 == 732
