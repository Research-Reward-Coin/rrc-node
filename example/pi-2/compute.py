import decimal

from mpmath import inf, mp, nsum

def pi_mpmath(n):
    """Calculate PI to the Nth digit.
    I figured using mpmath would work well, but this is not very
    efficient. With n = 1000, it took over a minute on my laptop.
    """
    mp.dps = n
    return str(nsum(lambda k: (4/(8*k+1) - 2/(8*k+4) - 1/(8*k+5) - 1/(8*k+6)) / 16**k, (0, inf)))

def pi_decimal(n):
    """Calculate PI to the Nth digit.
    This one uses the native python Decimal type that allows arbitrary
    precision. With n = 1000, it took less than a second on my laptop.
    """
    D = decimal.Decimal
    decimal.getcontext().prec = n+10
    pi = D(0)
    k = 0
    tail_prev = ''
    while True:
        pi += (D(4)/D(8*k+1) - D(2)/D(8*k+4) - D(1)/D(8*k+5) - D(1)/D(8*k+6)) / D(16)**D(k)
        tail = str(pi)[n+1:-1]
        if tail == tail_prev:
            break
        tail_prev = tail
        k += 1
    decimal.getcontext().prec = n
    return str(pi * D(1))

number_of_places = 1
# Reading the precision in from the decimals file.
with open("/precision/decimals", "r") as decimals_f:
    number_of_places = int(decimals_f.read())

# Dumping the value of pi in the pi file.
with open("/computed/pi", "w") as computed_f:
    computed_f.write(pi_decimal(number_of_places))
