import sys
import os
sys.path.append(os.getcwd())
import models
from database import engine, SessionLocal
models.Base.metadata.create_all(bind=engine)
db = SessionLocal()

dummy_names = {
    'PT-042': 'Rajesh Kumar',
    'PT-045': 'Sunil Verma',
    'PT-103': 'Ananya Das',
    'PT-001': 'Priya Singh',
    'PT-01': 'Mohan Nair',
    'PT-NEW-001': 'Deepa Patel',
    'PT-Ramesh-001': 'Ramesh Sharma',
}

for p in db.query(models.Patient).all():
    if not p.name or p.name.strip() == '' or p.name == 'Unknown' or p.name.startswith('Patient '):
        p.name = dummy_names.get(p.id, f"Patient {p.id.split('-')[-1]}")
        db.add(p)

db.commit()
print('Names updated!')
