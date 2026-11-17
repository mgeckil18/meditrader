mod common;
use common::unhex;
use medi_core::{pymath, rng};
use serde_json::Value;

fn load(name: &str) -> Value {
    let p = format!("{}/../fixtures/{}", env!("CARGO_MANIFEST_DIR"), name);
    serde_json::from_str(&std::fs::read_to_string(p).unwrap()).unwrap()
}

fn vec_of(v: &Value) -> Vec<f64> {
    v.as_array().unwrap().iter().map(|x| unhex(x.as_str().unwrap())).collect()
}

fn same(a: f64, b: f64) -> bool {
    a.to_bits() == b.to_bits() || (a.is_nan() && b.is_nan())
}

#[test]
fn python_numpy_math() {
    let m = load("math.json");
    for (key, f) in [
        ("sums", (|v: &[f64]| pymath::sum(v.iter().copied())) as fn(&[f64]) -> f64),
        ("means", pymath::np_mean),
        ("stds", pymath::np_std),
        ("medians", pymath::np_median),
    ] {
        let mut bad = 0;
        for c in m[key].as_array().unwrap() {
            let v = vec_of(&c[0]);
            let want = unhex(c[1].as_str().unwrap());
            let got = f(&v);
            if !same(got, want) {
                bad += 1;
                if bad < 4 {
                    eprintln!("{key} n={} got {got:e} want {want:e}", v.len());
                }
            }
        }
        assert_eq!(bad, 0, "{key}");
    }
    for c in m["rounds"].as_array().unwrap() {
        assert_eq!(pymath::round(unhex(c[0].as_str().unwrap())), c[1].as_i64().unwrap());
    }
    for c in m["mods"].as_array().unwrap() {
        let (a, b, w) = (unhex(c[0].as_str().unwrap()), unhex(c[1].as_str().unwrap()), unhex(c[2].as_str().unwrap()));
        assert!(same(pymath::fmod_py(a, b), w), "mod {a} {b}");
    }
    for c in m["fdivs"].as_array().unwrap() {
        let (a, b, w) = (unhex(c[0].as_str().unwrap()), unhex(c[1].as_str().unwrap()), unhex(c[2].as_str().unwrap()));
        assert!(same(pymath::floordiv(a, b), w), "floordiv {a} {b}");
    }
}

#[test]
fn numpy_rng_streams() {
    let cases = load("rng.json");
    for c in cases.as_array().unwrap() {
        let seed = c["seed"].as_u64().unwrap();
        let name = c["name"].as_str().unwrap();
        assert_eq!(rng::crc32(name.as_bytes()) as u64, c["crc"].as_u64().unwrap());
        let mut st = rng::RngStreams::new(seed);
        let g = st.get(name);
        assert_eq!(g.bg.state.to_string(), c["init_state"].as_str().unwrap(), "init state {seed} {name}");
        assert_eq!(g.bg.inc.to_string(), c["init_inc"].as_str().unwrap(), "init inc");
        for (i, d) in c["draws"].as_array().unwrap().iter().enumerate() {
            let meth = d[0].as_str().unwrap();
            let a = d[1].as_array().unwrap();
            let fa = |k: usize| a[k].as_f64().unwrap();
            let ctx = format!("{seed} {name} #{i} {meth}");
            match meth {
                "random" => assert!(same(g.random(), unhex(d[2].as_str().unwrap())), "{ctx}"),
                "normal" => assert!(same(g.normal(fa(0), fa(1)), unhex(d[2].as_str().unwrap())), "{ctx}"),
                "standard_normal" => assert!(same(g.standard_normal(), unhex(d[2].as_str().unwrap())), "{ctx}"),
                "standard_exponential" => {
                    assert!(same(g.standard_exponential(), unhex(d[2].as_str().unwrap())), "{ctx}")
                }
                "uniform" => assert!(same(g.uniform(fa(0), fa(1)), unhex(d[2].as_str().unwrap())), "{ctx}"),
                "beta" => assert!(same(g.beta(fa(0), fa(1)), unhex(d[2].as_str().unwrap())), "{ctx}"),
                "integers" => assert_eq!(
                    g.integers(a[0].as_i64().unwrap(), a[1].as_i64().unwrap()),
                    d[2].as_i64().unwrap(),
                    "{ctx}"
                ),
                "poisson" => assert_eq!(g.poisson(fa(0)), d[2].as_i64().unwrap(), "{ctx}"),
                "permutation" => {
                    let want: Vec<usize> =
                        d[2].as_array().unwrap().iter().map(|x| x.as_u64().unwrap() as usize).collect();
                    assert_eq!(g.permutation(a[0].as_u64().unwrap() as usize), want, "{ctx}")
                }
                _ => panic!("{meth}"),
            }
        }
        assert_eq!(g.bg.state.to_string(), c["end_state"].as_str().unwrap(), "end state {seed} {name}");
        assert_eq!(g.bg.has_uint32 as i64, c["end_has"].as_i64().unwrap());
        assert_eq!(g.bg.uinteger as i64, c["end_u"].as_i64().unwrap());
    }
}
