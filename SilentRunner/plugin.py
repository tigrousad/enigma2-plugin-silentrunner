"""
description = "SilentRunner - Background Script Manager by tigrousad"
"""

from Plugins.Plugin import PluginDescriptor

from .version import PLUGIN_NAME, PLUGIN_DESCRIPTION


def _open_plugin(session, **kwargs):
    """Open the main SilentRunner screen."""
    try:
        from .main import SilentRunnerScreen
        session.open(SilentRunnerScreen)
    except Exception as e:
        print(f"[SilentRunner] Could not open screen: {e}")


def Plugins(**kwargs):
    return [
        PluginDescriptor(
            name=PLUGIN_NAME,
            description=PLUGIN_DESCRIPTION,
            where=PluginDescriptor.WHERE_PLUGINMENU,
            icon="plugin.png",
            fnc=_open_plugin,
        ),
    ]
