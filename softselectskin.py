import pymel.core as pm
import maya.OpenMaya as om


__all__ = ['soft_selection', 'show']


main_window_flags = {
    'title': 'Soft Select Skinning',
    'widthHeight': [360, 640],
    'maximizeButton': False,
    'minimizeButton': False,
    'sizeable': True,
}


falloff_radius_slider_flags = {
    'label': 'Radius',
    'field': True,
    'minValue': 0.0,
    'maxValue': 100.0,
    'fieldMinValue': 0.0,
    'fieldMaxValue': 100.0,
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


def show():
    if pm.window('softselectskin', exists=True):
        pm.deleteUI('softselectskin')
    with pm.window('softselectskin', **main_window_flags) as win:
        with pm.formLayout() as main_layout:
            with pm.frameLayout(label='Soft Selection') as soft_select_framelayout:
                with pm.formLayout() as lyt:
                    current_radius = pm.softSelect(q=True, softSelectDistance=True)
                    current_curve = pm.softSelect(q=True, softSelectCurve=True)
                    slider = pm.floatSliderGrp('sss_fd', value=current_radius, **falloff_radius_slider_flags)
                    print slider
                    curve = pm.gradientControlNoAttr(h=120, asString=current_curve)

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

            with pm.frameLayout(label='Skeletons') as skeleton_framelayout:
                with pm.formLayout():
                    pass

            attach = {
                'e': True,
                'attachForm': [
                    (soft_select_framelayout, 'top', 5),
                    (soft_select_framelayout, 'left', 5),
                    (soft_select_framelayout, 'right', 5),
                    (skeleton_framelayout, 'left', 5),
                    (skeleton_framelayout, 'right', 5),
                ],
                'attachControl': [
                    (skeleton_framelayout, 'top', 5, soft_select_framelayout),
                ]
            }

            pm.formLayout(main_layout, **attach)
