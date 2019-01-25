# This file is generated automatically by scripts
from __future__ import absolute_import, division, print_function
import kimpy

attributes = [
  kimpy.length_unit.unused,
  kimpy.length_unit.A,
  kimpy.length_unit.Bohr,
  kimpy.length_unit.cm,
  kimpy.length_unit.m,
  kimpy.length_unit.nm,
]


str_names = [
  "unused",
  "A",
  "Bohr",
  "cm",
  "m",
  "nm",
]


def test_main():

  N = kimpy.length_unit.get_number_of_length_units()
  assert N == 6

  all_instances = []
  for i in range(N):
    inst,error = kimpy.length_unit.get_length_unit(i)
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
  inst,error = kimpy.length_unit.get_length_unit(N)
  assert error == True


if __name__ == '__main__':
  test_main()

