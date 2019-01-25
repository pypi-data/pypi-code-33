# This file is generated automatically by scripts
from __future__ import absolute_import, division, print_function
import kimpy

attributes = [
  kimpy.language_name.cpp,
  kimpy.language_name.c,
  kimpy.language_name.fortran,
]


str_names = [
  "cpp",
  "c",
  "fortran",
]


def test_main():

  N = kimpy.language_name.get_number_of_language_names()
  assert N == 3

  all_instances = []
  for i in range(N):
    inst,error = kimpy.language_name.get_language_name(i)
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
  inst,error = kimpy.language_name.get_language_name(N)
  assert error == True


if __name__ == '__main__':
  test_main()

