import pycom

class LEDStrip:
    DISABLED = const(-1)

    def __init__(self):
        self._r = pycom.nvs_get('red') or 0
        self._g = pycom.nvs_get('green') or 20
        self._b = pycom.nvs_get('blue') or 40
        self._fading = pycom.nvs_get('fader') or False
        self._fading_start = pycom.nvs_get('fading_start') or self.DISABLED
        self._fading_stop = pycom.nvs_get('fading_stop') or self.DISABLED

    @property
    def enabled(self):
        return self.r > 0 and self.g > 0 and self.b > 0

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

    # fading_stop (in minutes 0-1439)
    @property
    def fading_stop(self):
        return self._fading_stop


    @fading_stop.setter
    def fading_stop(self, value):
        self._fading_stop = value
        pycom.nvs_set('fading_stop', value)

    # fading_start (in minutes 0-1439)
    @property
    def fading_start(self):
        return self._fading_start


    @fading_start.setter
    def fading_start(self, value):
        self._fading_start = value
        pycom.nvs_set('fading_start', value)
