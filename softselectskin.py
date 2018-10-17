import pymel.core as pm
import maya.OpenMaya as om


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
    with pm.window(title='Soft Select Skinning') as win:
        with pm.formLayout() as lyt:
            btn1 = pm.button(label='One')
            btn2 = pm.button(label='Two')
            btn3 = pm.button(label='Three')
            pm.formLayout(lyt, e=True, attachForm=[(btn1, 'top', 5)])
            pm.formLayout(lyt, e=True, attachForm=[(btn1, 'left', 5)])
            pm.formLayout(lyt, e=True, attachForm=[(btn2, 'left', 5)])
            pm.formLayout(lyt, e=True, attachForm=[(btn3, 'left', 5)])
            pm.formLayout(lyt, e=True, attachForm=[(btn1, 'right', 5)])
            pm.formLayout(lyt, e=True, attachForm=[(btn2, 'right', 5)])
            pm.formLayout(lyt, e=True, attachForm=[(btn3, 'right', 5)])
            pm.formLayout(lyt, e=True, attachControl=[(btn2, 'top', 5, btn1)])
            pm.formLayout(lyt, e=True, attachControl=[(btn3, 'top', 5, btn2)])
            pm.formLayout(lyt, e=True, attachForm=[(btn3, 'bottom', 5)])
