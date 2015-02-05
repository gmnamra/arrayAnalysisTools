# Anthony Ho, ahho@stanford.edu, 2/3/2015
# Last update 2/4/2015
""" Library containing some commonly used mathematical functions and their derivatives """


import numpy as np


# Compute A*exp(-kt) + C
# where params[0] = A
#       params[1] = k
#       params[2] = C
def singleExp(params, x):
    return params[0]*np.exp(-params[1]*x) + params[2]

# Compute the Jacobian of singleExp
# Returns a 2D-ndarray of shape (len(params), len(x)) 
def singleExpPrime(params, x):
    partial_p0s = np.exp(-params[1]*x)
    partial_p1s = -params[0]*x*np.exp(-params[1]*x)
    partial_p2s = np.ones(len(x))
    return np.vstack([partial_p0s, partial_p1s, partial_p2s])

# Compute (A1*exp(-k1t) + A2)*exp(-k2t) + C
# where params[0] = A1
#       params[1] = k1
#       params[2] = A2
#       params[3] = k2
#       params[4] = C
def doubleExp(params, x):
    return params[0]*np.exp(-(params[1]+params[3])*x) + params[2]*np.exp(-params[3]*x) + params[4]

# Compute the Jacobian of singleExp
# Returns a 2D-ndarray of shape (len(params), len(x)) 
def doubleExpPrime(params, x):
    partial_p0s = np.exp(-(params[1]+params[3])*x)
    partial_p1s = -params[0]*x*np.exp(-(params[1]+params[3])*x)
    partial_p2s = np.exp(-params[3]*x)
    partial_p3s = -params[2]*x*np.exp(-params[3]*x)
    partial_p4s = np.ones(len(x))
    return np.vstack([partial_p0s, partial_p1s, partial_p2s, partial_p3s, partial_p4s])
