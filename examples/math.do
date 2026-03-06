# Math functions demonstration

fn power(base, exp) {
  if exp == 0 {
    return 1
  }
  return base * power(base, exp - 1)
}

fn sum(n) {
  if n <= 0 {
    return 0
  }
  return n + sum(n - 1)
}

fn factorial(n) {
  if n <= 1 {
    return 1
  }
  return n * factorial(n - 1)
}

fn main() {
  print("Math Functions Demo")
  print("===================")
  print("")
  print("2^8 =", power(2, 8))
  print("2^10 =", power(2, 10))
  print("3^5 =", power(3, 5))
  print("")
  print("Sum 1 to 10 =", sum(10))
  print("Sum 1 to 100 =", sum(100))
  print("")
  print("Factorial(5) =", factorial(5))
  print("Factorial(10) =", factorial(10))
  return 0
}
