#!/usr/bin/env python3
'''
License:    The author (Ronald S. Burkey) declares that this program
            is in the Public Domain (U.S. law) and may be used or 
            modified for any purpose whatever without licensing.
Filename:   parseCommandLine.py
Purpose:    Parses the XCOM-I command line and provides variables 
            containing the parsed command-line options.
Requires:   Python 3.6 or later.
Reference:  http://www.ibibio.org/apollo/Shuttle.html
Mods:       2024-03-27 RSB  Began experimenting with this concept.
'''

import sys
import os
import re
import datetime

def TIME(): # Equivalent to the XPL built-in.
    now = datetime.datetime.now()
    return  now.hour * 360000 + \
            now.minute * 6000 + \
            now.second * 100 + \
            now.microsecond // 10000
TIME_OF_GENERATION = TIME()

'''
# A nifty way to trap unwanted calls to `print`.
import builtins
orig_print = builtins.print
def my_print(*args, **kwargs):
    orig_print(*args, **kwargs)
    if ("file" not in kwargs):
        breakpoint()
builtins.print = my_print
'''

# `newHex` affects the algorithm for replacing "..." by numbers.  If False, then
# my original method is to replace numbers in non-decimal bases by tokens like
# 0x..., 0q..., 0o..., and 0b....  However, I found that that broke the weird
# `XSET` macro in HAL/S-FC source code, which can precede either decimal numbers
# or double-quoted strings, but gets confused if preceding something like 0x....
# The new algorithm simply replaces the double-quoted string by their decimal-
# number equivalents immediately. I'll likely want to just eliminate the old
# algorithm at some point.
newHex = True # ***DEBUG***

ifdefs = set()
inputFilenames = []
targetLanguage = "C"
outputFolder = None
indent = "  "
debugSink = None
lines = [] # One line of source code per entry.
lineRefs = [] # One reference (filename:number) for each line of source code.
pseudoStatements = [] # One pseudo-statement per entry. See the 
psRefs = [] # One index into `lineRefs` for each `pseudoStatement`
#sourceFiles = [] # Source filename for each line.
verbose = True
includeFolder = "../HALINCL" # Folder for /%INCLUDE ... %/ directives.
baseSource = None
adhocs = {}
standardXPL = False
identifierString = 'REL32V0   '  # String returned by MONITOR(23)
merge = None
firstFile = True
noInclusionDirectives = False
showBacktrace = False
physicalTop = 1 << 24
keepUnused = False
optproc = "COMPOPT_"

'''
McKeeman et al. does not specify the packing of the bits in memory for a BIT(n)
value.  This seems relatively easy to deduce from other clues for n<=32 because
in that case the BIT(n) values are supposed to behave like integers.
But for n>32, I haven't been able to deduce it from any clues or from code.
It's a serious problem because it means that if we get it wrong, there is a 
mismatch between the way the compiler packs INITIAL values for BIT(n) and the
way XPL programs use those values.  It also affects how `putBIT` masks off 
unused positions when n is not an exact multiple of 8.

Consequently, I've having to experiment with different packings, to see if any 
of them are more-congenial with the original XCOM program than others.  The 
packing is determined by the bitPacking` variable in Python or the `BIT_PACKING`
preprocessor constant (but having the same value as `bitPacker`) in C.  The 
values are interpreted like so:
    1   The rightmost bit (in an INITIAL "(1) ...") correspoinds to bit 0 in 
        the byte that's highest in memory.
    2   The leftmost bit corresponds to bit 7 in the byte that's lowest in 
        memory.  (I.e., the same bit-or as for bitPacking=1, but they may be
        aligned differently if n is not a multiple of 8.
    3.  TBD
'''
bitPacking = 2 # 2 appears to be the correct value to use.
# The characters used internally to replace spaces and duplicated single-quotes
# within quoted strings.  The exact values aren't important, except insofar as
# they shouldn't be something that would otherwise appear in XPL strings, but
# which are characters that won't cause Python to have a
# conniption.  I've chosen DC2 and DC4 control characters because they're the
# same in ASCII & EBCDIC, but that's just arbitrary.  I originally used
# ~ and ` since they weren't in the character set originally supported by XPL,
# but I've realized belately that my own instructions that logical-not and
# U.S.-cent should be replaced by them make it likely that they could in fact
# appear in strings *now*, particularly for macro definitions.
replacementQuote = "\x12"
replacementSpace = "\x14"
# Folder where XCOM-I.py itself is.
basePath = os.path.dirname(os.path.realpath(__file__)) + "/"
libFile = basePath + "SPACELIB.xpl"

# Raw read of a source-code file.  Recursive, if /%INCLUDE ... %/ directives
# (and similar) are encountered.
def readFileIntoLines(filename):
    global inputFilenames, lines
    # global sourceFiles
    if filename in inputFilenames:
        return
    try:
        inputFilenames.append(filename)
        f = open(filename, "r")
        lineNumber = 0
        for line in f:
            lineNumber += 1
            if "$%" in line:
                pass
            lines.append(line)
            lineRefs.append("%s:%d" % (filename, lineNumber))
            #sourceFiles.append(os.path.basename(filename))
            if not noInclusionDirectives:
                if "/%INCLUDE" in line:
                    fields = line.split()
                    readFileIntoLines(dirHALINCL + "/" + fields[1] + ".xpl")
                elif None != re.search('/\\*.*\\$%.*\\*/', line):
                    # In case it isn't obvious, this was looking for 
                    # $%filename directives within a comment.
                    basename = line[:80].split('$%')[1]
                    basename = basename.split('*')[0].split()[0]
                    readFileIntoLines(dirHALINCL + "/" + basename + ".xpl")
                elif line.lstrip().startswith('/**MERGE'):
                    fields =line.lstrip().split()
                    if baseSource != "":
                        readFileIntoLines(baseSource + "/" + fields[1] + ".xpl")
                    else:
                        readFileIntoLines(fields[1] + ".xpl")
        f.close()
    except:
        print("Failed to read file %s" % filename, file = sys.stderr)
        sys.exit(1)

# Parse the command line, reading the lines of XPL source code in the
# process.
helpMsg = '''
Usage:
    XCOM-I.py [OPTIONS] FILE1.xpl [ FILE2.xpl [ ... ] ]

The available OPTIONS are:

--help          Print this info.
--              If this is found, it means to skip the entire remainder of the
                command line.
--xpl           Compile standard XPL rather than XPL/I.
--lib-file=F    (Default SPACELIB.xpl, or XPL.LIBRARY.xpl if the --xpl option
                is used.)  Specifies a "library file" of XPL source code to 
                include prior to any of the XPL files specified on the command 
                line.  Note that if both --xpl and --lib-file are used, then
                --xpl must *precede* --lib-file on the command line; both must
                precede the names of the first source-code file specified.
--cond=c        XPL/I source-code files can contain code which is conditionally
                included or excluded, using the syntax
                    /?c...code...?/
                Here, c is a single upper-case alphabetical character.  This
                would be similar, for example, to "#ifdef c" in the C computer
                language.  Multiple --cond switches can appear on the same
                command line. In the XPL/I source code for the HAL/S-FC program,
                the relevant choices are:
                    c=P    For the Primary Flight Software (PFS).
                    c=B    For the Backup Flight Software (PFS).
                    c=A    To produce debugging output for BASED management.
                    c=C    To produce debugging output for COMPACTIFY.
                and one should use *either* --cond=P or --cond=B but not both.
--identifer=S   (Default "REL32V0   ".)  Set the 10-character string returned 
                by MONITOR(23).  Will be automatically truncated or padded as
                needed.
--optproc=N     (Default is COMPOPT_.)  The "options processor" is used for 
                interpreting the run-time program's (particularly HAL/S-FC's) 
                options, which originally came from JCL, instead from 
                command-line options.  For HAL/S-FC, the available processors 
                are:
                    COMPOPT_     (automatically changed to COMPOPT_PFS 
                                 if --cond=P or to COMPOPT_BFS if --cond=B)
                    COMPOPT_PFS
                    COMPOPT_BFS
                    COMPOPT_360
                    LISTOPT
                    MONOPT
                See Virtual AGC page XPL.html#programOptions for instructions
                in using a custom options processor.
                Note: On the command line, this option should precede any of the
                options that are processed by the selected options processor.
--include=F     Folder to use for XPL/I's "/%INCLUDE ... %/" directives.
                Note that this is relative to the source-code file.
                Defaults to ../HALINCL.  If used, should precede any XPL source
                files on the command line.
--source=F      (Default is the folder containing the first XPL source-code file
                given on the command line.)  Name of the folder from which
                XPL source-code files (other than those for --include) are drawn
                by default. If used, should precede any XPL source files on the
                command line.
--output=F      (Default is the base-name of the first XPL source-code file
                given on the command line.) Name of the folder to store output 
                files.
--merge=F       (Default None.)  Write a file F containing all of the merged XPL
                source code.  Note that the resulting file is not necessarily a
                valid XPL file itself, because any file-inclusion directives the
                original separate source-code files contained are still present
                in it; thus if the merged file were compiled using normal XCOM-I
                options, double-inclusions would occur.  If the merged file will
                itself be compiled, the --no-inclusion switch (see below) should
                be used.  It may be advisable to give the merged file an 
                extension like ".merged" rather than the usual ".xpl" to avoid 
                confusion.
--no-inclusion  Disables any file-include directives found within the XPL source
                code.  This is typically used for "merged" files (see above).
--patch=P       Path to the inline-BAL patch files.  By default, this will
                be the same folder that contains the first XPL source-code
                file specified on the command line.
--adhoc=S,R     This is a way of creating global XPL macros without change
                to source-code files.  S is the name of the macro and R is
                the replacement text.  This switch can be used multiple 
                times.  In hindsight, it doesn't seem useful.
--target=L      (Default C) Set the target language for object-code.
                Only C is presently supported.
--indent=N      (Default 2) Set the indentation width for C-language source code.
                This is purely cosmetic effect to make it more pleasant to read
                the code output by XCOM-I.
--debug=D       Print extra debugging messages to device D.  D is either stdout 
                or stderr.
--verbose       The --verbose switch (which is the default) embeds extra comments
--concise       in the generated C source code, useful for debugging, or just for
                improved human readability.  Whereas the --concise switch instead
                eliminates those extra comments, producing smaller C file sizes.
--backtrace     Show Python backtrace for some XCOM-I errors.
--keep-unused   By default, XPL procedures which are never called are discarded
                without any generation of C code, and reduced analysis.  With
                --keep-unused, those procedures are retained and processed
                normally.
'''

for parm in sys.argv[1:]:
    if parm == "--":
        break
    elif parm.startswith("--optproc="):
        optproc = parm[10:]
    elif parm == "--keep-unused":
        keepUnused = True
    elif parm.startswith("--merge="):
        merge = parm[8:]
    elif parm.startswith("--lib-file="):
        libFile = parm[11:]
    elif parm == "--no-inclusion":
        noInclusionDirectives = True
    elif parm == "--no-overrides":
        noOverrides = True
    elif parm == "--old-hex": # ***DEBUG***
        newHex = False
    elif parm == "--help":
        print(helpMsg, file = sys.stderr)
        sys.exit(0)
    elif parm == "--xpl":
        standardXPL = True
        libFile = basePath + "XPL.LIBRARY.xpl"
    elif parm.startswith("--cond="):
        cond = parm[7:]
        if len(cond) != 1 or not cond.isupper():
            print("Illegal conditional %s" % parm, file=sys.stderr)
            sys.exit(1)
        ifdefs.add(cond)
    elif parm.startswith("--identifier="):
        identifierString = "%-10s" % parm[13:23]
    elif parm.startswith("--include="):
        includeFolder = parm[10:]
    elif parm.startswith("--source="):
        baseSource = parm[9:]
    elif parm.startswith("--patch="):
        baseSource = parm[8:]
    elif parm.startswith("--adhoc="):
        fields = parm[8:].split(",", 1)
        if len(fields) != 2:
            print("The --adhoc switch requires 2 sub-fields", file=sys.stderr)
            sys.exit(1)
        adhocs[fields[0]] = fields[1]
    elif parm.startswith("--debug="):
        d = parm[8:]
        if d == "stdout":
            debugSink = sys.stdout
        elif d == "stderr":
            debugSink = sys.stderr
        else:
            print("Value for --debug not recognized", file = sys.stderr)
            sys.exit(1)
    elif parm == "--verbose":
        verbose = True
    elif parm == "--concise":
        verbose = False
    elif parm.startswith("--target="):
        targetLanguage = parm[9:].upper()
        if targetLanguage not in ["C"]:
            print("Target language not supported", file = sys.stderr)
            sys.exit(1)
    elif parm.startswith("--output="):
        outputFolder = parm[9:]
    elif parm.startswith("--indent="):
        indent = " " * int(parm[9:])
    elif parm.startswith("--packing="):
        bitPacking = int(parm[10:])
    elif parm == "--backtrace":
        showBacktrace = True
    elif parm.startswith("-"):
        print("Unknown option %s" % parm, file = sys.stderr)
        sys.exit(1)
    else:
        if firstFile:
            if baseSource == None:
                baseSource = os.path.dirname(parm)
            if baseSource != "":
                dirHALINCL = baseSource + "/" + includeFolder
            else:
                dirHALINCL = includeFolder
            if libFile != None:
                readFileIntoLines(libFile)
        firstFile = False
        readFileIntoLines(parm)
        if outputFolder == None:
            head, tail = os.path.split(parm)
            name, ext = os.path.splitext(tail)
            outputFolder = name
if merge != None:
    f = open(merge, "w")
    f.writelines(lines)
    f.close()


# All of the source code is now in lines[].  Massage it a bit.
for i in range(len(lines)):
    # If trailing linefeeds or carriage returns (Windows, I'm looking at you!)
    # were read in, strip them off.
    lines[i] = lines[i].rstrip("\n\r")
    # *Apparently*, in Windows, if you make the mistake of editing a source
    # file containing one of our problematic UTF-8 characters ("¬", "¢"), 
    # Windows will "thoughtfully" stick an unwanted UTF-8 character encoded as 
    # "\xef\xbb\xbf" at the beginning of the file when you save it.  I suppose
    # this must be invisible to the user, while helping Windows magically 
    # identify files as UTF-8 without examining the entire file.  But for 
    # XCOM-I, it's pure, unadulterated corruption.
    lines[i] = lines[i].replace("\xef\xbb\xbf", "")
    # Also, if somebody modern edits a file and thoughlessly put in any tab
    # characters, we need to expands those tabs into spaces.
    lines[i] = lines[i].expandtabs(8)
    # Make sure each line is at least 80 columns wide.
    lines[i] = "%-80s" % lines[i]
    # Strip off punch-card sequence numbers at the ends of lines.
    lines[i] = lines[i][:80]
    
    
