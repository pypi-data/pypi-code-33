class WandbMixin(object):
    def generate_pod_spec(self):
        pod_spec = super(WandbMixin, self).generate_pod_spec()
        print("DAMN", pod_spec)
