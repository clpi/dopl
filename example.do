# Ado Language Feature Demonstration
# This example showcases I/O, control flow, and complex algorithms

# Fibonacci sequence
fn fib(n) {
  if n <= 1 {
    return n
  }
  return fib(n - 1) + fib(n - 2)
}

# Factorial computation
fn factorial(n) {
  if n <= 1 {
    return 1
  }
  return n * factorial(n - 1)
}

# Check if number is prime
fn is_prime(n) {
  if n < 2 {
    return 0
  }
  let i = 2
  while i * i <= n {
    if n % i == 0 {
      return 0
    }
    i = i + 1
  }
  return 1
}

# Sum numbers from a to b
fn sum_range(a, b) {
  let total = 0
  let i = a
  while i <= b {
    total = total + i
    i = i + 1
  }
  return total
}

# Greatest common divisor using Euclidean algorithm
fn gcd(a, b) {
  while b != 0 {
    let temp = b
    b = a % b
    a = temp
  }
  return a
}

# Power function (iterative)
fn power(base, exp) {
  let result = 1
  let i = 0
  while i < exp {
    result = result * base
    i = i + 1
  }
  return result
}

# Collatz sequence length
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

# Count digits in number
fn count_digits(n) {
  if n == 0 {
    return 1
  }
  let count = 0
  while n != 0 {
    n = n / 10
    count = count + 1
  }
  return count
}

# Reverse digits
fn reverse_num(n) {
  let rev = 0
  while n != 0 {
    rev = rev * 10 + n % 10
    n = n / 10
  }
  return rev
}

# Check palindrome
fn is_palindrome(n) {
  return n == reverse_num(n)
}

# Main entry point
fn main() {
  print("Ado Language Demo")
  print("=================")
  
  # Fibonacci
  print("")
  print("Fibonacci(10):")
  print(fib(10))
  
  # Factorial
  print("")
  print("Factorial(7):")
  print(factorial(7))
  
  # Prime numbers
  print("")
  print("Prime numbers up to 30:")
  let n = 2
  while n <= 30 {
    if is_prime(n) {
      print(n)
    }
    n = n + 1
  }
  
  # Range sum
  print("")
  print("Sum 1 to 10:")
  print(sum_range(1, 10))
  
  # GCD
  print("")
  print("GCD(48, 18):")
  print(gcd(48, 18))
  
  # Power
  print("")
  print("2 to the power 10:")
  print(power(2, 10))
  
  # Collatz
  print("")
  print("Collatz steps for 27:")
  print(collatz_steps(27))
  
  # Digit counting
  print("")
  print("Digits in 12345:")
  print(count_digits(12345))
  
  # Reverse
  print("")
  print("Reverse of 12345:")
  print(reverse_num(12345))
  
  # Palindrome check
  print("")
  print("Is 12321 palindrome?")
  if is_palindrome(12321) {
    print("Yes!")
  } else {
    print("No!")
  }
  
  # Boolean logic demo
  print("")
  print("Boolean logic demo:")
  if true and not false {
    print("true and not false = true")
  }
  if false or true {
    print("false or true = true")
  }
  
  # Arithmetic operators
  print("")
  print("Arithmetic operations:")
  print("15 mod 4 =")
  print(15 % 4)
  print("100 div 7 =")
  print(100 / 7)
  
  # Chained comparisons
  print("")
  print("Chained comparisons:")
  if 5 < 10 and 10 <= 10 and 10 == 10 {
    print("All comparisons passed!")
  }
  
  # Nested conditionals
  print("")
  print("Nested control flow:")
  let x = 15
  if x > 10 {
    if x < 20 {
      print("x is between 10 and 20")
    } else {
      print("x is >= 20")
    }
  } else {
    print("x is <= 10")
  }
  
  # Counting loop
  print("")
  print("Counting 1 to 5:")
  let i = 1
  while i <= 5 {
    print(i)
    i = i + 1
  }
  
  # Table generation
  print("")
  print("Powers of 2:")
  let p = 1
  i = 0
  while i <= 10 {
    print(power(2, i))
    p = p * 2
    i = i + 1
  }
  
  print("")
  print("Done!")
  return 0
}
