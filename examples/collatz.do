# Collatz sequence length calculator
fn collatz(n) {
  if n == 1 {
    return 0
  }
  if n / 2 * 2 == n {
    return 1 + collatz(n / 2)
  }
  return 1 + collatz(3 * n + 1)
}

fn main() {
  print("Collatz sequence lengths:")
  let i = 1
  while i <= 20 {
    print(i, collatz(i))
    i = i + 1
  }
  print("")
  print("Collatz(27) =", collatz(27), "steps")
  return 0
}
