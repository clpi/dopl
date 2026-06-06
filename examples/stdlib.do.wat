(module
  (import "env" "print_i32" (func $print_i32 (param i32)))
  (import "env" "memcpy" (func $memcpy (param i32 i32 i32) (result i32)))
  (import "env" "malloc" (func $malloc (param i32) (result i32)))
  (memory (export "memory") 1 256)
  (func $ado_abs (param $x i32) (result i32)
    local.get $x
    i32.const 0
    i32.lt_s
    if (result i32)
      i32.const 0
      local.get $x
      i32.sub
    else
      local.get $x
    end
  )
  (func $ado_min (param $a i32) (param $b i32) (result i32)
    local.get $a
    local.get $b
    i32.gt_s
    if
      local.get $b
    else
      local.get $a
    end
  )
  (func $ado_max (param $a i32) (param $b i32) (result i32)
    local.get $a
    local.get $b
    i32.lt_s
    if
      local.get $b
    else
      local.get $a
    end
  )
  (func $main (export "_start") (result i32)
  ;; unsupported stmt
    i32.const 0
    return
  )
)
