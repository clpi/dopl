fn fib(n) {
  if n <= 1 { return n }
  return fib(n - 1) + fib(n - 2)
}

fn main() {
  let result = fib(42)
  print("result:", result)
  return result
}
