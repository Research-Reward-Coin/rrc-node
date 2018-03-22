# Rewrite of Henrik Johansson's (Henrik.Johansson@Nexus.Comm.SE)
# pi.c example from his bignum package for Python 3
#
# Terms based on Gauss' refinement of Machin's formula:
#
# arctan(x) = x - (x^3)/3 + (x^5)/5 - (x^7)/7 + ...

from decimal import Decimal, getcontext

TERMS = [(12, 18), (8, 57), (-5, 239)]  # ala Gauss

def arctan(talj, kvot):

    """Compute arctangent using a series approximation"""

    summation = 0

    talj *= product

    qfactor = 1

    while talj:
        talj //= kvot
        summation += (talj // qfactor)
        qfactor += 2

    return summation

number_of_places = 1
# Reading the precision in from the decimals file.
with open("/precision/decimals", "r") as decimals_f:
    number_of_places = int(decimals_f.read())
getcontext().prec = number_of_places
product = 10 ** number_of_places

result = 0

for multiplier, denominator in TERMS:
    denominator = Decimal(denominator)
    result += arctan(- denominator * multiplier, - (denominator ** 2))

result *= 4  # pi == atan(1) * 4
string = str(result)

# 3.14159265358979E+15 => 3.14159265358979
# Dumping the value of pi in the pi file.
with open("/computed/pi", "w") as computed_f:
    computed_f.write(string[0:string.index("E")])
