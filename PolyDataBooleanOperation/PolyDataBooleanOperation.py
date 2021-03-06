import os
import unittest
import vtk, qt, ctk, slicer
from slicer.ScriptedLoadableModule import *
import logging

#
# PolyDataBooleanOperation
#

class PolyDataBooleanOperation(ScriptedLoadableModule):
  """Uses ScriptedLoadableModule base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def __init__(self, parent):
    ScriptedLoadableModule.__init__(self, parent)
    self.parent.title = "PolyDataBooleanOperation" # TODO make this more human readable by adding spaces
    self.parent.categories = ["Examples"]
    self.parent.dependencies = []
    self.parent.contributors =  ["Longquan Chen(SPL)", "Junichi Tokuda (SPL)"]
    self.parent.helpText = """ wrapper of the vtkBooleanOperationPolyDataFilter"""
    self.parent.helpText += self.getDefaultModuleDocumentationLink()
    self.parent.acknowledgementText = """
This file was originally developed by Jean-Christophe Fillion-Robin, Kitware Inc.
and Steve Pieper, Isomics, Inc. and was partially funded by NIH grant 3P41RR013218-12S1.
""" # replace with organization, grant and thanks.

#
# PolyDataBooleanOperationWidget
#

class PolyDataBooleanOperationWidget(ScriptedLoadableModuleWidget):
  """Uses ScriptedLoadableModuleWidget base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def setup(self):
    ScriptedLoadableModuleWidget.setup(self)

    # Instantiate and connect widgets ...
    self.logic = PolyDataBooleanOperationLogic()
    #
    # Parameters Area
    #
    parametersCollapsibleButton = ctk.ctkCollapsibleButton()
    parametersCollapsibleButton.text = "Parameters"
    self.layout.addWidget(parametersCollapsibleButton)

    # Layout within the dummy collapsible button
    parametersFormLayout = qt.QFormLayout(parametersCollapsibleButton)

    #
    # input volume selector
    #
    self.inputSelector1 = slicer.qMRMLNodeComboBox()
    self.inputSelector1.nodeTypes = ["vtkMRMLModelNode"]
    self.inputSelector1.selectNodeUponCreation = True
    self.inputSelector1.addEnabled = False
    self.inputSelector1.removeEnabled = False
    self.inputSelector1.noneEnabled = False
    self.inputSelector1.showHidden = False
    self.inputSelector1.showChildNodeTypes = False
    self.inputSelector1.setMRMLScene( slicer.mrmlScene )
    self.inputSelector1.setToolTip( "Pick the input to the algorithm." )
    parametersFormLayout.addRow("Input Model 1: ", self.inputSelector1)

    self.inputSelector2 = slicer.qMRMLNodeComboBox()
    self.inputSelector2.nodeTypes = ["vtkMRMLModelNode"]
    self.inputSelector2.selectNodeUponCreation = True
    self.inputSelector2.addEnabled = False
    self.inputSelector2.removeEnabled = False
    self.inputSelector2.noneEnabled = False
    self.inputSelector2.showHidden = False
    self.inputSelector2.showChildNodeTypes = False
    self.inputSelector2.setMRMLScene(slicer.mrmlScene)
    self.inputSelector2.setToolTip("Pick the input to the algorithm.")
    parametersFormLayout.addRow("Input Model 2: ", self.inputSelector2)

    #
    # output volume selector
    #
    self.outputSelector = slicer.qMRMLNodeComboBox()
    self.outputSelector.nodeTypes = ["vtkMRMLModelNode"]
    self.outputSelector.selectNodeUponCreation = True
    self.outputSelector.addEnabled = True
    self.outputSelector.removeEnabled = True
    self.outputSelector.noneEnabled = True
    self.outputSelector.showHidden = False
    self.outputSelector.showChildNodeTypes = False
    self.outputSelector.setMRMLScene( slicer.mrmlScene )
    self.outputSelector.setToolTip( "Pick the output to the algorithm." )
    parametersFormLayout.addRow("Output Model: ", self.outputSelector)

    #
    # Algorithm setting
    #
    self.operationTypeSelector = qt.QComboBox()
    for index, value in enumerate(self.logic.operationTypes):
      self.operationTypeSelector.insertItem(index, value)
    parametersFormLayout.addRow("OperationType: ", self.operationTypeSelector)
    #
    # Apply Button
    #
    self.applyButton = qt.QPushButton("Apply")
    self.applyButton.toolTip = "Run the algorithm."
    self.applyButton.enabled = False
    parametersFormLayout.addRow(self.applyButton)

    # connections
    self.applyButton.connect('clicked(bool)', self.onApplyButton)
    self.inputSelector1.connect("currentNodeChanged(vtkMRMLNode*)", self.onSelect)
    self.inputSelector2.connect("currentNodeChanged(vtkMRMLNode*)", self.onSelect)
    self.outputSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.onSelect)
    #self.outputSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.onSelectOutput)

    # Add vertical spacer
    self.layout.addStretch(1)

    # Refresh Apply button state
    self.onSelect()

  def cleanup(self):
    pass

  def onSelect(self):
    self.applyButton.enabled = self.inputSelector1.currentNode() and self.inputSelector2.currentNode() and self.outputSelector.currentNode()

  def onApplyButton(self):
    self.logic.run(self.inputSelector1.currentNode(), self.inputSelector2.currentNode(), self.outputSelector.currentNode(), self.operationTypeSelector.currentIndex)

#
# PolyDataBooleanOperationLogic
#

class PolyDataBooleanOperationLogic(ScriptedLoadableModuleLogic):
  """This class should implement all the actual
  computation done by your module.  The interface
  should be such that other python code can import
  this class and make use of the functionality without
  requiring an instance of the Widget.
  Uses ScriptedLoadableModuleLogic base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """
  def __init__(self, parent = None):
    self.operationTypes = ["Intersection", "Difference", "Union"]

  def isValidInputOutputData(self, inputModel1, inputModel2, outputModel):
    """Validates if the output is not the same as input
    """
    if not inputModel1:
      logging.debug('isValidInputOutputData failed: no input model 1 node defined')
      return False
    if not inputModel2:
      logging.debug('isValidInputOutputData failed: no input model 2 node defined')
      return False
    if not outputModel:
      logging.debug('isValidInputOutputData failed: no output model node defined')
      return False
    if inputModel1.GetID()==outputModel.GetID() or inputModel2.GetID()==outputModel.GetID():
      logging.debug('isValidInputOutputData failed: input and output model is the same. Create a new model for output to avoid this error.')
      return False
    return True

  def run(self, inputModel1, inputModel2, outputModel, operationIndex):
    """
    Run the actual algorithm
    """

    if not self.isValidInputOutputData(inputModel1, inputModel2, outputModel):
      slicer.util.errorDisplay('Input volume is the same as output volume. Choose a different output volume.')
      return False

    logging.info('Processing started')

    triangleFilter1 = vtk.vtkTriangleFilter()
    triangleFilter1.SetInputData(inputModel1.GetPolyData())
    triangleFilter1.Update()
    triangleFilter2 = vtk.vtkTriangleFilter()
    triangleFilter2.SetInputData(inputModel2.GetPolyData())
    triangleFilter2.Update()
    booleanFilter = vtk.vtkBooleanOperationPolyDataFilter()
    if operationIndex == 0:
      booleanFilter.SetOperationToIntersection()
    elif operationIndex == 1:
      booleanFilter.SetOperationToDifference()
    elif operationIndex == 2:
      booleanFilter.SetOperationToUnion()
    booleanFilter.SetInputData(0, triangleFilter1.GetOutput())
    booleanFilter.SetInputData(1, triangleFilter2.GetOutput())
    booleanFilter.Update()
    outputModel.SetAndObservePolyData(booleanFilter.GetOutput())
    outputModel.CreateDefaultDisplayNodes()
    logging.info('Processing completed')

    return True


class PolyDataBooleanOperationTest(ScriptedLoadableModuleTest):
  """
  This is the test case for your scripted module.
  Uses ScriptedLoadableModuleTest base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def setUp(self):
    """ Do whatever is needed to reset the state - typically a scene clear will be enough.
    """
    slicer.mrmlScene.Clear(0)

  def runTest(self):
    """Run as few or as many tests as needed here.
    """
    self.setUp()
    self.test_PolyDataBooleanOperation1()

  def test_PolyDataBooleanOperation1(self):
    """ Ideally you should have several levels of tests.  At the lowest level
    tests should exercise the functionality of the logic with different inputs
    (both valid and invalid).  At higher levels your tests should emulate the
    way the user would interact with your code and confirm that it still works
    the way you intended.
    One of the most important features of the tests is that it should alert other
    developers when their changes will have an impact on the behavior of your
    module.  For example, if a developer removes a feature that you depend on,
    your test should break so they know that the feature is needed.
    """

    self.delayDisplay("Starting the test")
    #
    # first, get some data
    #
    import urllib
    downloads = (
        ('http://slicer.kitware.com/midas3/download?items=5767', 'FA.nrrd', slicer.util.loadVolume),
        )

    for url,name,loader in downloads:
      filePath = slicer.app.temporaryPath + '/' + name
      if not os.path.exists(filePath) or os.stat(filePath).st_size == 0:
        logging.info('Requesting download %s from %s...\n' % (name, url))
        urllib.urlretrieve(url, filePath)
      if loader:
        logging.info('Loading %s...' % (name,))
        loader(filePath)
    self.delayDisplay('Finished with download and loading')

    volumeNode = slicer.util.getNode(pattern="FA")
    logic = PolyDataBooleanOperationLogic()
    self.assertIsNotNone( logic.hasImageData(volumeNode) )
    self.delayDisplay('Test passed!')
