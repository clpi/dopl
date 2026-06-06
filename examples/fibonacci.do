# Fibonacci sequence calculator
fn fibonacci(n) {
  if n <= 1 {
    return n
  }
  return fibonacci(n - 1) + fibonacci(n - 2)
}

fn main() {
  print("Fibonacci(10) =", fibonacci(10))
  return 0
}
