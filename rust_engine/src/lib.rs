use pyo3::prelude::*;
use rayon::prelude::*;

/// A satellite position at a given time step.
#[pyclass]
#[derive(Clone, Debug)]
struct SatPosition {
    #[pyo3(get)]
    timestamp_ms: i64,
    #[pyo3(get)]
    x_km: f64,
    #[pyo3(get)]
    y_km: f64,
    #[pyo3(get)]
    z_km: f64,
    #[pyo3(get)]
    vx_km_s: f64,
    #[pyo3(get)]
    vy_km_s: f64,
    #[pyo3(get)]
    vz_km_s: f64,
}

#[pymethods]
impl SatPosition {
    #[new]
    fn new(timestamp_ms: i64, x_km: f64, y_km: f64, z_km: f64,
           vx_km_s: f64, vy_km_s: f64, vz_km_s: f64) -> Self {
        Self { timestamp_ms, x_km, y_km, z_km, vx_km_s, vy_km_s, vz_km_s }
    }
}

/// A conjunction (close approach) event detected by the engine.
#[pyclass]
#[derive(Clone, Debug)]
struct ConjunctionResult {
    #[pyo3(get)]
    timestamp_ms: i64,
    #[pyo3(get)]
    sat_a_index: usize,
    #[pyo3(get)]
    sat_b_index: usize,
    #[pyo3(get)]
    distance_km: f64,
    #[pyo3(get)]
    relative_velocity_km_s: f64,
    #[pyo3(get)]
    risk_score: f64,
}

/// Compute Euclidean distance between two 3D points.
#[inline]
fn distance_3d(ax: f64, ay: f64, az: f64, bx: f64, by: f64, bz: f64) -> f64 {
    ((ax - bx).powi(2) + (ay - by).powi(2) + (az - bz).powi(2)).sqrt()
}

/// Compute relative velocity magnitude.
#[inline]
fn relative_velocity(avx: f64, avy: f64, avz: f64, bvx: f64, bvy: f64, bvz: f64) -> f64 {
    ((avx - bvx).powi(2) + (avy - bvy).powi(2) + (avz - bvz).powi(2)).sqrt()
}

/// Calculate risk score (0-100) based on distance and relative velocity.
#[inline]
fn calculate_risk(distance_km: f64, rel_vel: f64) -> f64 {
    let distance_factor = (100.0 * (-distance_km / 2.0).exp()).max(0.0);
    let velocity_factor = (rel_vel / 15.0).min(1.0);
    let score = distance_factor * (0.7 + 0.3 * velocity_factor);
    score.min(100.0).max(0.0)
}

/// Perform collision detection across all satellite pairs using Rayon parallelism.
///
/// Args:
///     positions: Vec of (satellite_index, Vec<SatPosition>) — position arrays per satellite
///     threshold_km: Minimum distance to flag as conjunction
///
/// Returns: Vec of ConjunctionResult for all detected close approaches.
#[pyfunction]
fn detect_collisions_parallel(
    positions: Vec<(usize, Vec<SatPosition>)>,
    threshold_km: f64,
) -> PyResult<Vec<ConjunctionResult>> {
    let n = positions.len();

    // Build pair indices
    let mut pairs: Vec<(usize, usize)> = Vec::new();
    for i in 0..n {
        for j in (i + 1)..n {
            pairs.push((i, j));
        }
    }

    // Parallel conjunction check across all pairs
    let results: Vec<Vec<ConjunctionResult>> = pairs.par_iter().map(|&(i, j)| {
        let (idx_a, ref pos_a) = positions[i];
        let (idx_b, ref pos_b) = positions[j];

        let mut events = Vec::new();
        let len = pos_a.len().min(pos_b.len());

        for k in 0..len {
            let pa = &pos_a[k];
            let pb = &pos_b[k];

            if pa.timestamp_ms != pb.timestamp_ms {
                continue;
            }

            let dist = distance_3d(pa.x_km, pa.y_km, pa.z_km, pb.x_km, pb.y_km, pb.z_km);

            if dist < threshold_km {
                let rel_vel = relative_velocity(
                    pa.vx_km_s, pa.vy_km_s, pa.vz_km_s,
                    pb.vx_km_s, pb.vy_km_s, pb.vz_km_s,
                );
                let risk = calculate_risk(dist, rel_vel);

                events.push(ConjunctionResult {
                    timestamp_ms: pa.timestamp_ms,
                    sat_a_index: idx_a,
                    sat_b_index: idx_b,
                    distance_km: dist,
                    relative_velocity_km_s: rel_vel,
                    risk_score: risk,
                });
            }
        }

        events
    }).collect();

    // Flatten and sort by risk score
    let mut all_events: Vec<ConjunctionResult> = results.into_iter().flatten().collect();
    all_events.sort_by(|a, b| b.risk_score.partial_cmp(&a.risk_score).unwrap());

    Ok(all_events)
}

/// Batch distance computation — returns minimum distance for each pair.
#[pyfunction]
fn batch_min_distances(
    positions: Vec<(usize, Vec<SatPosition>)>,
) -> PyResult<Vec<(usize, usize, f64)>> {
    let n = positions.len();
    let mut pairs: Vec<(usize, usize)> = Vec::new();
    for i in 0..n {
        for j in (i + 1)..n {
            pairs.push((i, j));
        }
    }

    let results: Vec<(usize, usize, f64)> = pairs.par_iter().map(|&(i, j)| {
        let (idx_a, ref pos_a) = positions[i];
        let (idx_b, ref pos_b) = positions[j];
        let len = pos_a.len().min(pos_b.len());

        let mut min_dist = f64::MAX;
        for k in 0..len {
            let dist = distance_3d(
                pos_a[k].x_km, pos_a[k].y_km, pos_a[k].z_km,
                pos_b[k].x_km, pos_b[k].y_km, pos_b[k].z_km,
            );
            if dist < min_dist {
                min_dist = dist;
            }
        }

        (idx_a, idx_b, min_dist)
    }).collect();

    Ok(results)
}

/// Python module definition.
#[pymodule]
fn satellite_rs(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_class::<SatPosition>()?;
    m.add_class::<ConjunctionResult>()?;
    m.add_function(wrap_pyfunction!(detect_collisions_parallel, m)?)?;
    m.add_function(wrap_pyfunction!(batch_min_distances, m)?)?;
    Ok(())
}
