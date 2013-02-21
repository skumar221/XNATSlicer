cmake_minimum_required(VERSION 2.8.9)

#-----------------------------------------------------------------------------
if(NOT Slicer_SOURCE_DIR)
  set(EXTENSION_NAME XNATSlicer)
  set(EXTENSION_HOMEPAGE "http://www.slicer.org/slicerWiki/index.php/Documentation/4.2/Extensions/XNATSlicer")
  set(EXTENSION_CATEGORY "Remote")
  set(EXTENSION_CONTRIBUTORS "Sunil Kumar (Washington University in St. Louis), Dan Marcus (Washington University in St. Louis), Steve Pieper (Isomics)")
  set(EXTENSION_DESCRIPTION "Secure GUI-based IO with any XNAT server. Powered by PyXNAT. Win64 for now.")
  set(EXTENSION_ICONURL "http://wiki.slicer.org/slicerWiki/images/e/e1/XNATSlicerIcon.jpg")
  set(EXTENSION_SCREENSHOTURLS "http://www.slicer.org/slicerWiki/images/4/4c/XNATSlicer-Panel.png")
endif()

#-----------------------------------------------------------------------------
if(NOT Slicer_SOURCE_DIR)
  find_package(Slicer REQUIRED)
  include(${Slicer_USE_FILE})
endif()

#-----------------------------------------------------------------------------
add_subdirectory(XNATSlicer)

#-----------------------------------------------------------------------------
if(NOT Slicer_SOURCE_DIR)
  include(${Slicer_EXTENSION_CPACK})
endif()
