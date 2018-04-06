algorithmic-musician
=====

Senior Project, Elliot Miller, 2016

# Quick-Start Guide

This project was written in Python 2.7.10. There are two main programs that can
be run in this project:

1. Command line interface
2. Web server interface

# Setup

Make sure Python 2.7 is installed along with tkinter, matplotlib, and pyaudio.
On a debian-based system you can install all the requirements with:

    [sudo] apt install python2.7 python-tk python-pip python-pyaudio
    [sudo] pip install matplotlib

# Command line interface

From the root directory of this project, run the command,

    python generator.py [filename]

Where `filename` is the path to the waveform file you want the program to
analyze and generate music from.

To play a wavefile you can use the `player.py` program:

    python player.py filename.wav

# Web interface

From the root directory of this project, run the command,

    python server.py

Python should immediatly start a local web server on port 8080. If it was
successful, python will print out `Started httpserver on port  8080`. Open a
web browser to [localhost:8080](http://localhost:8080/) to use the program.
