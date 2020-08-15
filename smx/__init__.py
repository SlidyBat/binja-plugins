from binaryninja import *
from .sparch import SourcePawn, SourceMod
from .smxview import SmxView

# Arch
SourcePawn.register()

# Platform
sm = SourceMod(Architecture['sourcepawn'])
sm.register('sourcemod')

# View
SmxView.register()