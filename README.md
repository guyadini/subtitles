Use subTransform.py to sync .srt files to the correct movie times
(see the help / docstring for the command line options).

The idea behind this simple program is that the mapping between the 
srt file times (ST) and the movie times (MT) is calculated by an affine transformation:
ST[i] = a*MT[i]  + b.

To find  the transformation, we just need two points - so we take the first and last
subtitles, and fit the transformation according to those points.

Enjoy!

