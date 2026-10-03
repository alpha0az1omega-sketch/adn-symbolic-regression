# RESULTS

All runs executed on **Termux, Android**, on a mid-range phone.

## Environment

- Platform: Android (Termux)
- Python: 3.13.13
- NumPy: 2.4.4
- SymPy: 1.14.0

## Test 1 — Harmonic target

**Target:** `y = x·sin(x)`
**Discovered:** `y = x*sin(x)`

| Metric | Value |
|---|---|
| MSE | 5.36e-33 |
| Terms | 1 |
| Time | 18.0 ms |
| Library size | 53 |

Result: **exact recovery**.

## Test 2 — Third Law of Kepler

**Target:** `T = a^(3/2)`
**Discovered:** `y = a**(3/2)`

| Metric | Value |
|---|---|
| MSE | 4.77e-31 |
| Terms | 1 |
| Time | 17.8 ms |
| Library size | 55 |

Result: **exact recovery** of Kepler's Third Law.

## Test 3 — Newton's law of gravitation

**Target:** `F = m1·m2/r²`
**Discovered:** 6-term approximation

| Metric | Value |
|---|---|
| MSE | 1.615e+00 |
| Terms | 6 |
| Time | 63.8 ms |

Reason for failure: the library only generates *pairwise* products.
`(m1·m2)·(1/r²)` is a triple product and is not present.

## Test 4 — Radioactive decay

**Target:** `N = exp(-t/2)`
**Discovered:** 6-term approximation

| Metric | Value |
|---|---|
| MSE | 6.014e-06 |
| Terms | 6 |
| Time | 10.0 ms |

Reason for failure: the library has `exp(-t)` but not `exp(-t/2)`.

## Summary

| Target | Exact | MSE | Time |
|---|---|---|---|
| harmonique | yes | 5.36e-33 | 18 ms |
| kepler | yes | 4.77e-31 | 18 ms |
| gravite | no | 1.6 | 64 ms |
| radioactif | no | 6e-6 | 10 ms |

**Success rate: 2/4 on known targets.**

This is the expected behavior of a minimal symbolic regression engine.

## Next steps

- Add fractional exponents: `exp(-t/2)`
- Add triple products: `(a*b)*c`
- Increase max k beyond 6
- Enrich the library
