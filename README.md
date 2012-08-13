Use subTransform.py to sync .srt files to the correct movie times
(see the help / docstring for the command line options).

The idea behind this simple program is that the mapping between the 
srt file times (ST) and the movie times (MT) is calculated by an affine transformation:
ST[i] = a*MT[i]  + b.

To find  the transformation, we just need two points - so we take the first and last
subtitles, and fit the transformation according to those points.

Some typical usage examples:

1. subTransform -i <filename>: will calculate the a,b parameters of the affine transform, by asking the user
to give the correct time of the first and last subtitles of the input srt file in the video.

2. subTransform -i <filename> -o <synced srt file>: will calculate a,b as before, and sync the input file, writing
the result to the outfile.

3. subTransform -a <a as float> -b <b as float> --applyTo '<some pattern>' --prefix <some_prefix>: apply the calculated
transformation to multiple files (any files which match the input pattern), and append the prefix to the names
of the output files.



Enjoy!

