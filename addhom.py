"""
The return of woody nightshade
"""
from db import db

wood = dict(
    name='Woody nightshade',
    homeopathic=True,
    indications='a wide range of chronic ailments'
    )

db.drugs.insert(wood)
