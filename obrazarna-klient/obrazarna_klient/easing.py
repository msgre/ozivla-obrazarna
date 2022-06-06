import math


class EasyInOut:
    def __init__(self, v1, v2, steps):
        self.v1 = v1
        self.v2 = v2
        self.diff = (v2 - v1) / 2
        self.steps = steps
        self.t_const = math.pi / self.steps
        self._step = 0
    
    def get(self, step):
        return self.v1 + self.diff * (1 - math.cos(step * self.t_const))

    def step(self):
        out = self.get(self._step)
        self._step += 1
        return out

    def done(self):
        return self._step >= self.steps
