# This file is generated automatically by scripts
from __future__ import absolute_import, division, print_function
import kimpy

attributes = [
  kimpy.model_routine_name.Create,
  kimpy.model_routine_name.ComputeArgumentsCreate,
  kimpy.model_routine_name.Compute,
  kimpy.model_routine_name.Extension,
  kimpy.model_routine_name.Refresh,
  kimpy.model_routine_name.WriteParameterizedModel,
  kimpy.model_routine_name.ComputeArgumentsDestroy,
  kimpy.model_routine_name.Destroy,
]


str_names = [
  "Create",
  "ComputeArgumentsCreate",
  "Compute",
  "Extension",
  "Refresh",
  "WriteParameterizedModel",
  "ComputeArgumentsDestroy",
  "Destroy",
]


def test_main():

  N = kimpy.model_routine_name.get_number_of_model_routine_names()
  assert N == 8

  all_instances = []
  for i in range(N):
    inst,error = kimpy.model_routine_name.get_model_routine_name(i)
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
  inst,error = kimpy.model_routine_name.get_model_routine_name(N)
  assert error == True


if __name__ == '__main__':
  test_main()

