"""Model monitoring maths (data-free, so it also runs in CI)."""
import numpy as np

import evidence


def test_psi_flags_drift_and_not_noise():
    rng = np.random.default_rng(0)
    base = rng.normal(0, 1, 5000)
    assert evidence._psi(base, rng.normal(0, 1, 5000)) < evidence.PSI_WATCH        # same distribution: stable
    assert evidence._psi(base, rng.normal(1.0, 1, 5000)) > evidence.PSI_BREACH     # shifted by 1 sd: breach
