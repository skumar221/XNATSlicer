#-----------------------------------------------------------------------------
set(MODULE_NAME XNATSlicer)

#-----------------------------------------------------------------------------
set(MODULE_PYTHON_SCRIPTS
  ${MODULE_NAME}.py
  ${MODULE_NAME}Lib/io/XnatAnalyzeLoadWorkflow.py
  ${MODULE_NAME}Lib/io/XnatDeleteWorkflow.py
  ${MODULE_NAME}Lib/io/XnatDicomLoadWorkflow.py
  ${MODULE_NAME}Lib/io/XnatFileLoadWorkflow.py
  ${MODULE_NAME}Lib/io/XnatIo.py
  ${MODULE_NAME}Lib/io/XnatLoadWorkflow.py
  ${MODULE_NAME}Lib/io/XnatSaveWorkflow.py
  ${MODULE_NAME}Lib/io/XnatSceneLoadWorkflow.py
  ${MODULE_NAME}Lib/ui/custom-qt-widgets/AnimatedCollapsible.py
  ${MODULE_NAME}Lib/ui/custom-qt-widgets/FingerTabWidget.py
  ${MODULE_NAME}Lib/ui/custom-qt-widgets/HoverButton.py
  ${MODULE_NAME}Lib/ui/custom-qt-widgets/VariableItemListWidget.py
  ${MODULE_NAME}Lib/ui/settings-widgets/XnatDetailsSettings.py
  ${MODULE_NAME}Lib/ui/settings-widgets/XnatHostSettings.py
  ${MODULE_NAME}Lib/ui/settings-widgets/XnatMetadataEditor.py
  ${MODULE_NAME}Lib/ui/settings-widgets/XnatMetadataSettings.py
  ${MODULE_NAME}Lib/ui/settings-widgets/XnatSettings.py
  ${MODULE_NAME}Lib/ui/settings-widgets/XnatTreeViewSettings.py
  ${MODULE_NAME}Lib/ui/XnatButtons.py
  ${MODULE_NAME}Lib/ui/XnatFolderMaker.py
  ${MODULE_NAME}Lib/ui/XnatLoginMenu.py
  ${MODULE_NAME}Lib/ui/XnatMetadataManager.py
  ${MODULE_NAME}Lib/ui/XnatNodeDetails.py
  ${MODULE_NAME}Lib/ui/XnatSaveDialog.py
  ${MODULE_NAME}Lib/ui/XnatSearchBar.py
  ${MODULE_NAME}Lib/ui/XnatSettingsWindow.py
  ${MODULE_NAME}Lib/ui/XnatTreeView.py
  ${MODULE_NAME}Lib/ui/XnatView.py
  ${MODULE_NAME}Lib/ui/XnatViewer.py
  ${MODULE_NAME}Lib/utils/XnatError.py
  ${MODULE_NAME}Lib/utils/XnatFileInfo.py
  ${MODULE_NAME}Lib/utils/XnatGlobals.py
  ${MODULE_NAME}Lib/utils/XnatMrmlParser.py
  ${MODULE_NAME}Lib/utils/XnatPopup.py
  ${MODULE_NAME}Lib/utils/XnatScenePackager.py
  ${MODULE_NAME}Lib/utils/XnatSessionManager.py
  ${MODULE_NAME}Lib/utils/XnatSettingsFile.py
  ${MODULE_NAME}Lib/utils/XnatTimer.py
  ${MODULE_NAME}Lib/utils/XnatUtils.py
  )

set(MODULE_PYTHON_RESOURCES
  Resources/Icons/${MODULE_NAME}.png
  ${MODULE_NAME}Lib/icons/addproj.jpg
  ${MODULE_NAME}Lib/icons/delete.jpg
  ${MODULE_NAME}Lib/icons/load.jpg
  ${MODULE_NAME}Lib/icons/save.jpg
  ${MODULE_NAME}Lib/icons/update.jpg
  ${MODULE_NAME}Lib/icons/wrench.png
  Resources/Icons/addproj.png
  Resources/Icons/delete.png
  Resources/Icons/eye.png
  Resources/Icons/gear.png
  Resources/Icons/load.png
  Resources/Icons/save.png
  Resources/Icons/search.png
  Resources/Icons/test.png
  Resources/Icons/wrench.png
  Resources/Icons/x.png
  Resources/Icons/XNATSlicer-MarketIcon.png
  Resources/Images/DeveloperDesc_MainPanel.png
  Resources/Images/UserDesc_MainPanel.png
  Resources/Images/XNATSlicer-MainIcon.png
  ${MODULE_NAME}Lib/ui/custom-qt-widgets/wrench.png
  )

#-----------------------------------------------------------------------------
slicerMacroBuildScriptedModule(
  NAME ${MODULE_NAME}
  SCRIPTS "${MODULE_PYTHON_SCRIPTS}"
  RESOURCES "${MODULE_PYTHON_RESOURCES}"
  )

#-----------------------------------------------------------------------------
if(BUILD_TESTING)

  # this will regiester the unittest subclass in the main script
  # as a ctest (note that it is also usable as a runtime test).
  slicer_add_python_unittest(SCRIPT ${MODULE_NAME}.py)

  # additional build-time testing goes in here
  add_subdirectory(Testing)
endif()
