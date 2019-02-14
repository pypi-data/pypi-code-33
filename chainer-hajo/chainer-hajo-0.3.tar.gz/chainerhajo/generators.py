import chainer
import chainer.functions as F
import chainer.links as L


class SynthAndGate(chainer.Chain):
    def __init__(self, n_in, n_mid, n_out, ksize=1, stride=1, pad=0, initialW=None, apply_tanh=True):
        super(SynthAndGate, self).__init__()
        self.n_out_blocks = n_mid // n_out
        assert(self.n_out_blocks*n_out == n_mid)
        self.apply_tanh = apply_tanh
        if initialW is None:
            initialW1 = chainer.initializers.Normal(0.05)
            initialW2 = chainer.initializers.Normal(0.25)
        else:
            initialW1 = initialW
            initialW2 = initialW
        with self.init_scope():
            self.synth=L.Convolution2D(n_in, n_mid, ksize=ksize, stride=stride, pad=pad, initialW=initialW1)
            self.gate=L.Convolution2D(n_in, n_mid, ksize=ksize, stride=stride, pad=pad, initialW=initialW2)

    def __call__(self, x):
        synth = self.synth(x)
        if self.apply_tanh:
            synth = F.tanh(synth)
        gate = F.sigmoid(self.gate(x))
        x = synth * gate
        n,f,sy,sx = x.shape
        x = x.reshape( (n,f//self.n_out_blocks,self.n_out_blocks,sy,sx) )
        x = F.sum(x, axis=2)
        return x
