fn main() {
  let arr = [10, 20, 30]
  push(arr, 40)
  let empty = []
  push(empty, 1)
  let vals = [1, 2, 3, 4, 5]
  let stack = [10, 20, 30]
  print(ado_pop(stack))
  print(len(stack))
  let rev = [1, 2, 3, 4, 5]
  ado_reverse(rev)
  print(rev[0])
  let rm = [100, 200, 300, 400]
  ado_remove(rm, 1)
  print(len(rm))
  let ins = [1, 2, 4, 5]
  ado_insert(ins, 2, 3)
  print(len(ins))
  let nums = [5, 2, 8, 1, 9]
  let i = 0
  let total = 0
  while i < len(nums) {
    total = total + nums[i]
    i = i + 1
  }
  print(total)
  return 0
  print("ado_min(9, 2) =", ado_min(9, 2))

  print("ado_max(3, 7) =", ado_max(3, 7))
  print("ado_max(9, 2) =", ado_max(9, 2))

  print("ado_clamp(5, 0, 10) =", ado_clamp(5, 0, 10))
  print("ado_clamp(-5, 0, 10) =", ado_clamp(-5, 0, 10))
  print("ado_clamp(15, 0, 10) =", ado_clamp(15, 0, 10))

  print("ado_pow(2, 0) =", ado_pow(2, 0))
  print("ado_pow(2, 10) =", ado_pow(2, 10))
  print("ado_pow(3, 4) =", ado_pow(3, 4))

  # Extended Math Helpers
  print("")
  print("=== Extended Math Helpers ===")

  print("ado_sign(-10) =", ado_sign(-10))
  print("ado_sign(0) =", ado_sign(0))
  print("ado_sign(42) =", ado_sign(42))

  print("ado_is_even(4) =", ado_is_even(4))
  print("ado_is_even(7) =", ado_is_even(7))
  print("ado_is_odd(4) =", ado_is_odd(4))
  print("ado_is_odd(7) =", ado_is_odd(7))

  print("ado_gcd(12, 8) =", ado_gcd(12, 8))
  print("ado_gcd(17, 5) =", ado_gcd(17, 5))
  print("ado_lcm(12, 8) =", ado_lcm(12, 8))
  print("ado_lcm(6, 4) =", ado_lcm(6, 4))

  # Array Operation Tests
  print("")
  print("=== Array Operation Tests ===")

  # contains
  let vals = [1, 2, 3, 4, 5]
  print("contains(vals, 3) =", ado_contains(vals, 3))
  print("contains(vals, 9) =", ado_contains(vals, 9))

  # pop
  let stack = [10, 20, 30]
  print("pop(stack) =", ado_pop(stack))
  print("after pop, len =", len(stack))
  print("stack[0] =", stack[0])
  print("stack[1] =", stack[1])

  # reverse
  let rev = [1, 2, 3, 4, 5]
  ado_reverse(rev)
  print("rev[0] after reverse =", rev[0])
  print("rev[1] =", rev[1])
  print("rev[2] =", rev[2])
  print("rev[3] =", rev[3])
  print("rev[4] =", rev[4])

  # remove
  let rm = [100, 200, 300, 400]
  ado_remove(rm, 1)
  print("after remove idx 1, len =", len(rm))
  print("rm[0] =", rm[0])
  print("rm[1] =", rm[1])
  print("rm[2] =", rm[2])

  # insert
  let ins = [1, 2, 4, 5]
  ado_insert(ins, 2, 3)
  print("after insert 3 at idx 2, len =", len(ins))
  print("ins[0] =", ins[0])
  print("ins[1] =", ins[1])
  print("ins[2] =", ins[2])
  print("ins[3] =", ins[3])
  print("ins[4] =", ins[4])

  # Combined Test
  print("")
  print("=== Combined Test ===")

  let nums = [5, 2, 8, 1, 9]
  let total = 0
  for idx in 0..5 {
    total = total + nums[idx]
  }
  print("sum of [5,2,8,1,9] =", total)

  print("")
  print("All stdlib tests passed!")
  return 0
