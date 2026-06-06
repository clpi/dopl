fn collatz_steps(n) {
  let steps = 0
  while n != 1 {
    if n % 2 == 0 {
      n = n / 2
    } else {
      n = 3 * n + 1
    }
    steps = steps + 1
  }
  return steps
}

fn max_collatz(limit) {
  let max_steps = 0
  let max_n = 0
  let i = 1
  while i <= limit {
    let steps = collatz_steps(i)
    if steps > max_steps {
      max_steps = steps
      max_n = i
    }
    i = i + 1
  }
  return max_n
}

fn main() {
  let result = max_collatz(100000)
  print("max collatz n up to 100000:", result)
  return result
}
