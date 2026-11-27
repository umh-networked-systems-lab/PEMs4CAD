"""
pems.py -- Python translation of the MATLAB perception error model (PEM) functions:

    validateInputs                -> validate_inputs
    getObjectDetectionProbability -> get_object_detection_probability
    getPositionEstimationError    -> get_position_estimation_error
    getHeadingEstimationError     -> get_heading_estimation_error
    getExistenceProbability       -> get_existence_probability

Requires: numpy
"""

import numpy as np

# Random number generator (equivalent of MATLAB's rand / randn).
# Call set_seed() for "rng('shuffle')" behaviour, or set_seed(42) for reproducibility.
_rng = np.random.default_rng()


def set_seed(seed=None):
    """Re-seed the module's random generator. seed=None -> seeded from OS entropy (like rng('shuffle'))."""
    global _rng
    _rng = np.random.default_rng(seed)


def rand():
    """Uniform random number in [0, 1) (MATLAB rand())."""
    return _rng.random()


def randn():
    """Standard normal random number (MATLAB randn())."""
    return _rng.standard_normal()


class PEMsError(ValueError):
    """ValueError carrying a MATLAB-style error identifier (e.g. 'validateInputs:outOfDomain')."""

    def __init__(self, identifier, message):
        super().__init__(f"{identifier}: {message}")
        self.identifier = identifier


def _is_real_numeric(x):
    """MATLAB-like isnumeric & isreal (booleans, strings and complex numbers are rejected)."""
    if isinstance(x, (bool, np.bool_)):
        return False
    try:
        return np.asarray(x).dtype.kind in "iuf"
    except Exception:
        return False


def _out(x):
    """Return a plain Python float for scalar results, an ndarray otherwise."""
    x = np.asarray(x, dtype=float)
    return float(x) if x.ndim == 0 else x


# ----------------------------------------------------------------------------
# validateInputs
# ----------------------------------------------------------------------------
def validate_inputs(lidar_type, perception_stage, d, theta, D_max):
    """Validate lidar type, perception stage and (d, theta) domain.

    d     : distance in meters (scalar or array)
    theta : angle in degrees (scalar or array, same size as d, or one of them scalar)
    D_max : maximum distance (m) for angles close to the x-axis
    """
    if D_max is None:
        raise PEMsError("validateInputs:missingInput",
                        "D_max must be provided as the fifth input.")
    if (not _is_real_numeric(D_max) or np.size(D_max) != 1
            or not np.isfinite(D_max) or D_max <= 0):
        raise PEMsError("validateInputs:badDmax",
                        "D_max must be a positive, finite, real scalar.")

    # 1) lidar_type
    if lidar_type not in ("OS2-128", "OS2-64", "OS1-64"):
        raise PEMsError("validateInputs:notSupported",
                        f"Lidar type '{lidar_type}': not supported.")

    # 2) perception_stage
    if perception_stage not in ("detection", "validation"):
        raise PEMsError("validateInputs:badStage",
                        f"perception_stage must be 'detection' or 'validation' "
                        f"(got '{perception_stage}').")

    # 3) d and theta
    if (not _is_real_numeric(d) or not _is_real_numeric(theta)
            or not np.all(np.isfinite(np.asarray(d, dtype=float)))
            or not np.all(np.isfinite(np.asarray(theta, dtype=float)))):
        raise PEMsError("validateInputs:badNumeric",
                        "d and theta must be real, finite numeric values.")
    d = np.asarray(d, dtype=float)
    theta = np.asarray(theta, dtype=float)
    if d.size != 1 and theta.size != 1 and d.shape != theta.shape:
        raise PEMsError("validateInputs:sizeMismatch",
                        "d and theta must be the same size (or one of them scalar).")
    if np.any(d < 0):
        raise PEMsError("validateInputs:negativeD", "d must be non-negative.")

    # Fold the angle into [0, 180)
    th = np.mod(theta, 180)

    # Domain limit D_lim(theta)
    D_lim = np.where((th < 15) | (th >= 165), float(D_max),            # [0,15) U [165,180)
            np.where(((th >= 15) & (th < 45)) | ((th >= 135) & (th < 165)),
                     50.0,                                             # [15,45) U [135,165)
                     20.0))                                            # [45, 135)

    if np.any(d > D_lim):   # broadcasting handles scalar/array mix
        raise PEMsError("validateInputs:outOfDomain",
                        "d exceeds the allowed domain D_lim(theta).")


# ----------------------------------------------------------------------------
# getObjectDetectionProbability
# ----------------------------------------------------------------------------
def get_object_detection_probability(lidar_type, perception_stage, d, theta):
    """Probability that the target object is detected."""
    D_max = 250  # meters
    validate_inputs(lidar_type, perception_stage, d, theta, D_max)
    d = np.asarray(d, dtype=float)

    if lidar_type == "OS2-128":
        if perception_stage == "detection":
            prob = np.exp(-(0.0057 * d) ** 7.05)
        else:  # validation
            prob = np.exp(-(0.0081 * d) ** 9.65)
    elif lidar_type == "OS2-64":
        if perception_stage == "detection":
            prob = np.exp(-(0.0079 * d) ** 6.05)
        else:  # validation
            prob = np.exp(-(0.0113 * d) ** 6.1)
    elif lidar_type == "OS1-64":
        if perception_stage == "detection":
            prob = np.exp(-(0.0145 * d) ** 7.1)
        else:  # validation
            prob = np.exp(-(0.018 * d) ** 4.8)

    return _out(prob)


# ----------------------------------------------------------------------------
# getPositionEstimationError
# ----------------------------------------------------------------------------
def get_position_estimation_error(lidar_type, perception_stage, d, theta):
    """Sample (x_error, y_error) in meters for a detected object."""
    d_in = d
    d = np.asarray(d, dtype=float)

    with np.errstate(over="ignore"):   # exp() overflow -> inf, like MATLAB
        if lidar_type == "OS2-128":
            if perception_stage == "detection":
                D_max = 240
                x_mean = -0.71 + np.exp((0.0051 * d) ** 10)
                x_std = -0.9137 + np.exp((0.004486 * d) ** 6.108)
                y_mean = 0.0005 * d + 0.0335
                y_std = 0 * d + 0.0988
            else:  # validation
                D_max = 170
                x_mean = 0 * d + 0.3
                x_std = 0 * d + 0.0871
                y_mean = 0.0005 * d + 0.0318
                y_std = 0.0008 * d + 0.0296
        elif lidar_type == "OS2-64":
            if perception_stage == "detection":
                D_max = 190
                x_mean = -0.3164 + np.exp((0.0012 * d) ** 1.3490)
                x_std = -0.8982 + np.exp((0.0071 * d) ** 23.8104)
                y_mean = 0.0008 * d + 0.0129
                y_std = 0.0015 * d + -0.0103
            else:  # validation
                D_max = 160
                x_mean = -0.0003 * d + 0.7027
                x_std = 0.0002 * d + 0.0876
                y_mean = 0.0008 * d + 0.0123
                y_std = 0.0009 * d + 0.0188
        elif lidar_type == "OS1-64":
            if perception_stage == "detection":
                D_max = 120
                x_mean = -0.2972 + np.exp((0.0012 * d) ** 15.8399)
                x_std = -0.9369 + np.exp((0.0017 * d) ** 1.3642)
                y_mean = 0.0009 * d + 0.0136
                y_std = 0.0015 * d + 0.0050
            else:  # validation
                D_max = 100
                x_mean = 0.0017 * d + 0.6516
                x_std = -0.0003 * d + 0.0868
                y_mean = 0.0010 * d + 0.0120
                y_std = 0.0008 * d + 0.0237
        else:
            raise PEMsError("validateInputs:notSupported",
                            f"Lidar type '{lidar_type}': not supported.")

        # Make sure that domain is ok
        validate_inputs(lidar_type, perception_stage, d_in, theta, D_max)

        # Sample values from Gaussian distribution
        x_error = np.abs(x_mean + x_std * randn())
        y_error = np.abs(y_mean + y_std * randn())

    # Assign a random sign (+1 or -1 with equal probability)
    if rand() < 0.5:
        x_error = -x_error
    if rand() < 0.5:
        y_error = -y_error

    return _out(x_error), _out(y_error)


# ----------------------------------------------------------------------------
# getHeadingEstimationError
# ----------------------------------------------------------------------------
def get_heading_estimation_error(lidar_type, perception_stage, d, theta):
    """Sample heading error in degrees for a detected object."""
    d_in = d
    d = np.asarray(d, dtype=float)

    with np.errstate(over="ignore"):   # exp() overflow -> inf, like MATLAB
        if lidar_type == "OS2-128":
            if perception_stage == "detection":
                D_max = 240
                mu = 0.6258 + np.exp((0.0063 * d) ** 2.2688)
                sigma = 0.0137 + np.exp((0.0082 * d) ** 2.3423)
            else:  # validation
                D_max = 170
                mu = 0.5632 + np.exp((0.0042 * d) ** 1.7398)
                sigma = 0.1008 + np.exp((0.0064 * d) ** 1.9705)
        elif lidar_type == "OS2-64":
            if perception_stage == "detection":
                D_max = 190
                mu = 1.1403 + np.exp((0.0074 * d) ** 215.8726)
                sigma = 0.6499 + np.exp((0.0075 * d) ** 125.0842)
            else:  # validation
                D_max = 160
                mu = 0.5290 + np.exp((0.0081 * d) ** 1.0384)
                sigma = -0.3466 + np.exp((0.0097 * d) ** 0.4994)
        elif lidar_type == "OS1-64":
            if perception_stage == "detection":
                D_max = 120
                mu = 0.8533 + np.exp((0.0096 * d) ** 1.9933)
                sigma = -0.2651 + np.exp((0.0133 * d) ** 0.9798)
            else:  # validation
                D_max = 100
                mu = 1.0038 + np.exp((0.0133 * d) ** 166.8569)
                sigma = -0.49 + np.exp((0.0174 * d) ** 0.6870)
        else:
            raise PEMsError("validateInputs:notSupported",
                            f"Lidar type '{lidar_type}': not supported.")

        # Make sure that domain is ok
        validate_inputs(lidar_type, perception_stage, d_in, theta, D_max)

        # Sample values from Gaussian distribution
        heading_error = np.abs(mu + sigma * randn())

    # Assign a random sign (+1 or -1 with equal probability)
    if rand() < 0.5:
        heading_error = -heading_error

    return _out(heading_error)


# ----------------------------------------------------------------------------
# getExistenceProbability
# ----------------------------------------------------------------------------
def get_existence_probability(lidar_type, perception_stage, d, theta):
    """Sample the existence probability (confidence) of a detected object."""
    d_in = d
    d = np.asarray(d, dtype=float)

    if lidar_type == "OS2-128":
        if perception_stage == "detection":
            D_max = 240
            mu = -0.0020 * d + 0.8016
            sigma = 0 * d + 0.0667
        else:  # validation
            D_max = 170
            mu = -0.0016 * d + 0.8403
            sigma = 0.0003 * d + 0.0371
    elif lidar_type == "OS2-64":
        if perception_stage == "detection":
            D_max = 190
            mu = -0.0031 * d + 0.8410
            sigma = 0.0011 * d - 0.0396
        else:  # validation
            D_max = 160
            mu = -0.0021 * d + 0.8096
            sigma = 0.0006 * d + 0.0232
    elif lidar_type == "OS1-64":
        if perception_stage == "detection":
            D_max = 120
            mu = -0.0052 * d + 0.8484
            sigma = 0.0008 * d + 0.0232
        else:  # validation
            D_max = 100
            mu = -0.0058 * d + 0.8607
            sigma = 0.0007 * d + 0.0242
    else:
        raise PEMsError("validateInputs:notSupported",
                        f"Lidar type '{lidar_type}': not supported.")

    # Make sure that domain is ok
    validate_inputs(lidar_type, perception_stage, d_in, theta, D_max)

    # Sample values from Gaussian distribution
    existence_prob = np.minimum(np.abs(mu + sigma * randn()), 1)

    return _out(existence_prob)
