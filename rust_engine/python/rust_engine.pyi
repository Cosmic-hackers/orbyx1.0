"""Type stubs for the satellite_rs Rust extension module."""

class SatPosition:
    timestamp_ms: int
    x_km: float
    y_km: float
    z_km: float
    vx_km_s: float
    vy_km_s: float
    vz_km_s: float

    def __init__(
        self,
        timestamp_ms: int,
        x_km: float,
        y_km: float,
        z_km: float,
        vx_km_s: float,
        vy_km_s: float,
        vz_km_s: float,
    ) -> None: ...


class ConjunctionResult:
    timestamp_ms: int
    sat_a_index: int
    sat_b_index: int
    distance_km: float
    relative_velocity_km_s: float
    risk_score: float


def detect_collisions_parallel(
    positions: list[tuple[int, list[SatPosition]]],
    threshold_km: float,
) -> list[ConjunctionResult]: ...


def batch_min_distances(
    positions: list[tuple[int, list[SatPosition]]],
) -> list[tuple[int, int, float]]: ...
