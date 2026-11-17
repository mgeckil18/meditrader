//! Exact copy of NumPy `default_rng` (PCG64 + SeedSequence) and the distributions we use.
//!
//! Source: numpy v2.4.4 `numpy/random/` (bit_generator.pyx, _pcg64.pyx, src/pcg64/pcg64.h,
//! src/distributions/distributions.c, _generator.pyx, _bounded_integers.pyx.in). The Python engine (sim/rng.py) opens a
//! separate stream per subsystem with `SeedSequence([seed, crc32(name)])`; the same here.
//! Tests: `tests/numeric.rs` (bit for bit, with fixtures generated from NumPy).

mod zig;

use crate::pymath;
use indexmap::IndexMap;
use serde::{Deserialize, Serialize};

const MULT: u128 = (2549297995355413924u128 << 64) | 4865540595714422341u128;

/// PCG64 (XSL-RR 128/64) bit generator, with NumPy's `has_uint32` buffer.
#[derive(Clone, Debug, PartialEq, Eq)]
pub struct Pcg64 {
    pub state: u128,
    pub inc: u128,
    pub has_uint32: bool,
    pub uinteger: u32,
}

impl Pcg64 {
    fn step(&mut self) {
        self.state = self.state.wrapping_mul(MULT).wrapping_add(self.inc);
    }

    pub fn from_seed(initstate: u128, initseq: u128) -> Self {
        let mut r = Pcg64 { state: 0, inc: (initseq << 1) | 1, has_uint32: false, uinteger: 0 };
        r.step();
        r.state = r.state.wrapping_add(initstate);
        r.step();
        r
    }

    /// `PCG64(SeedSequence(entropy))`.
    pub fn from_entropy(entropy: &[u32]) -> Self {
        let w = SeedSequence::new(entropy).generate_state_u64(4);
        Self::from_seed(((w[0] as u128) << 64) | w[1] as u128, ((w[2] as u128) << 64) | w[3] as u128)
    }

    #[inline]
    pub fn next_u64(&mut self) -> u64 {
        self.step();
        let s = self.state;
        let hi = (s >> 64) as u64;
        let lo = s as u64;
        (hi ^ lo).rotate_right((hi >> 58) as u32)
    }

    #[inline]
    pub fn next_u32(&mut self) -> u32 {
        if self.has_uint32 {
            self.has_uint32 = false;
            return self.uinteger;
        }
        let n = self.next_u64();
        self.has_uint32 = true;
        self.uinteger = (n >> 32) as u32;
        n as u32
    }

    #[inline]
    pub fn next_double(&mut self) -> f64 {
        (self.next_u64() >> 11) as f64 * (1.0 / 9007199254740992.0)
    }
}

/// NumPy `SeedSequence` (pool_size 4, no spawn_key).
pub struct SeedSequence {
    pool: [u32; 4],
}

const INIT_A: u32 = 0x43b0d7e5;
const MULT_A: u32 = 0x931e8875;
const INIT_B: u32 = 0x8b51f9dd;
const MULT_B: u32 = 0x58f38ded;
const MIX_MULT_L: u32 = 0xca01f9dd;
const MIX_MULT_R: u32 = 0x4973f715;

fn hashmix(value: u32, hc: &mut u32) -> u32 {
    let mut v = value ^ *hc;
    *hc = hc.wrapping_mul(MULT_A);
    v = v.wrapping_mul(*hc);
    v ^ (v >> 16)
}

fn mix(x: u32, y: u32) -> u32 {
    let r = MIX_MULT_L.wrapping_mul(x).wrapping_sub(MIX_MULT_R.wrapping_mul(y));
    r ^ (r >> 16)
}

impl SeedSequence {
    pub fn new(entropy: &[u32]) -> Self {
        let mut pool = [0u32; 4];
        let mut hc = INIT_A;
        for i in 0..4 {
            pool[i] = hashmix(if i < entropy.len() { entropy[i] } else { 0 }, &mut hc);
        }
        for i_src in 0..4 {
            for i_dst in 0..4 {
                if i_src != i_dst {
                    let h = hashmix(pool[i_src], &mut hc);
                    pool[i_dst] = mix(pool[i_dst], h);
                }
            }
        }
        for &e in entropy.iter().skip(4) {
            for p in pool.iter_mut() {
                let h = hashmix(e, &mut hc);
                *p = mix(*p, h);
            }
        }
        SeedSequence { pool }
    }

    pub fn generate_state_u32(&self, n: usize) -> Vec<u32> {
        let mut hc = INIT_B;
        (0..n)
            .map(|i| {
                let mut d = self.pool[i % 4] ^ hc;
                hc = hc.wrapping_mul(MULT_B);
                d = d.wrapping_mul(hc);
                d ^ (d >> 16)
            })
            .collect()
    }

    pub fn generate_state_u64(&self, n: usize) -> Vec<u64> {
        let w = self.generate_state_u32(2 * n);
        (0..n).map(|i| (w[2 * i] as u64) | ((w[2 * i + 1] as u64) << 32)).collect()
    }
}

/// Turns a Python integer into SeedSequence input (`_int_to_uint32_array`: low word first; 0 -> [0]).
pub fn int_to_u32_words(mut x: u128) -> Vec<u32> {
    if x == 0 {
        return vec![0];
    }
    let mut out = Vec::new();
    while x > 0 {
        out.push(x as u32);
        x >>= 32;
    }
    out
}

/// Counterpart of `np.random.Generator` (only the methods we use).
#[derive(Clone, Debug, PartialEq, Eq)]
pub struct Generator {
    pub bg: Pcg64,
}

impl Generator {
    pub fn new(bg: Pcg64) -> Self {
        Generator { bg }
    }

    /// `random()`
    pub fn random(&mut self) -> f64 {
        self.bg.next_double()
    }

    /// `uniform(low, high)` = low + (high - low) x U
    pub fn uniform(&mut self, low: f64, high: f64) -> f64 {
        low + (high - low) * self.bg.next_double()
    }

    /// `standard_normal()` (ziggurat)
    pub fn standard_normal(&mut self) -> f64 {
        loop {
            let mut r = self.bg.next_u64();
            let idx = (r & 0xff) as usize;
            r >>= 8;
            let sign = r & 1;
            let rabs = (r >> 1) & 0x000f_ffff_ffff_ffff;
            let mut x = rabs as f64 * zig::WI_DOUBLE[idx];
            if sign & 1 == 1 {
                x = -x;
            }
            if rabs < zig::KI_DOUBLE[idx] {
                return x;
            }
            if idx == 0 {
                loop {
                    let xx = -zig::ZIGGURAT_NOR_INV_R * pymath::log1p(-self.bg.next_double());
                    let yy = -pymath::log1p(-self.bg.next_double());
                    if yy + yy > xx * xx {
                        return if (rabs >> 8) & 1 == 1 {
                            -(zig::ZIGGURAT_NOR_R + xx)
                        } else {
                            zig::ZIGGURAT_NOR_R + xx
                        };
                    }
                }
            } else if (zig::FI_DOUBLE[idx - 1] - zig::FI_DOUBLE[idx]) * self.bg.next_double() + zig::FI_DOUBLE[idx]
                < pymath::exp(-0.5 * x * x)
            {
                return x;
            }
        }
    }

    /// `normal(loc, scale)` = loc + scale x N(0, 1)
    pub fn normal(&mut self, loc: f64, scale: f64) -> f64 {
        loc + scale * self.standard_normal()
    }

    pub fn standard_exponential(&mut self) -> f64 {
        let mut ri = self.bg.next_u64();
        ri >>= 3;
        let idx = (ri & 0xff) as usize;
        ri >>= 8;
        let x = ri as f64 * zig::WE_DOUBLE[idx];
        if ri < zig::KE_DOUBLE[idx] {
            return x;
        }
        if idx == 0 {
            zig::ZIGGURAT_EXP_R - pymath::log1p(-self.bg.next_double())
        } else if (zig::FE_DOUBLE[idx - 1] - zig::FE_DOUBLE[idx]) * self.bg.next_double() + zig::FE_DOUBLE[idx]
            < pymath::exp(-x)
        {
            x
        } else {
            self.standard_exponential()
        }
    }

    pub fn standard_gamma(&mut self, shape: f64) -> f64 {
        if shape == 1.0 {
            return self.standard_exponential();
        } else if shape == 0.0 {
            return 0.0;
        } else if shape < 1.0 {
            loop {
                let u = self.bg.next_double();
                let v = self.standard_exponential();
                if u <= 1.0 - shape {
                    let x = pymath::pow(u, 1.0 / shape);
                    if x <= v {
                        return x;
                    }
                } else {
                    let y = -pymath::log((1.0 - u) / shape);
                    let x = pymath::pow(1.0 - shape + shape * y, 1.0 / shape);
                    if x <= v + y {
                        return x;
                    }
                }
            }
        }
        let b = shape - 1.0 / 3.0;
        let c = 1.0 / pymath::sqrt(9.0 * b);
        loop {
            let (mut x, mut v);
            loop {
                x = self.standard_normal();
                v = 1.0 + c * x;
                if v > 0.0 {
                    break;
                }
            }
            v = v * v * v;
            let u = self.bg.next_double();
            if u < 1.0 - 0.0331 * (x * x) * (x * x) {
                return b * v;
            }
            if pymath::log(u) < 0.5 * x * x + b * (1.0 - v + pymath::log(v)) {
                return b * v;
            }
        }
    }

    /// `beta(a, b)`; only the a > 1 or b > 1 branch (gamma ratio) is used.
    pub fn beta(&mut self, a: f64, b: f64) -> f64 {
        assert!(!(a <= 1.0 && b <= 1.0), "beta: Johnk branch not ported");
        let ga = self.standard_gamma(a);
        let gb = self.standard_gamma(b);
        ga / (ga + gb)
    }

    /// `poisson(lam)`
    pub fn poisson(&mut self, lam: f64) -> i64 {
        if lam >= 10.0 {
            self.poisson_ptrs(lam)
        } else if lam == 0.0 {
            0
        } else {
            let enlam = pymath::exp(-lam);
            let mut x = 0;
            let mut prod = 1.0;
            loop {
                prod *= self.bg.next_double();
                if prod > enlam {
                    x += 1;
                } else {
                    return x;
                }
            }
        }
    }

    fn poisson_ptrs(&mut self, lam: f64) -> i64 {
        let slam = pymath::sqrt(lam);
        let loglam = pymath::log(lam);
        let b = 0.931 + 2.53 * slam;
        let a = -0.059 + 0.02483 * b;
        let invalpha = 1.1239 + 1.1328 / (b - 3.4);
        let vr = 0.9277 - 3.6224 / (b - 2.0);
        loop {
            let u = self.bg.next_double() - 0.5;
            let v = self.bg.next_double();
            let us = 0.5 - u.abs();
            let k = pymath::floor((2.0 * a / us + b) * u + lam + 0.43) as i64;
            if us >= 0.07 && v <= vr {
                return k;
            }
            if k < 0 || (us < 0.013 && v > us) {
                continue;
            }
            if (pymath::log(v) + pymath::log(invalpha) - pymath::log(a / (us * us) + b))
                <= (-lam + k as f64 * loglam - loggam(k as f64 + 1.0))
            {
                return k;
            }
        }
    }

    /// `integers(low, high)`: [low, high) (Lemire; a 32-bit generator if the range fits in 32 bits).
    pub fn integers(&mut self, low: i64, high: i64) -> i64 {
        assert!(high > low, "integers: empty range");
        let rng = (high - 1 - low) as u64;
        low + self.bounded_u64(rng) as i64
    }

    fn bounded_u64(&mut self, rng: u64) -> u64 {
        if rng == 0 {
            0
        } else if rng <= 0xFFFF_FFFF {
            if rng == 0xFFFF_FFFF {
                return self.bg.next_u32() as u64;
            }
            let rng = rng as u32;
            let excl = rng.wrapping_add(1);
            let mut m = self.bg.next_u32() as u64 * excl as u64;
            let mut left = m as u32;
            if left < excl {
                let thr = (u32::MAX - rng) % excl;
                while left < thr {
                    m = self.bg.next_u32() as u64 * excl as u64;
                    left = m as u32;
                }
            }
            m >> 32
        } else if rng == u64::MAX {
            self.bg.next_u64()
        } else {
            let excl = rng + 1;
            let mut m = self.bg.next_u64() as u128 * excl as u128;
            let mut left = m as u64;
            if left < excl {
                let thr = (u64::MAX - rng) % excl;
                while left < thr {
                    m = self.bg.next_u64() as u128 * excl as u128;
                    left = m as u64;
                }
            }
            (m >> 64) as u64
        }
    }

    /// `random_interval(max)` (masked rejection; used by permutation/shuffle).
    fn interval(&mut self, max: u64) -> u64 {
        if max == 0 {
            return 0;
        }
        let mut mask = max;
        mask |= mask >> 1;
        mask |= mask >> 2;
        mask |= mask >> 4;
        mask |= mask >> 8;
        mask |= mask >> 16;
        mask |= mask >> 32;
        if max <= 0xFFFF_FFFF {
            loop {
                let v = self.bg.next_u32() as u64 & mask;
                if v <= max {
                    return v;
                }
            }
        } else {
            loop {
                let v = self.bg.next_u64() & mask;
                if v <= max {
                    return v;
                }
            }
        }
    }

    /// `permutation(n)` = `shuffle(arange(n))` (Fisher-Yates, from the end).
    pub fn permutation(&mut self, n: usize) -> Vec<usize> {
        let mut v: Vec<usize> = (0..n).collect();
        let mut i = n;
        while i > 1 {
            i -= 1;
            let j = self.interval(i as u64) as usize;
            v.swap(i, j);
        }
        v
    }
}

fn loggam(x: f64) -> f64 {
    #[allow(clippy::excessive_precision)] // NumPy loggam coefficients, copied verbatim
    const A: [f64; 10] = [
        8.333333333333333e-02,
        -2.777777777777778e-03,
        7.936507936507937e-04,
        -5.952380952380952e-04,
        8.417508417508418e-04,
        -1.917526917526918e-03,
        6.410256410256410e-03,
        -2.955065359477124e-02,
        1.796443723688307e-01,
        -1.39243221690590e+00,
    ];
    if x == 1.0 || x == 2.0 {
        return 0.0;
    }
    let n: i64 = if x < 7.0 { (7.0 - x) as i64 } else { 0 };
    let mut x0 = x + n as f64;
    let x2 = (1.0 / x0) * (1.0 / x0);
    let lg2pi = 1.8378770664093453e+00;
    let mut gl0 = A[9];
    for k in (0..=8).rev() {
        gl0 *= x2;
        gl0 += A[k];
    }
    let mut gl = gl0 / x0 + 0.5 * lg2pi + (x0 - 0.5) * pymath::log(x0) - x0;
    if x < 7.0 {
        for _ in 1..=n {
            gl -= pymath::log(x0 - 1.0);
            x0 -= 1.0;
        }
    }
    gl
}

/// zlib crc32 (Python `zlib.crc32`).
pub fn crc32(data: &[u8]) -> u32 {
    let mut c: u32 = 0xFFFF_FFFF;
    for &b in data {
        c ^= b as u32;
        for _ in 0..8 {
            c = if c & 1 != 0 { 0xEDB8_8320 ^ (c >> 1) } else { c >> 1 };
        }
    }
    !c
}

/// Exportable generator state (same fields as NumPy `bit_generator.state`).
#[derive(Clone, Debug, Serialize, Deserialize, PartialEq, Eq)]
pub struct GenState {
    pub state: String,
    pub inc: String,
    pub has_uint32: u8,
    pub uinteger: u32,
}

impl From<&Generator> for GenState {
    fn from(g: &Generator) -> Self {
        GenState {
            state: g.bg.state.to_string(),
            inc: g.bg.inc.to_string(),
            has_uint32: g.bg.has_uint32 as u8,
            uinteger: g.bg.uinteger,
        }
    }
}

impl From<&GenState> for Generator {
    fn from(s: &GenState) -> Self {
        Generator::new(Pcg64 {
            state: s.state.parse().expect("rng state"),
            inc: s.inc.parse().expect("rng inc"),
            has_uint32: s.has_uint32 != 0,
            uinteger: s.uinteger,
        })
    }
}

/// `sim/rng.py::RngStreams`: one named stream per subsystem; created on first use with `SeedSequence([seed, crc32(name)])`.
#[derive(Clone, Debug)]
pub struct RngStreams {
    pub seed: u64,
    pub streams: IndexMap<String, Generator>,
}

impl RngStreams {
    pub fn new(seed: u64) -> Self {
        RngStreams { seed, streams: IndexMap::new() }
    }

    pub fn get(&mut self, name: &str) -> &mut Generator {
        if !self.streams.contains_key(name) {
            let mut ent = int_to_u32_words(self.seed as u128);
            ent.extend(int_to_u32_words(crc32(name.as_bytes()) as u128));
            self.streams.insert(name.to_string(), Generator::new(Pcg64::from_entropy(&ent)));
        }
        self.streams.get_mut(name).unwrap()
    }
}

#[derive(Serialize, Deserialize)]
struct StreamsRepr {
    seed: u64,
    streams: IndexMap<String, GenState>,
}

impl Serialize for RngStreams {
    fn serialize<S: serde::Serializer>(&self, s: S) -> Result<S::Ok, S::Error> {
        StreamsRepr {
            seed: self.seed,
            streams: self.streams.iter().map(|(k, g)| (k.clone(), GenState::from(g))).collect(),
        }
        .serialize(s)
    }
}

impl<'de> Deserialize<'de> for RngStreams {
    fn deserialize<D: serde::Deserializer<'de>>(d: D) -> Result<Self, D::Error> {
        let r = StreamsRepr::deserialize(d)?;
        Ok(RngStreams {
            seed: r.seed,
            streams: r.streams.iter().map(|(k, g)| (k.clone(), Generator::from(g))).collect(),
        })
    }
}
