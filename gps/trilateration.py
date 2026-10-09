import numpy as np
from scipy.optimize import least_squares

from .config import MIN_TRIANGLE_AREA_KM2


def analytic(sats, r):
    (x1, y1), (x2, y2), (x3, y3) = sats
    r1, r2, r3 = r

    A = 2 * (x2 - x1)
    B = 2 * (y2 - y1)
    C = r1**2 - r2**2 - x1**2 + x2**2 - y1**2 + y2**2
    D = 2 * (x3 - x2)
    E = 2 * (y3 - y2)
    F = r2**2 - r3**2 - x2**2 + x3**2 - y2**2 + y3**2

    det = E * A - B * D
    if abs(det) < 8 * MIN_TRIANGLE_AREA_KM2:
        return None

    x = (C * E - F * B) / det
    y = (C * D - A * F) / (B * D - A * E)
    return x, y


def numeric(sats, r, start):
    xy = np.asarray(sats, dtype=float)
    r = np.asarray(r, dtype=float)

    def residuals(p):
        return (p[0] - xy[:, 0]) ** 2 + (p[1] - xy[:, 1]) ** 2 - r**2

    res = least_squares(residuals, x0=np.asarray(start, dtype=float), method="lm")
    return (float(res.x[0]), float(res.x[1])) if res.success else None
