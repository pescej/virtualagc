### FILE="Main.annotation"
## Copyright:   Public domain.
## Filename:    ALARM_AND_ABORT.agc
## Purpose:     A section of Colossus revision 236.
##              It is part of the reconstructed source code for the second
##              release (first manufactured) of the flighta software for
##              the Command Module's (CM) Apollo Guidance Computer (AGC)
##              for Apollo 8.  The code has been recreated from a copy of
##              Colossus 237. It has been adapted such that the resulting
##              bugger words exactly match those specified for Colossus 236
##              in NASA drawing 2021151B, which gives relatively high
##              confidence that the reconstruction is correct.
## Reference:   1457
## Assembler:   yaYUL
## Contact:     Ron Burkey <info@sandroid.org>.
## Website:     www.ibiblio.org/apollo/index.html
## Warning:     THIS PROGRAM IS STILL UNDERGOING RECONSTRUCTION
##              AND DOES NOT YET REFLECT THE ORIGINAL CONTENTS OF
##              COLOSSUS 236.
## Mod history: 2019-08-02 MAS  Created from Colossus236.

## Page 1457
# 	   THE FOLLOWING SUBROUTINE MAY BE CALLED TO DISPLAY A NON-ABORTIVE ALARM CONDITION. IT MAY BE CALLED
# EITHER IN INTERRUPT OR UNDER EXECUTIVE CONTROL.

# 	   CALLING SEQUENCE IS AS FOLLOWS:

#          TC     ALARM
#          OCT    AAANN           ALARM NO. NN IN GENERAL AREA AAA.
#                                 (RETURNS HERE)

		BLOCK	02
		SETLOC	FFTAG7
		BANK

		EBANK=	FAILREG

		COUNT	02/ALARM

# ALARM TURNS ON THE PROGRAM ALARM LIGHT, BUT DOES NOT DISPLAY.

ALARM		INHINT

		CA	Q
ALARM2		TS	ALMCADR
		INDEX	Q
		CA	0
BORTENT		TS	L

PRIOENT		CA	BBANK
 +1		EXTEND
		ROR	SUPERBNK	# ADD SUPER BITS.
		TS	ALMCADR +1

LARMENT		CA	Q		# STORE RETURN FOR ALARM
		TS	ITEMP1

CHKFAIL1	CCS	FAILREG		# IS ANYTHING IN FAILREG
		TCF	CHKFAIL2	# YES TRY NEXT REG
		LXCH	FAILREG
		TCF	PROGLARM	# TURN ALARM LIGHT ON FOR FIRST ALARM

CHKFAIL2	CCS	FAILREG +1
		TCF	FAIL3
		LXCH	FAILREG +1
		TCF	MULTEXIT

FAIL3		CA	FAILREG +2
		MASK	POSMAX
		CCS	A
		TCF	MULTFAIL
		LXCH	FAILREG +2
## Page 1458
		TCF	MULTEXIT

PROGLARM	CS	DSPTAB +11D
		MASK	OCT40400
		ADS	DSPTAB +11D

MULTEXIT	XCH	ITEMP1		# OBTAIN RETURN ADDRESS IN A
		RELINT
		INDEX	A
		TC	1

MULTFAIL	CA	L
		AD	BIT15
		TS	FAILREG +2

		TCF	MULTEXIT

# PRIOLARM DISPLAYS V05N09 VIA PRIODSPR WITH 3 RETURNS TO THE USER FROM THE ASTRONAUT AT CALL LOC +1,+2,+3 AND
# AN IMMEDIATE RETURN TO THE USER AT CALL LOC +4. EXAMPLE FOLLOWS,
#						   CAF    OCTXX           ALARM CODE
#						   TC     BANKCALL
#						   CADR   PRIOLARM

#						   ...    ...
#						   ...    ...
#						   ...    ...             ASTRONAUT RETURN
#						   TC     PHASCHNG        IMMEDIATE RETURN TO USER. RESTART
#						   OCT    X.1             PHASE CHANGE FOR PRIO DISPLAY

		BANK	10
		SETLOC	DISPLAYS
		BANK

		COUNT	10/DSPLA

PRIOLARM	INHINT			# * * * KEEP IN DISPLAY ROUTINES BANK
		TS	L		# SAVE ALARM CODE

		CA	BUF2		# 2 CADR OF PRIOLARM USER
		TS	ALMCADR
		CA	BUF2 +1
		TC	PRIOENT +1	# * LEAVE L ALONE
-2SEC		DEC	-200		# *** DONT MOVE
		CAF	V05N09
		TCF	PRIODSPR

		BLOCK	02
		SETLOC	FFTAG7
		BANK

## Page 1459
		COUNT	02/ALARM

BAILOUT		INHINT
		CA	Q
		TS	ALMCADR

		INDEX	Q
		CAF	0
		TC	BORTENT
OCT40400	OCT	40400

		INHINT
WHIMPER		CA	TWO
		AD	Z
		TS	BRUPT
		RESUME
		TC	POSTJUMP	# RESUME SENDS CONTROL HERE
		CADR	ENEMA
POODOO		INHINT
		CA	Q
ABORT2		TS	ALMCADR
		INDEX	Q
		CAF	0
		TC	BORTENT
OCT77770	OCT	77770		# DONT MOVE
		CS	BIT1
		MASK	FLAGWRD1
		TS	FLAGWRD1	# RESET AVEGFLAG
		CS	BIT6
		MASK	FLAGWRD7
		TS	FLAGWRD7	# RESET V37FLAG

		TC	BANKCALL
		CADR	MR.KLEAN
		TC	WHIMPER

CCSHOLE		INHINT
		CA	Q
		TC	ABORT2
OCT1103		OCT	1103
CURTAINS	INHINT
		CA	Q
		TC	ALARM2
OCT217		OCT	00217
		TC	ALMCADR		# RETURN TO USER

DOALARM		EQUALS	ENDOFJOB
# CALLING SEQUENCE FOR VARALARM

#						   CAF    (ALARM)
## Page 1460
#						   TC     VARALARM

# VARALARM TURNS ON PROGRAM ALARM LIGHT BUT DOES NOT DISPLAY
VARALARM	INHINT

		TS	L		# SAVE USERS ALARM CODE

		CA	Q		# SAVE USERS Q
		TS	ALMCADR

		TC	PRIOENT
OCT14		OCT	14		# DONT MOVE

		TC	ALMCADR		# RETURN TO USER

ABORT		EQUALS	BAILOUT		# *** TEMPORARY UNTIL ABORT CALLS OUT
