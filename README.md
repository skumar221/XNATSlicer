Sunil Kumar
kumars at mir.wustl.edu
Last Revision: 12-20-12

Installation Instructions:

WIN64:
	NOTE: Please make sure you have read/write access to the Slicer program folder (i.e. C:\Program Files\Slicer-4.2.x)!
	The module will automatically install PyXNAT once you try to log in. 

MAC / UNIX (untested on UNIX):
	NOTE: This only applies for building from source.  Once Slicer is built from source, you can proceed to the instructions below:
	1) Make sure you have an install of Python 2.6 available.
	2) Navigate to where Python 2.6 was installed (such as '/usr/lib/python2.6') and, from the command line, run "find . -name "*ssl*"".
	3) Copy all of those files to the following directory: <SLICER SOURCE>/python-build/lib/python2.6.  You might have to make some of 
	   the directories such as 'lib-dynload' within '<SLICER SOURCE>/python-build/lib/python2.6'.
	4) Download the setuptools egg for your system, found here: http://pypi.python.org/pypi/setuptools
	5) Put the egg in a directory where you don't mind accessing it via the Slicer command prompt.
	6) From the Slicer Python command prompt, run:
	
		proc = qt.QProcess()
		proc.start("sh <path to setuptools egg>/setuptools-0.6c11-py2.6.egg")
		proc.waitForFinished()
		
		[there should be a file called "easy_install" in '<SLICER SOURCE>/python-build/lib/python2.6']
		
		Then, run the following:
		
		import subprocess
		subprocess.call(["<path to easy install>/easy_install", "httplib2"])
		subprocess.call(["<path to easy install>/easy_install", "lxml"])
		subprocess.call(["<path to easy install>/easy_install", "pyxnat"])
		
	7) You should be able to run "import pyxnat" without errors.