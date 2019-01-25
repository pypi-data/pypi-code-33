# This file is generated automatically by scripts
from __future__ import absolute_import, division, print_function
import kimpy

attributes = [
  kimpy.log_verbosity.silent,
  kimpy.log_verbosity.fatal,
  kimpy.log_verbosity.error,
  kimpy.log_verbosity.warning,
  kimpy.log_verbosity.information,
  kimpy.log_verbosity.debug,
]


str_names = [
  "silent",
  "fatal",
  "error",
  "warning",
  "information",
  "debug",
]


def test_main():

  N = kimpy.log_verbosity.get_number_of_log_verbosities()
  assert N == 6

  all_instances = []
  for i in range(N):
    inst,error = kimpy.log_verbosity.get_log_verbosity(i)
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
  inst,error = kimpy.log_verbosity.get_log_verbosity(N)
  assert error == True


if __name__ == '__main__':
  test_main()

