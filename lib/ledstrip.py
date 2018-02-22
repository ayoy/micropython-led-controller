import pycom

class LEDStrip:
    DISABLED = const(-1)

    def __init__(self):
        self._r = pycom.nvs_get('red') or 0
        self._g = pycom.nvs_get('green') or 20
        self._b = pycom.nvs_get('blue') or 40
        self._fading = pycom.nvs_get('fading') or False
        self._schedule_start = pycom.nvs_get('schedule_start') or self.DISABLED
        self._schedule_stop = pycom.nvs_get('schedule_stop') or self.DISABLED


    @property
    def enabled(self):
        return self.r > 0 or self.g > 0 or self.b > 0


    # red
    @property
    def r(self):
        return self._r


    @r.setter
    def r(self, value):
        self._r = value
        pycom.nvs_set('red', value)

    # green
    @property
    def g(self):
        return self._g


    @g.setter
    def g(self, value):
        self._g = value
        pycom.nvs_set('green', value)

    # blue
    @property
    def b(self):
        return self._b


    @b.setter
    def b(self, value):
        self._b = value
        pycom.nvs_set('blue', value)

    # fading
    @property
    def fading(self):
        return self._fading


    @fading.setter
    def fading(self, value):
        self._fading = value
        pycom.nvs_set('fading', value)

    # schedule_stop (in minutes 0-1439)
    @property
    def schedule_stop(self):
        return self._schedule_stop


    @schedule_stop.setter
    def schedule_stop(self, value):
        self._schedule_stop = value
        pycom.nvs_set('schedule_stop', value)

    # schedule_start (in minutes 0-1439)
    @property
    def schedule_start(self):
        return self._schedule_start


    @schedule_start.setter
    def schedule_start(self, value):
        self._schedule_start = value
        pycom.nvs_set('schedule_start', value)
