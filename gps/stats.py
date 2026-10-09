import math
from statistics import mean

import pandas as pd

METHODS = (("analytic", "Аналітичний"), ("numeric", "Чисельний (МНК)"))


def summary(history):
    rows = []
    for key, name in METHODS:
        pts = [h[key] for h in history if h[key]]
        jumps = [math.dist(a, b) * 1000 for a, b in zip(pts, pts[1:])]  # м
        rows.append({
            "Метод": name,
            "Розрахунків": len(pts),
            "Середній стрибок, м": round(mean(jumps), 1) if jumps else None,
            "Максимальний стрибок, м": round(max(jumps), 1) if jumps else None,
        })
    return pd.DataFrame(rows).set_index("Метод")
