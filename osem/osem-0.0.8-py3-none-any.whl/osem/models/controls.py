from osem.models.base import Model


class Hysteresis(Model):
    """Model class of a hysteresis controller"""
    #TODO DevMaster: What is the purpose of this class missing documentation

    def __init__(self, x_max=1.0, x_min=0.0, y_init=0, start="1/1/2000"):
        super().__init__(start)
        self.x_max = x_max
        self.x_min = x_min

        self.x = 0.0
        self.y = y_init

    def step(self, step, unit="seconds"):
        super().step(step, unit)
        if self.y and self.x >= self.x_max:
            self.y = 0
        if not self.y and self.x <= self.x_min:
            self.y = 1
