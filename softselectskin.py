import pymel.core as pm
import maya.OpenMaya as om
import maya.OpenMayaUI as omui


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
    'label': 'Falloff Radius: ',
    'field': True,
    'minValue': 0.0,
    'maxValue': 100.0,
    'fieldMinValue': 0.0,
    'fieldMaxValue': 100.0,
    'columnWidth': [1, 100],
    'changeCommand': lambda d: pm.softSelect(e=True, softSelectDistance=d),
}

falloff_curve_display_flags = {
    'label': 'Falloff Curve: ',
    'width': 100,
    'align': 'right',
}

falloff_curve_flags = {
    'height': 120,
    'changeCommand': lambda c: pm.softSelect(e=True, softSelectCurve=c),
}

skeleton_list_flags = {
    'height': 120,
    'allowMultiSelection': False,
}


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

    def callback(cmd, _):
        if not (cmd.count('softSelect ') and pm.window('softselectskin', exists=True)): return
        current_radius = pm.softSelect(q=True, softSelectDistance=True)
        current_curve = pm.softSelect(q=True, softSelectCurve=True)
        try:
            pm.floatSliderGrp(slider, e=True, value=current_radius)
            pm.gradientControlNoAttr(curve, e=True, asString=current_curve)
        except NameError:
            pass

    return callback


def selection_changed_callback_generator(text_list):

    def callback():
        try:
            current = pm.ls(sl=True)
            current_obj = current[0].name().split('.')[0]
            if pm.objectType(current_obj, isType='transform'):
                current_obj = pm.listRelatives(current_obj)[0]
            skin_cluster = pm.listConnections(current_obj, d=False, type="skinCluster")[0]
        except IndexError:
            text_list.removeAll()
            return
        text_list.removeAll()
        for joint in pm.skinCluster(skin_cluster, q=True, influence=True):
            text_list.append(joint)

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
                    with pm.formLayout('curve_formlayout') as curve_formlayout:
                        curve_display = pm.text('curve_display', **falloff_curve_display_flags)
                        curve = pm.gradientControlNoAttr('gc_curve', asString=current_curve, **falloff_curve_flags)

                        attach = {
                            'e': True,
                            'attachForm': [
                                (curve_display, 'top', 0),
                                (curve_display, 'bottom', 0),
                                (curve_display, 'left', 0),
                                (curve, 'top', 0),
                                (curve, 'bottom', 0),
                                (curve, 'right', 0),
                            ],
                            'attachControl': [
                                (curve, 'left', 0, curve_display),
                            ]
                        }

                        pm.formLayout(curve_formlayout, **attach)

                    callback = softselect_changed_callback_generator(slider, curve)
                    callback_id = om.MCommandMessage.addCommandCallback(callback)

                    attach = {
                        'e': True,
                        'attachForm': [
                            (slider, 'top', 5),
                            (slider, 'left', 5),
                            (slider, 'right', 5),
                            (curve_formlayout, 'left', 5),
                            (curve_formlayout, 'right', 5),
                        ],
                        'attachControl': [
                            (curve_formlayout, 'top', 5, slider),
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

    omui.MUiMessage.addUiDeletedCallback(win, lambda *_: om.MMessage.removeCallback(callback_id))
