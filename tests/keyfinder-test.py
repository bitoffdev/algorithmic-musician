"""
keyfinder-test.py - tests the keyfinder class
:author: Elliot Miller

Usage: python keyfinder-test.py
"""
# ******************************************************************************
# Add the parent directory to Python's list of paths to search for modules
import sys
sys.path.append("../")
# ******************************************************************************
if __name__=="__main__":
    import keyfinder

    assert(keyfinder.key([261.6, 293.7, 329.6, 349.2, 392.0, 440.0, 493.9])=="C")
    assert(keyfinder.key([277.2, 311.1, 349.2, 370.0, 415.3, 466.2, 523.3, 554.4])=="C#")
    assert(keyfinder.key([293.7, 329.6, 370.0, 392.0, 440.0, 493.9, 554.4, 587.3])=="D")
    print "Tests succeded!"
