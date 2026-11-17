//! Test helpers: parses Python's `float.hex()` format.
pub fn unhex(s: &str) -> f64 {
    match s {
        "inf" => return f64::INFINITY,
        "-inf" => return f64::NEG_INFINITY,
        "nan" => return f64::NAN,
        _ => {}
    }
    let (neg, s) = if let Some(r) = s.strip_prefix('-') { (true, r) } else { (false, s) };
    let s = s.strip_prefix("0x").expect("hex");
    let (mant, exp) = s.split_once('p').expect("p");
    let exp: i32 = exp.parse().unwrap();
    let (ip, fp) = mant.split_once('.').unwrap_or((mant, ""));
    let mut m: u64 = u64::from_str_radix(ip, 16).unwrap();
    for c in fp.chars() {
        m = m * 16 + c.to_digit(16).unwrap() as u64;
    }
    let e = exp - 4 * fp.len() as i32;
    // m < 2^57, exponent scale: scale in two steps for an exact result (no underflow in these fixtures)
    let v = (m as f64) * 2f64.powi(e);
    if neg {
        -v
    } else {
        v
    }
}
