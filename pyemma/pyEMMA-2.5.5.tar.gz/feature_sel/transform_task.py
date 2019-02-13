from celery import Celery, group

broker_url = 'amqp://marscher:foobar@wallaby:5672/myvhost'
app = Celery('transform_task', broker=broker_url)


test_systems = ['1FME', '2F4K', '2JOF', '2WAV', 'A3D', 'CLN025', 'GTT', 'lambda', 'NuG2', 'PRB', 'UVF',
                'NTL9-0-protein_fixed_CC'
                ]

@app.task
def transform_angles_cossin(file):
    print('transforming: ', file)
    import tables
    import h5py as h
    def t(rad):
        import numpy as np

        rad = np.dstack((np.cos(rad), np.sin(rad)))
        rad = rad.reshape(rad.shape[0], rad.shape[1]*rad.shape[2])
        return rad

    with h.File(file, mode='a') as f:
        ds = f['/backbone']
        new_shape = ds.shape[0], ds.shape[1] * 2
        try:
            del f['backbone_cossin']
        except KeyError: pass
        trans = t(ds[:,:])
        new_dataset = f.create_dataset('backbone_cossin', shape=new_shape, chunks=True,
                                       compression=32001, data=trans)

if __name__ == '__main__':
    transform_angles_cossin('/group/ag_cmb/marscher/feature_sel/lambda-0-protein-070.dcd_backbone.h5')


