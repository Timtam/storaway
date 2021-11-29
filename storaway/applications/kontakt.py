from utils.platform import Platform

from .application import Application


class Kontakt(Application):

    name = "Kontakt"
    description = "Native Instruments Kontakt Library Database"
    platforms = (Platform.WINDOWS,)
