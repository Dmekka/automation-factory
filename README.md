# automation-factory
# Package Sorter

Robotic arm dispatch logic for Smarter Technology's automation factory. Given a package's dimensions and mass, `sort()` returns the name of the stack it should be routed to.

---

## Rules

A package is **bulky** if:
- Its volume (Width × Height × Length) is ≥ 1,000,000 cm³, **or**
- Any single dimension is ≥ 150 cm

A package is **heavy** if:
- Its mass is ≥ 20 kg

| Condition | Stack |
|---|---|
| Neither bulky nor heavy | `STANDARD` |
| Bulky **or** heavy (but not both) | `SPECIAL` |
| Both bulky **and** heavy | `REJECTED` |

---

## Usage

```python
from package_sorter import sort

sort(10, 10, 10, 5)       # → "STANDARD"
sort(200, 10, 10, 5)      # → "SPECIAL"  (bulky by dimension)
sort(100, 100, 100, 10)   # → "SPECIAL"  (bulky by volume)
sort(10, 10, 10, 25)      # → "SPECIAL"  (heavy)
sort(200, 200, 200, 50)   # → "REJECTED" (both)
```

### Signature

```python
def sort(width: float, height: float, length: float, mass: float) -> str:
```

| Parameter | Unit | Constraint |
|---|---|---|
| `width` | cm | > 0 |
| `height` | cm | > 0 |
| `length` | cm | > 0 |
| `mass` | kg | ≥ 0 |

### Exceptions

| Exception | Raised when |
|---|---|
| `TypeError` | Any argument is not a numeric type (`int` or `float`) |
| `ValueError` | Any dimension is ≤ 0, mass is negative, or any value is non-finite (`NaN`, `±inf`) |

---

## Running the Tests

No dependencies beyond the Python standard library.

```bash
python package_sorter.py
```

### Test Classes

| Class | Coverage |
|---|---|
| `TestStandardStack` | Normal packages — not bulky, not heavy |
| `TestBulkyClassification` | Volume threshold, each dimension axis, tricky volume-only cases |
| `TestHeavyClassification` | Mass at, above, and just above the 20 kg threshold |
| `TestRejectedStack` | Both bulky and heavy — all combinations |
| `TestBoundaryValues` | Exact threshold crossings in both directions |
| `TestTypeValidation` | Wrong types: strings, `None`, lists, dicts, complex numbers, wrong arg counts |
| `TestValueValidation` | Bad values: zeros, negatives, `±inf`, `NaN` for each parameter |
| `TestBooleanInputs` | Python's `bool`-as-`int` quirk handled explicitly |

**57 tests, 0 failures.**

---

## Constants

```python
VOLUME_THRESHOLD    = 1_000_000  # cm³
DIMENSION_THRESHOLD = 150        # cm
MASS_THRESHOLD      = 20         # kg
```

All thresholds are defined as named constants at the top of the file for easy modification.
