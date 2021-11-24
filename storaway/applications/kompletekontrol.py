from utils.platform import Platform

from .application import Application


class KompleteKontrol(Application):

    name = "KompleteKontrol"
    description = "Native Instruments Komplete Kontrol"
    platforms = (Platform.WINDOWS,)
