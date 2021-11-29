from utils.platform import Platform

from .application import Application


class SpitfireAudio(Application):

    name = "SpitfireAudio"
    description = "Spitfire Audio Management Application"
    platforms = (Platform.WINDOWS,)
