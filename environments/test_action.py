# import environment cube3
#import sys
#print(sys.path)
from environments.cube3 import Cube3

cube_env = Cube3()

# Test algorithm action expansion
i = 0
for key, value in cube_env.subroutines.items():
    print(i, key, value)
    i += 1

# Testing funcionality of _expand_subroutines
algs = {
            "edge": ["R1", "U1"],
        }
subroutines = cube_env._expand_subroutines(algs)
i = 0
for key, value in subroutines.items():
    print(i, key, value)
    i += 1
