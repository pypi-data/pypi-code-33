import cProfile
from .utils import get_class_and_fn_from_str

# Adapted from:
# https://zapier.com/engineering/profiling-python-boss/

### Usage
# There are two options. Decorate a function, then just run your code.
# Note: @do_profile requires `pip install line_profiler`.


### Simple @do_profile ###

# @do_cprofile
# def your_func_here(...)


### Line-by-line: @do_profile ###

# @do_profile(follow=[some_subfunc_to_test])
# def your_func_here(...)
#   some_subfunc_to_test()


# Notes for line-by-line
# If you're profiling a member function, use the fully qualified string <module>.<class>.<fn> in the follow list. It will work automagically.
# For example: follow=['my.fully.qualified.MyClass.my_fn']
#
# If you're profiling a standalone function, pass the raw function to the follow list.
# If you call the profiled function in a loop, you'll have to create the Profiler object outside of the loop and pass it in via profiler=.
# If you do pass in your own profiler, you'll have to call yourprofiler.print_stats() after the loop to get the
# Note that the profiler object will likely have to be global since it needs to be instantiated before class/function definition time.

# Example 1:
# from utils.perf import do_profile, profiler_singleton
#
# @do_profile(profiler=profiler_singleton)
# def yourfunction(...)
#   <your profiled code>
# ... later, outside yourfunction:
# profiler_singleton.print_stats()


# Example 2:
# from utils.perf import do_profile
# from line_profiler import LineProfiler
#
# profiler = LineProfiler()
#
# @do_profile(profiler=profiler)
# def yourfunction(...)
#   <your profiled code>
# ... later, anywhere outside your loop:
# profiler.print_stats()


def do_cprofile(func):
  def profiled_func(*args, **kwargs):
    profile = cProfile.Profile()
    try:
      profile.enable()
      result = func(*args, **kwargs)
      profile.disable()
      return result
    finally:
      profile.print_stats()
  return profiled_func

# Intended for export to other modules.
profiler_singleton = None

try:
  from line_profiler import LineProfiler

  def do_profile(profiler=None, follow=[]):
    def inner(func):
      def profiled_func(*args, **kwargs):
        try:
          # import ipdb; ipdb.set_trace()
          if not profiler:
            _profiler = LineProfiler()
          else:
            _profiler = profiler

          _profiler.add_function(func)
          for f in follow:
            if type(f) is 'string':
              _cls, f = get_class_and_fn_from_str(f)
            _profiler.add_function(f)

          _profiler.enable_by_count()
          return func(*args, **kwargs)
        finally:
          if not profiler:
            _profiler.print_stats()
      return profiled_func
    return inner

  profiler_singleton = LineProfiler()

except ImportError:
  def do_profile(follow=[]):
    "Helpful if you accidentally leave in production!"
    def inner(func):
      def nothing(*args, **kwargs):
        return func(*args, **kwargs)
      return nothing
    return inner



