import json
from app.services import backtest_service, combination_engine, engine_data

bundle = engine_data.load_backtest_bundle()
targets,_ = backtest_service._targets(bundle)
res = combination_engine.generate_combinations(
    targets[0]['snapshot'],
    targets[0]['prior'],
    bundle['indicators'],
    seed=123,
    candidates=2000,
    sampling='uniform',
    count=5,
    use_individual=False,
    use_profiles=False,
    use_associations=True,
)
for c in res['combinations']:
    print(c['numbers'], c['stars'], c['score'])
    for a in c['associations'][:10]:
        print('  ', a)
    print()
