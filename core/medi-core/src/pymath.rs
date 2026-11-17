//! Exact copy of the numeric behaviour of Python and NumPy.
//!
//! Why: the Rust engine must give bit-identical results to the Python engine (the oracle). Python's `sum()` uses
//! compensated summation, `round()` rounds twice, `%` takes the divisor's sign, `max`/`min` return the first on ties;
//! NumPy's `mean`/`std` sum pairwise. All of it is here; tests are in `tests/numeric.rs` (with fixtures generated from
//! NumPy). Engine code uses no numeric shortcut outside these helpers.
//!
//! Math functions (exp, log, pow, erf, ...) are called from glibc `libm`: Python's `math` module and NumPy use
//! the same library (verified on this machine: np.exp == math.exp).

mod libm {
    extern "C" {
        pub fn exp(x: f64) -> f64;
        pub fn log(x: f64) -> f64;
        pub fn log1p(x: f64) -> f64;
        pub fn pow(x: f64, y: f64) -> f64;
        pub fn erf(x: f64) -> f64;
        pub fn sqrt(x: f64) -> f64;
        pub fn fmod(x: f64, y: f64) -> f64;
        pub fn floor(x: f64) -> f64;
    }
}

/// The compiler recognises libm calls and rewrites constant-argument ones into "equivalent" expressions: `pow(x, -1.0)` -> `1.0 / x`,
/// `pow(x, 2.0)` -> `x * x`, `pow(x, 0.5)` -> `sqrt` ... glibc `pow` is not always correctly rounded, so these can differ by
/// 1 ulp (seen in the D5 port: `363.59... ** -1.0` != `1 / 363.59...`). `black_box` hides the argument from the compiler,
/// so the call really goes to glibc, as in Python.
#[inline(always)]
fn bb(x: f64) -> f64 {
    std::hint::black_box(x)
}

#[inline]
pub fn exp(x: f64) -> f64 {
    unsafe { libm::exp(bb(x)) }
}
#[inline]
pub fn log(x: f64) -> f64 {
    unsafe { libm::log(bb(x)) }
}
#[inline]
pub fn log1p(x: f64) -> f64 {
    unsafe { libm::log1p(bb(x)) }
}
/// Python `x ** y` (float) and C `pow`. Do not use `powi`: the result may round differently.
#[inline]
pub fn pow(x: f64, y: f64) -> f64 {
    unsafe { libm::pow(bb(x), bb(y)) }
}
#[inline]
pub fn erf(x: f64) -> f64 {
    unsafe { libm::erf(bb(x)) }
}
#[inline]
pub fn sqrt(x: f64) -> f64 {
    unsafe { libm::sqrt(x) }
}
#[inline]
pub fn floor(x: f64) -> f64 {
    unsafe { libm::floor(x) }
}

/// `math.prod` (left-to-right product, starting from 1).
pub fn prod<I: IntoIterator<Item = f64>>(it: I) -> f64 {
    let mut r = 1.0;
    for x in it {
        r *= x;
    }
    r
}

/// CPython `sum()` (3.12+): Neumaier compensated summation for floats. The start is int 0; the first float becomes `0 + x`.
pub fn sum<I: IntoIterator<Item = f64>>(it: I) -> f64 {
    let mut it = it.into_iter();
    let first = match it.next() {
        None => return 0.0,
        Some(x) => 0.0 + x,
    };
    let (mut hi, mut lo) = (first, 0.0f64);
    for x in it {
        let t = hi + x;
        if hi.abs() >= x.abs() {
            lo += (hi - t) + x;
        } else {
            lo += (x - t) + hi;
        }
        hi = t;
    }
    if lo != 0.0 && lo.is_finite() {
        hi + lo
    } else {
        hi
    }
}

/// Python `round(x)` -> int (ties to even).
#[inline]
pub fn round(x: f64) -> i64 {
    x.round_ties_even() as i64
}

/// Python `int(x)` (truncation toward zero).
#[inline]
pub fn int(x: f64) -> i64 {
    x.trunc() as i64
}

/// Python float `a % b`.
pub fn fmod_py(a: f64, b: f64) -> f64 {
    let mut m = unsafe { libm::fmod(a, b) };
    if m != 0.0 {
        if (b < 0.0) != (m < 0.0) {
            m += b;
        }
    } else {
        m = 0.0f64.copysign(b);
    }
    m
}

/// Python float `a // b`.
pub fn floordiv(a: f64, b: f64) -> f64 {
    let mut m = unsafe { libm::fmod(a, b) };
    let mut div = (a - m) / b;
    if m != 0.0 && (b < 0.0) != (m < 0.0) {
        m += b;
        div -= 1.0;
    }
    let _ = m;
    if div != 0.0 {
        let mut fd = floor(div);
        if div - fd > 0.5 {
            fd += 1.0;
        }
        fd
    } else {
        0.0f64.copysign(a / b)
    }
}

/// Python `max(a, b)`: b only if strictly greater than a.
#[inline]
pub fn max(a: f64, b: f64) -> f64 {
    if b > a {
        b
    } else {
        a
    }
}

/// Python `min(a, b)`: b only if strictly less than a.
#[inline]
pub fn min(a: f64, b: f64) -> f64 {
    if b < a {
        b
    } else {
        a
    }
}

/// Python `max(iterable)`; None if empty.
pub fn max_iter<I: IntoIterator<Item = f64>>(it: I) -> Option<f64> {
    let mut it = it.into_iter();
    let mut m = it.next()?;
    for x in it {
        if x > m {
            m = x;
        }
    }
    Some(m)
}

/// Python `min(iterable)`; None if empty.
pub fn min_iter<I: IntoIterator<Item = f64>>(it: I) -> Option<f64> {
    let mut it = it.into_iter();
    let mut m = it.next()?;
    for x in it {
        if x < m {
            m = x;
        }
    }
    Some(m)
}

// --- NumPy --------------------------------------------------------------------------------------------

/// NumPy `pairwise_sum` (numpy/_core/src/umath/loops_utils.h.src).
fn pairwise_sum(a: &[f64]) -> f64 {
    let n = a.len();
    if n < 8 {
        let mut res = 0.0;
        for &x in a {
            res += x;
        }
        res
    } else if n <= 128 {
        let mut r = [a[0], a[1], a[2], a[3], a[4], a[5], a[6], a[7]];
        let mut i = 8;
        while i < n - (n % 8) {
            for j in 0..8 {
                r[j] += a[i + j];
            }
            i += 8;
        }
        let mut res = ((r[0] + r[1]) + (r[2] + r[3])) + ((r[4] + r[5]) + (r[6] + r[7]));
        while i < n {
            res += a[i];
            i += 1;
        }
        res
    } else {
        let mut n2 = n / 2;
        n2 -= n2 % 8;
        pairwise_sum(&a[..n2]) + pairwise_sum(&a[n2..])
    }
}

/// `np.add.reduce` (1-d, contiguous float64): output starts at the identity (0), the whole array is summed pairwise and added.
pub fn np_sum(a: &[f64]) -> f64 {
    0.0 + pairwise_sum(a)
}

/// `np.mean` (float64). NaN if empty (NumPy warns and returns NaN).
pub fn np_mean(a: &[f64]) -> f64 {
    np_sum(a) / a.len() as f64
}

/// `np.std` (ddof = 0).
pub fn np_std(a: &[f64]) -> f64 {
    let n = a.len() as f64;
    let m = np_sum(a) / n;
    let sq: Vec<f64> = a
        .iter()
        .map(|&x| {
            let d = x - m;
            d * d
        })
        .collect();
    sqrt(np_sum(&sq) / n)
}

/// `np.median`: the middle element for odd length, the mean of the two middle ones for even (`np.mean([lo, hi])`).
pub fn np_median(a: &[f64]) -> f64 {
    let n = a.len();
    assert!(n > 0, "np_median: empty array");
    let mut v = a.to_vec();
    v.sort_by(|x, y| x.partial_cmp(y).expect("np_median: NaN"));
    if n % 2 == 1 {
        v[n / 2]
    } else {
        np_mean(&[v[n / 2 - 1], v[n / 2]])
    }
}
