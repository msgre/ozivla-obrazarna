import math


class EasyInOut:
    def __init__(self, pos1, pos2, steps):
        self.pos1 = pos1
        self.pos2 = pos2
        self.diff = ((pos2[0] - pos1[0]) // 2, (pos2[1] - pos1[1]) // 2)
        self.steps = steps
        self.t_const = math.pi / self.steps
        self._step = 0
    
    def get(self, step):
        v = (1 - math.cos(step * self.t_const))
        return (int(round(self.pos1[0] + self.diff[0] * v)), int(round(self.pos1[1] + self.diff[1] * v)))

    def step(self):
        out = self.get(self._step)
        self._step += 1
        return out

    def done(self):
        return self._step > self.steps
