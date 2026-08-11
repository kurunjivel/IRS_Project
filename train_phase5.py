import sys
sys.path.insert(0, '.')
from unittest.mock import MagicMock
sys.modules.setdefault('mysql', MagicMock())
sys.modules.setdefault('mysql.connector', MagicMock())

from services.ml.model_trainer import ModelTrainer
from services.ml.model_evaluator import ModelEvaluator

trainer = ModelTrainer()
report = trainer.train()
print("Best model:", report.best_model_name)
print()
tbl = report.comparison_table()
tbl['Selected'] = tbl['Selected'].str.replace('\u2713', 'YES')
print(tbl.to_string(index=False))
print()

evaluator = ModelEvaluator()
for r in report.all_results:
    r.pipeline.fit(report.split.X_train, report.split.y_train)
    ev = evaluator.evaluate(r.pipeline, report.split)
    print(ev.summary())
    print()
