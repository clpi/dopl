# Conditional expressions demonstration

fn max(a, b) {
  if a > b {
    return a
  }
  return b
}

fn min(a, b) {
  if a < b {
    return a
  }
  return b
}

fn abs(n) {
  if n < 0 {
    return 0 - n
  }
  return n
}

fn sign(n) {
  if n < 0 {
    return -1
  }
  if n > 0 {
    return 1
  }
  return 0
}

fn clamp(val, lo, hi) {
  return max(lo, min(hi, val))
}

fn main() {
  print("Conditional Functions Demo")
  print("==========================")
  print("")
  print("max(10, 20) =", max(10, 20))
  print("max(30, 20) =", max(30, 20))
  print("")
  print("min(10, 20) =", min(10, 20))
  print("min(30, 20) =", min(30, 20))
  print("")
  print("abs(-15) =", abs(-15))
  print("abs(15) =", abs(15))
  print("abs(0) =", abs(0))
  print("")
  print("sign(-42) =", sign(-42))
  print("sign(42) =", sign(42))
  print("sign(0) =", sign(0))
  print("")
  print("clamp(50, 0, 100) =", clamp(50, 0, 100))
  print("clamp(-50, 0, 100) =", clamp(-50, 0, 100))
  print("clamp(150, 0, 100) =", clamp(150, 0, 100))
  return 0
}
