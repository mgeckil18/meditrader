//! Calendar (counterpart of `datetime.date`, proleptic Gregorian). "YYYY-MM-DD" in JSON.

use serde::{Deserialize, Deserializer, Serialize, Serializer};

#[derive(Clone, Copy, Debug, PartialEq, Eq, PartialOrd, Ord)]
pub struct Date {
    /// Days since 0001-01-01 (Python `date.toordinal() - 1`).
    ord: i64,
}

fn days_from_civil(y: i64, m: u32, d: u32) -> i64 {
    let y = if m <= 2 { y - 1 } else { y };
    let era = y.div_euclid(400);
    let yoe = y - era * 400;
    let mp = (m as i64 + 9) % 12;
    let doy = (153 * mp + 2) / 5 + d as i64 - 1;
    let doe = yoe * 365 + yoe / 4 - yoe / 100 + doy;
    era * 146097 + doe - 719468
}

fn civil_from_days(z: i64) -> (i64, u32, u32) {
    let z = z + 719468;
    let era = z.div_euclid(146097);
    let doe = z - era * 146097;
    let yoe = (doe - doe / 1460 + doe / 36524 - doe / 146096) / 365;
    let y = yoe + era * 400;
    let doy = doe - (365 * yoe + yoe / 4 - yoe / 100);
    let mp = (5 * doy + 2) / 153;
    let d = (doy - (153 * mp + 2) / 5 + 1) as u32;
    let m = if mp < 10 { mp + 3 } else { mp - 9 } as u32;
    (if m <= 2 { y + 1 } else { y }, m, d)
}

impl Date {
    pub fn new(y: i64, m: u32, d: u32) -> Date {
        Date { ord: days_from_civil(y, m, d) }
    }
    pub fn ymd(self) -> (i64, u32, u32) {
        civil_from_days(self.ord)
    }
    pub fn year(self) -> i64 {
        self.ymd().0
    }
    pub fn month(self) -> u32 {
        self.ymd().1
    }
    pub fn day(self) -> u32 {
        self.ymd().2
    }
    pub fn add_days(self, n: i64) -> Date {
        Date { ord: self.ord + n }
    }
    /// `(self - other).days`
    pub fn days_since(self, other: Date) -> i64 {
        self.ord - other.ord
    }
}

pub const START_DATE: (i64, u32, u32) = (1560, 3, 1);

impl Serialize for Date {
    fn serialize<S: Serializer>(&self, s: S) -> Result<S::Ok, S::Error> {
        let (y, m, d) = self.ymd();
        s.serialize_str(&format!("{y:04}-{m:02}-{d:02}"))
    }
}

impl<'de> Deserialize<'de> for Date {
    fn deserialize<D: Deserializer<'de>>(de: D) -> Result<Date, D::Error> {
        let s = String::deserialize(de)?;
        let p: Vec<&str> = s.split('-').collect();
        let bad = || serde::de::Error::custom(format!("tarih: {s}"));
        if p.len() != 3 {
            return Err(bad());
        }
        Ok(Date::new(
            p[0].parse().map_err(|_| bad())?,
            p[1].parse().map_err(|_| bad())?,
            p[2].parse().map_err(|_| bad())?,
        ))
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn roundtrip() {
        let d = Date::new(1560, 3, 1);
        assert_eq!(d.ymd(), (1560, 3, 1));
        assert_eq!(d.add_days(365).ymd(), (1561, 3, 1));
        assert_eq!(Date::new(1600, 3, 1).days_since(Date::new(1600, 2, 1)), 29);
        assert_eq!(Date::new(1700, 3, 1).days_since(Date::new(1700, 2, 1)), 28);
    }
}
