fn is_prime(n) {
  if n < 2 { return 0 }
  let i = 2
  while i * i <= n {
    if n % i == 0 { return 0 }
    i = i + 1
  }
  return 1
}

fn count_primes(limit) {
  let count = 0
  let n = 2
  while n <= limit {
    if is_prime(n) { count = count + 1 }
    n = n + 1
  }
  return count
}

fn main() {
  let result = count_primes(100000)
  print("primes up to 100000:", result)
  return result
}
