from utils.platform import Platform

from .application import Application


class Thunderbird(Application):

    name = "Thunderbird"
    description = "Mozilla Thunderbird"
    platforms = (Platform.WINDOWS,)
