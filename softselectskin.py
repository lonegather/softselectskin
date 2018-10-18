import os
import pymel.core as pm
import maya.OpenMaya as om


__all__ = ['soft_selection', 'show']


main_window_flags = {
    'title': 'Soft Select Skinning',
    'maximizeButton': False,
    'minimizeButton': False,
    'resizeToFitChildren': True,
    'dockCorner': ['topLeft', 'left'],
}

softselect_frame_flags = {
    'label': 'Soft Selection',
    'collapsable': True
}

skeleton_frame_flags = {
    'label': 'Skeletons',
    'collapsable': True
}

falloff_radius_slider_flags = {
    'label': 'Radius',
    'field': True,
    'minValue': 0.0,
    'maxValue': 100.0,
    'fieldMinValue': 0.0,
    'fieldMaxValue': 100.0,
    'changeCommand': lambda d: pm.softSelect(e=True, softSelectDistance=d),
}

falloff_curve_flags = {
    'h': 120,
    'changeCommand': lambda c: pm.softSelect(e=True, softSelectCurve=c),
}

skeleton_list_flags = {
    'allowMultiSelection': False,
}


try:
    pm.condition("SoftSelectParamsChanged", state=True)
except RuntimeError:
    pass
pm.mel.eval('source "%s/override.mel";' % os.path.dirname(__file__).replace('\\', '/'))


def soft_selection():
    selection = om.MSelectionList()
    rich_selection = om.MRichSelection()
    om.MGlobal.getRichSelection(rich_selection)
    rich_selection.getSelection(selection)

    dag_path = om.MDagPath()
    component = om.MObject()

    iter = om.MItSelectionList(selection, om.MFn.kMeshVertComponent)
    elements = []
    weights = []
    while not iter.isDone():
        iter.getDagPath(dag_path, component)
        dag_path.pop()
        fn_comp = om.MFnSingleIndexedComponent(component)

        for i in range(fn_comp.elementCount()):
            elements.append(fn_comp.element(i))
            weights.append(fn_comp.weight(i).influence())
        iter.next()
    return elements, weights


def softselect_changed_callback_generator(slider, curve):

    def callback():
        current_radius = pm.softSelect(q=True, softSelectDistance=True)
        current_curve = pm.softSelect(q=True, softSelectCurve=True)
        pm.floatSliderGrp(slider, e=True, value=current_radius)
        pm.gradientControlNoAttr(curve, e=True, asString=current_curve)

    return callback


def selection_changed_callback_generator(text_list):

    def callback():
        print 'testing...'
        try:
            current = pm.ls(sl=True)
        except IndexError:
            print 'None'
            return
        current_obj = current[0].name().split('.')[0]
        if not pm.objectType(current_obj, isType='transform'):
            print 'None'
            return
        current_shape = pm.listRelatives(current_obj)[0]
        if not current_shape:
            print 'None'
            return
        skin_cluster = pm.listConnections(current_shape, d=False, type="skinCluster")[0]
        print pm.skinCluster(skin_cluster, q=True, influence=True)

    return callback


def show():
    if pm.window('softselectskin', exists=True):
        pm.deleteUI('softselectskin')
    with pm.window('softselectskin', **main_window_flags) as win:
        with pm.formLayout('main_form') as main_layout:
            with pm.frameLayout('softselect_frame', **softselect_frame_flags) as softselect_framelayout:
                with pm.formLayout('softselect_form') as lyt:
                    current_radius = pm.softSelect(q=True, softSelectDistance=True)
                    current_curve = pm.softSelect(q=True, softSelectCurve=True)
                    slider = pm.floatSliderGrp('fsg_radius', value=current_radius, **falloff_radius_slider_flags)
                    curve = pm.gradientControlNoAttr('gc_curve', asString=current_curve, **falloff_curve_flags)
                    callback = softselect_changed_callback_generator(slider, curve)
                    pm.scriptJob(conditionChange=["SoftSelectParamsChanged", callback], parent=win)

                    attach = {
                        'e': True,
                        'attachForm': [
                            (slider, 'top', 5),
                            (slider, 'left', 5),
                            (slider, 'right', 20),
                            (curve, 'left', 5),
                            (curve, 'right', 5),
                        ],
                        'attachControl': [
                            (curve, 'top', 5, slider),
                        ]
                    }

                    pm.formLayout(lyt, **attach)

            with pm.frameLayout('skeleton_frame', **skeleton_frame_flags) as skeleton_framelayout:
                with pm.formLayout('skeleton_formlayout') as skeleton_formlayout:
                    tsl = pm.textScrollList('skeleton_list', **skeleton_list_flags)
                    callback = selection_changed_callback_generator(tsl)
                    pm.scriptJob(event=['SelectionChanged', callback], parent=win)

                    attach = {
                        'e': True,
                        'attachForm': [
                            (tsl, 'top', 5),
                            (tsl, 'left', 5),
                            (tsl, 'right', 5),
                        ],
                    }

                    pm.formLayout(skeleton_formlayout, **attach)

            attach = {
                'e': True,
                'attachForm': [
                    (softselect_framelayout, 'top', 5),
                    (softselect_framelayout, 'left', 5),
                    (softselect_framelayout, 'right', 5),
                    (skeleton_framelayout, 'left', 5),
                    (skeleton_framelayout, 'right', 5),
                ],
                'attachControl': [
                    (skeleton_framelayout, 'top', 5, softselect_framelayout),
                ]
            }

            pm.formLayout(main_layout, **attach)
