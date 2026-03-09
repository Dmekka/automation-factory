"""
package_sorter.py
-----------------
Robotic arm dispatch logic for Smarter Technology's automation factory.
Sorts packages into STANDARD, SPECIAL, or REJECTED stacks based on
volume, dimensions, and mass.
"""

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
VOLUME_THRESHOLD = 1_000_000   # cm³
DIMENSION_THRESHOLD = 150      # cm
MASS_THRESHOLD = 20            # kg

STANDARD = "STANDARD"
SPECIAL  = "SPECIAL"
REJECTED = "REJECTED"


# ---------------------------------------------------------------------------
# Core function
# ---------------------------------------------------------------------------
def sort(width: float, height: float, length: float, mass: float) -> str:
    """
    Dispatch a package to the correct stack.

    Parameters
    ----------
    width, height, length : float
        Package dimensions in centimetres (must be > 0).
    mass : float
        Package mass in kilograms (must be >= 0).

    Returns
    -------
    str
        "STANDARD", "SPECIAL", or "REJECTED".

    Raises
    ------
    TypeError
        If any argument is not numeric.
    ValueError
        If any dimension is non-positive or mass is negative.
    """
    # --- Input validation ---------------------------------------------------
    for name, value in [("width", width), ("height", height),
                        ("length", length), ("mass", mass)]:
        if not isinstance(value, (int, float)):
            raise TypeError(f"'{name}' must be numeric, got {type(value).__name__}.")
        if not _is_finite(value):
            raise ValueError(f"'{name}' must be a finite number.")

    if width <= 0 or height <= 0 or length <= 0:
        raise ValueError("All dimensions must be greater than zero.")
    if mass < 0:
        raise ValueError("'mass' cannot be negative.")

    # --- Classification -----------------------------------------------------
    bulky = (
        width * height * length >= VOLUME_THRESHOLD
        or width  >= DIMENSION_THRESHOLD
        or height >= DIMENSION_THRESHOLD
        or length >= DIMENSION_THRESHOLD
    )
    heavy = mass >= MASS_THRESHOLD

    # --- Dispatch -----------------------------------------------------------
    if bulky and heavy:
        return REJECTED
    if bulky or heavy:
        return SPECIAL
    return STANDARD


def _is_finite(value: float) -> bool:
    """Return True if *value* is a real, finite number (not NaN or ±inf)."""
    import math
    return math.isfinite(value)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------
import unittest

# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestStandardStack(unittest.TestCase):
    """Packages that are neither bulky nor heavy -> STANDARD."""

    def test_small_light_package(self):
        self.assertEqual(sort(10, 10, 10, 5), STANDARD)

    def test_dimensions_well_below_all_thresholds(self):
        self.assertEqual(sort(10, 10, 10, 1), STANDARD)

    def test_volume_just_below_threshold(self):
        # 99 * 100 * 100 = 990,000 cm3  <  1,000,000
        self.assertEqual(sort(99, 100, 100, 19), STANDARD)

    def test_volume_fractionally_below_threshold(self):
        # 99.9999 * 100 * 100 = 999,999 cm3
        self.assertEqual(sort(99.9999, 100, 100, 1), STANDARD)

    def test_mass_fractionally_below_threshold(self):
        self.assertEqual(sort(10, 10, 10, 19.9999), STANDARD)

    def test_float_dimensions(self):
        self.assertEqual(sort(10.5, 20.3, 30.1, 5.0), STANDARD)

    def test_zero_mass_accepted(self):
        self.assertEqual(sort(1, 1, 1, 0), STANDARD)

    def test_very_small_dimensions(self):
        self.assertEqual(sort(0.001, 0.001, 0.001, 0), STANDARD)

    def test_int_and_float_inputs_equivalent(self):
        self.assertEqual(sort(10, 10, 10, 5), sort(10.0, 10.0, 10.0, 5.0))


class TestBulkyClassification(unittest.TestCase):
    """Packages that qualify as bulky (volume or dimension threshold) -> SPECIAL."""

    def test_volume_exactly_at_threshold(self):
        # 100 * 100 * 100 = 1,000,000 cm3
        self.assertEqual(sort(100, 100, 100, 10), SPECIAL)

    def test_volume_above_threshold(self):
        self.assertEqual(sort(200, 200, 200, 5), SPECIAL)

    def test_volume_just_above_threshold(self):
        self.assertEqual(sort(100.001, 100, 100, 1), SPECIAL)

    def test_very_flat_package_hits_volume_threshold(self):
        # 1000 * 1000 * 1 = 1,000,000 cm3
        self.assertEqual(sort(1000, 1000, 1, 1), SPECIAL)

    def test_all_dims_below_150_but_bulky_by_volume(self):
        # 149^3 = 3,307,949 cm3 -- each dim < 150 but volume exceeds threshold
        self.assertEqual(sort(149, 149, 149, 1), SPECIAL)

    def test_width_exactly_at_dimension_threshold(self):
        self.assertEqual(sort(150, 10, 10, 5), SPECIAL)

    def test_height_exactly_at_dimension_threshold(self):
        self.assertEqual(sort(10, 150, 10, 5), SPECIAL)

    def test_length_exactly_at_dimension_threshold(self):
        self.assertEqual(sort(10, 10, 150, 5), SPECIAL)

    def test_width_above_dimension_threshold(self):
        self.assertEqual(sort(200, 10, 10, 1), SPECIAL)

    def test_height_above_dimension_threshold(self):
        self.assertEqual(sort(1, 200, 1, 1), SPECIAL)

    def test_length_above_dimension_threshold(self):
        self.assertEqual(sort(1, 1, 200, 1), SPECIAL)

    def test_dimension_just_above_threshold(self):
        self.assertEqual(sort(150.001, 1, 1, 1), SPECIAL)

    def test_bulky_with_zero_mass(self):
        self.assertEqual(sort(150, 1, 1, 0), SPECIAL)


class TestHeavyClassification(unittest.TestCase):
    """Packages that qualify as heavy (mass threshold) -> SPECIAL."""

    def test_mass_exactly_at_threshold(self):
        self.assertEqual(sort(10, 10, 10, 20), SPECIAL)

    def test_mass_above_threshold(self):
        self.assertEqual(sort(10, 10, 10, 100), SPECIAL)

    def test_mass_just_above_threshold(self):
        self.assertEqual(sort(1, 1, 1, 20.001), SPECIAL)


class TestRejectedStack(unittest.TestCase):
    """Packages that are both bulky AND heavy -> REJECTED."""

    def test_volume_threshold_and_mass_threshold(self):
        self.assertEqual(sort(100, 100, 100, 20), REJECTED)

    def test_volume_over_and_mass_over(self):
        self.assertEqual(sort(200, 200, 200, 50), REJECTED)

    def test_dimension_threshold_and_mass_over(self):
        self.assertEqual(sort(150, 10, 10, 25), REJECTED)

    def test_dimension_threshold_and_mass_threshold(self):
        self.assertEqual(sort(150, 1, 1, 20), REJECTED)

    def test_very_large_values(self):
        self.assertEqual(sort(1e9, 1e9, 1e9, 1e9), REJECTED)


class TestBoundaryValues(unittest.TestCase):
    """Exact threshold crossings and off-by-one checks."""

    def test_volume_one_below_is_standard(self):
        self.assertEqual(sort(99.9999, 100, 100, 1), STANDARD)

    def test_volume_exactly_at_threshold_is_special(self):
        self.assertEqual(sort(100, 100, 100, 10), SPECIAL)

    def test_mass_just_below_is_standard(self):
        self.assertEqual(sort(10, 10, 10, 19.9999), STANDARD)

    def test_mass_exactly_at_threshold_is_special(self):
        self.assertEqual(sort(1, 1, 1, 20), SPECIAL)

    def test_dimension_at_149_not_bulky_by_dimension(self):
        # 149 < 150 and 149^1 volume is tiny -- standard
        self.assertEqual(sort(149, 1, 1, 1), STANDARD)

    def test_dimension_at_150_is_bulky(self):
        self.assertEqual(sort(150, 1, 1, 1), SPECIAL)

    def test_int_float_boundary_equivalence(self):
        self.assertEqual(
            sort(100, 100, 100, 10),
            sort(100.0, 100.0, 100.0, 10.0)
        )


class TestTypeValidation(unittest.TestCase):
    """Non-numeric types should raise TypeError."""

    def test_string_width(self):
        with self.assertRaises(TypeError):
            sort("10", 10, 10, 5)

    def test_numeric_string_width(self):
        with self.assertRaises(TypeError):
            sort("100", 100, 100, 10)

    def test_none_mass(self):
        with self.assertRaises(TypeError):
            sort(10, 10, 10, None)

    def test_list_width(self):
        with self.assertRaises(TypeError):
            sort([10], 10, 10, 5)

    def test_dict_mass(self):
        with self.assertRaises(TypeError):
            sort(10, 10, 10, {"mass": 5})

    def test_complex_number_width(self):
        with self.assertRaises(TypeError):
            sort(10+0j, 10, 10, 5)

    def test_too_few_arguments(self):
        with self.assertRaises(TypeError):
            sort(10, 10, 10)

    def test_too_many_arguments(self):
        with self.assertRaises(TypeError):
            sort(10, 10, 10, 5, 99)


class TestValueValidation(unittest.TestCase):
    """Out-of-range or non-finite values should raise ValueError."""

    def test_zero_width(self):
        with self.assertRaises(ValueError):
            sort(0, 10, 10, 5)

    def test_zero_height(self):
        with self.assertRaises(ValueError):
            sort(10, 0, 10, 5)

    def test_zero_length(self):
        with self.assertRaises(ValueError):
            sort(10, 10, 0, 5)

    def test_negative_width(self):
        with self.assertRaises(ValueError):
            sort(-5, 10, 10, 5)

    def test_negative_mass(self):
        with self.assertRaises(ValueError):
            sort(10, 10, 10, -1)

    def test_positive_inf_dimension(self):
        with self.assertRaises(ValueError):
            sort(float("inf"), 10, 10, 5)

    def test_negative_inf_dimension(self):
        with self.assertRaises(ValueError):
            sort(float("-inf"), 10, 10, 5)

    def test_positive_inf_mass(self):
        with self.assertRaises(ValueError):
            sort(10, 10, 10, float("inf"))

    def test_nan_mass(self):
        with self.assertRaises(ValueError):
            sort(10, 10, 10, float("nan"))

    def test_nan_dimension(self):
        with self.assertRaises(ValueError):
            sort(float("nan"), 10, 10, 5)


class TestBooleanInputs(unittest.TestCase):
    """
    bool is a subclass of int in Python.
    Verifies it is handled predictably rather than silently misclassified.
    """

    def test_false_as_dimension_raises_value_error(self):
        # False == 0, which is an invalid (non-positive) dimension
        with self.assertRaises(ValueError):
            sort(False, 10, 10, 5)

    def test_true_as_mass_treated_as_1kg(self):
        # True == 1, well below the 20 kg threshold
        self.assertEqual(sort(10, 10, 10, True), STANDARD)

# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
ALL_TEST_CLASSES = [
    TestStandardStack,
    TestBulkyClassification,
    TestHeavyClassification,
    TestRejectedStack,
    TestBoundaryValues,
    TestTypeValidation,
    TestValueValidation,
    TestBooleanInputs,
]


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    # unittest.main(verbosity=2)
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    for cls in ALL_TEST_CLASSES:
        suite.addTests(loader.loadTestsFromTestCase(cls))
    unittest.TextTestRunner(verbosity=2).run(suite)
