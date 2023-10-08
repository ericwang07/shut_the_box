ShutTheBox:
	echo "#!/bin/bash" > ShutTheBox
	echo "pypy3 main.py \"\$$@\"" >> ShutTheBox
	chmod u+x ShutTheBox
