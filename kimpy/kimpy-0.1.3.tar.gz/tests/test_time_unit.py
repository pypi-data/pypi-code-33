# This file is generated automatically by scripts
from __future__ import absolute_import, division, print_function
import kimpy

attributes = [
  kimpy.time_unit.unused,
  kimpy.time_unit.fs,
  kimpy.time_unit.ps,
  kimpy.time_unit.ns,
  kimpy.time_unit.s,
]


str_names = [
  "unused",
  "fs",
  "ps",
  "ns",
  "s",
]


def test_main():

  N = kimpy.time_unit.get_number_of_time_units()
  assert N == 5

  all_instances = []
  for i in range(N):
    inst,error = kimpy.time_unit.get_time_unit(i)
    all_instances.append(inst)

    assert error == False
    assert inst == attributes[i]
    assert str(inst) == str_names[i]

  # test operator overloading
  for i in range(N):
    assert all_instances[i] == all_instances[i]
    for j in range(i+1, N):
      assert all_instances[i] != all_instances[j]

  # test out of bound
  inst,error = kimpy.time_unit.get_time_unit(N)
  assert error == True


if __name__ == '__main__':
  test_main()

