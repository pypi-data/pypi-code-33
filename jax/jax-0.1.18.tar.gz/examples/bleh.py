import jax.numpy as np

from jax.experimental import stax
from jax.experimental.stax import Conv, Dense, MaxPool, Relu, Flatten, LogSoftmax

# Set up network initialization and evaluation functions
net_init, net_apply = stax.serial(
    Conv(32, (3, 3), padding='SAME'), Relu,
    Conv(64, (3, 3), padding='SAME'), Relu,
    MaxPool((2, 2)), Flatten,
    Dense(128), Relu,
    Dense(10), LogSoftmax,
)

# Initialize parameters, not committing to a batch shape
in_shape = (-1, 28, 28, 1)
out_shape, net_params = net_init(in_shape)

# Apply network
inputs = np.zeros((128, 28, 28, 1))
predictions = net_apply(net_params, inputs)


from jax.experimental import minmax
from jax import jit, grad

# Define a simple squared-error loss
def loss(params, batch):
  inputs, targets = batch
  predictions = net_apply(params, inputs)
  return np.sum((predictions - targets)**2)

# Set up an optimizer
opt_init, opt_update = minmax.momentum(step_size=1e-3, mass=0.9)

# Define a compiled update step
@jit
def step(i, opt_state, batch):
  params = minmax.get_params(opt_state)
  g = grad(loss)(params, batch)
  return opt_update(i, g, opt_state)

# Dummy input data stream
data_generator = ((np.zeros((128, 28, 28, 1)), np.zeros((128, 10)))
                  for _ in range(10))

# Optimize parameters in a loop
opt_state = opt_init(net_params)
for i in range(10):
  opt_state = step(i, opt_state, next(data_generator))
net_params = minmax.get_params(opt_state)
