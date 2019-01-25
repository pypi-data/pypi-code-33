# This file is generated automatically by scripts
from __future__ import absolute_import, division, print_function
import kimpy

attributes = [
  kimpy.temperature_unit.unused,
  kimpy.temperature_unit.K,
]


str_names = [
  "unused",
  "K",
]


def test_main():

  N = kimpy.temperature_unit.get_number_of_temperature_units()
  assert N == 2

  all_instances = []
  for i in range(N):
    inst,error = kimpy.temperature_unit.get_temperature_unit(i)
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
  inst,error = kimpy.temperature_unit.get_temperature_unit(N)
  assert error == True


if __name__ == '__main__':
  test_main()

