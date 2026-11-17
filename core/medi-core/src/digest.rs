//! State digest: same as `core/tools/state_io.py::digest`. The tree is turned into a type-tagged byte string and SHA-1 hashed.
//! Dict keys are sorted (internal order need not match Python); numbers are written as float64 bits.

use indexmap::IndexMap;
use serde_json::Value;

fn num(buf: &mut Vec<u8>, x: f64) {
    buf.push(b'D');
    buf.extend_from_slice(&x.to_le_bytes());
}

fn ser(v: &Value, buf: &mut Vec<u8>) {
    match v {
        Value::Null => buf.push(b'N'),
        Value::Bool(true) => buf.push(b'T'),
        Value::Bool(false) => buf.push(b'F'),
        Value::Number(n) => num(buf, n.as_f64().unwrap()),
        Value::String(s) => match s.as_str() {
            "inf" => num(buf, f64::INFINITY),
            "-inf" => num(buf, f64::NEG_INFINITY),
            "nan" => num(buf, f64::NAN),
            _ => {
                buf.push(b'S');
                buf.extend_from_slice(&(s.len() as u32).to_le_bytes());
                buf.extend_from_slice(s.as_bytes());
            }
        },
        Value::Array(a) => {
            buf.push(b'L');
            buf.extend_from_slice(&(a.len() as u32).to_le_bytes());
            for x in a {
                ser(x, buf);
            }
        }
        Value::Object(o) => {
            buf.push(b'M');
            buf.extend_from_slice(&(o.len() as u32).to_le_bytes());
            let mut keys: Vec<&String> = o.keys().collect();
            keys.sort();
            for k in keys {
                buf.extend_from_slice(&(k.len() as u32).to_le_bytes());
                buf.extend_from_slice(k.as_bytes());
                ser(&o[k], buf);
            }
        }
    }
}

fn hash(v: &Value) -> String {
    let mut b = Vec::new();
    ser(v, &mut b);
    let h = sha1_smol::Sha1::from(&b).digest().to_string();
    h[..16].to_string()
}

/// Digest per top-level field; per element for `merchants`, `gone` and `markets`.
pub fn digest(tree: &Value) -> IndexMap<String, String> {
    let mut out = IndexMap::new();
    let o = tree.as_object().expect("state is not an object");
    let mut keys: Vec<&String> = o.keys().collect();
    keys.sort();
    for k in keys {
        let v = &o[k];
        if k == "n_npc" || k == "cfg" {
            continue;
        }
        match (k.as_str(), v) {
            ("merchants" | "markets" | "gone", Value::Array(a)) => {
                for (i, x) in a.iter().enumerate() {
                    out.insert(format!("{k}/{i}"), hash(x));
                }
                out.insert(format!("{k}/len"), a.len().to_string());
            }
            _ => {
                out.insert(k.clone(), hash(v));
            }
        }
    }
    out
}
