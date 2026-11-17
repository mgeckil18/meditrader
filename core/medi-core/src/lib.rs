//! Medi simulation core: a bit-exact Rust counterpart of the Python `sim/world5.py` engine, plus mechanisms added since.
//! Architecture and verification method: showcase/engineering/ (English), docs/design/rust-core.md (Turkish).

// Event logs are plain tuples that mirror the Python reference engine row for row.
#![allow(clippy::type_complexity)]

pub mod config;
pub mod consts;
pub mod date;
pub mod digest;
pub mod ledger;
pub mod map;
pub mod market;
pub mod prof;
pub mod pymath;
pub mod rng;
pub mod world;
