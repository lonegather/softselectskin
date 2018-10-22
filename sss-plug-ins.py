from maya.OpenMayaMPx import MFnPlugin, MPxContext, MPxContextCommand
from maya.OpenMayaUI import M3dView


class SoftSkinningContext(MPxContext):

    def __init__(self):
        super(SoftSkinningContext, self).__init__()
        self.start_x, self.start_y, self.end_x, self.end_y = 0, 0, 0, 0
        self.view = None

    def toolOnSetup(self, *args):
        return super(SoftSkinningContext, self).toolOnSetup(*args)

    def doPress(self, *args):
        self.view = M3dView.active3dView()

    def doDrag(self, *args):
        return super(SoftSkinningContext, self).doDrag(*args)

    def doRelease(self, *args):
        return super(SoftSkinningContext, self).doRelease(*args)


class SoftSkinningContextCommand(MPxContextCommand):
    
    def __init__(self):
        super(SoftSkinningContextCommand, self).__init__()

    def makeObj(self, *args):
        return SoftSkinningContext()

    @staticmethod
    def creator():
        return SoftSkinningContextCommand()


def initializePlugin(obj):
    plugin = MFnPlugin(obj, "Serious Sam", "1.0", "Any")
    status = plugin.registerContextCommand("softSkinningContext", SoftSkinningContextCommand.creator)
    return status


def uninitializePlugin(obj):
    plugin = MFnPlugin(obj)
    status = plugin.deregisterContextCommand("softSkinningContext")
    return status
