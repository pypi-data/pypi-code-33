import waverunner
from waverunner import Server
import argparse

try:
    import xarray as xr
except ImportError:
    pass

import numpy as np

from scipy.interpolate import interp1d

try:
    from .Pyspectre import hash_tests
except:
    from pyspectre.Pyspectre import hash_tests


def run_batch(circuit, stimuli, time_vec, signal_names='all', dtype='float32', return_type='ndarray'):

    # print('running_batch of {} simulations.'.format(len(stimuli)))
    if signal_names is None or not signal_names:
        signal_names = 'all'
    times, signals = circuit.run_batch(stimuli, time_vec, signal_names)

    times = np.array(times)
    ids = np.array(hash_tests(stimuli, time_vec))

    # new_timespan = times.min(axis=1), times.max(axis=1)
    # new_time = np.linspace(new_timespan[0], new_timespan[1], stimuli[0].shape[-1])

    for i, (t, s) in enumerate(zip(times, signals)):
        signals[i] = interp1d(t, s, bounds_error=False, fill_value=(s[:, 0], s[:, -1]))(time_vec)

    if return_type == 'xarray':
        data = xr.DataArray(
            data=np.stack(signals).astype(dtype),
            coords=[ids, signal_names, time_vec.astype(dtype)],
            dims=['id', 'name', 'time'],
            name=str(id(stimuli)),
        )

    elif return_type == 'ndarray' or return_type == 'numpy':
        data = np.stack(signals).astype(dtype)

    return data


def start_server(port=None,
                 remote_ips=None,
                 polling_interval=0,
                 notify_interval=0,
                 worker_processes=False,
                 max_n_workers=None,
                 verbosity=0):

    server = waverunner.Waverunner(port=port,
                                   remote_ips=remote_ips,
                                   polling_interval=polling_interval,
                                   notify_interval=notify_interval,
                                   worker_processes=worker_processes,
                                   max_n_workers=max_n_workers,
                                   verbosity=verbosity)

    server.register_secure_method(run_batch)

    try:
        server.serve_forever()

    except:
        server.stop_service()

    finally:
        server.exit_gracefully()


def main():
    # parser = argparse.ArgumentParser()
    # parser.add_argument('--port', '-p', action='store')
    # parser.add_argument('--remote_ips', '-r', action='store')
    # parser.add_argument('--polling-interval', '-I', action='store', type=int)
    # parser.add_argument('--notify-interval', '-i', action='store', type=int)
    # parser.add_argument('--verbosity', '-v', action='store', type=int, default=1)
    # parser.add_argument('--multiprocess', '-m', action='store_true')
    # parser.add_argument('--num-workers', '-n', type=int, default=None)
    #
    # args = parser.parse_args()
    #
    # start_server(port=args.port,
    #              remote_ips=args.remote_ips,
    #              polling_interval=args.polling_interval,
    #              notify_interval=args.notify_interval,
    #              worker_processes=args.multiprocess,
    #              max_n_workers=args.num_workers,
    #              verbosity=args.verbosity)

    server = Server.main()
    server.register_secure_method(run_batch)

    try:
        server.serve_forever()

    # except Exception as e:
    #     raise e

    finally:
        server.exit_gracefully()


if __name__ == '__main__':
    main()
