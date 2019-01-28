"""
Goldbach assumption

perfect number

prime factorisation

rsa key


"""





# -*- coding: utf-8 -*-


"""


Created on Thu Oct  5 16:44:23 2017






@author: Christian Bender






This python library contains some useful functions to deal with


prime numbers and whole numbers.






Overview:






isPrime(number)


sieveEr(N)


getPrimeNumbers(N)


primeFactorization(number)


greatestPrimeFactor(number)


smallestPrimeFactor(number)


getPrime(n)


getPrimesBetween(pNumber1, pNumber2)






----






isEven(number)


isOdd(number)


gcd(number1, number2)  // greatest common divisor


kgV(number1, number2)  // least common multiple


getDivisors(number)    // all divisors of 'number' inclusive 1, number


isPerfectNumber(number)






NEW-FUNCTIONS






simplifyFraction(numerator, denominator)


factorial (n) // n!


fib (n) // calculate the n-th fibonacci term.






-----






goldbach(number)  // Goldbach's assumption






"""


def isPrime(number):
    """


        input: positive integer 'number'


        returns true if 'number' is prime otherwise false.


    """

    import math  # for function sqrt

    # precondition

    assert isinstance(number, int) and (number >= 0), \
 \
        "'number' must been an int and positive"

    status = True

    # 0 and 1 are none primes.

    if number <= 1:
        status = False

    for divisor in range(2, int(round(math.sqrt(number))) + 1):

        # if 'number' divisible by 'divisor' then sets 'status'

        # of false and break up the loop.

        if number % divisor == 0:
            status = False

            break

    # precondition

    assert isinstance(status, bool), "'status' must been from type bool"

    return status


# ------------------------------------------


def sieveEr(N):
    """


        input: positive integer 'N' > 2


        returns a list of prime numbers from 2 up to N.





        This function implements the algorithm called


        sieve of erathostenes.





    """

    # precondition

    assert isinstance(N, int) and (N > 2), "'N' must been an int and > 2"

    # beginList: conatins all natural numbers from 2 upt to N

    beginList = [x for x in range(2, N + 1)]

    ans = []  # this list will be returns.

    # actual sieve of erathostenes

    for i in range(len(beginList)):

        for j in range(i + 1, len(beginList)):

            if (beginList[i] != 0) and \
 \
                    (beginList[j] % beginList[i] == 0):

            beginList[j] = 0


# filters actual prime numbers.


ans = [x for x in beginList if x != 0]

# precondition


assert isinstance(ans, list), "'ans' must been from type list"

return ans


# --------------------------------


def getPrimeNumbers(N):
    """


        input: positive integer 'N' > 2


        returns a list of prime numbers from 2 up to N (inclusive)


        This function is more efficient as function 'sieveEr(...)'


    """

    # precondition

    assert isinstance(N, int) and (N > 2), "'N' must been an int and > 2"

    ans = []

    # iterates over all numbers between 2 up to N+1

    # if a number is prime then appends to list 'ans'

    for number in range(2, N + 1):

        if isPrime(number):
            ans.append(number)

    # precondition

    assert isinstance(ans, list), "'ans' must been from type list"

    return ans


# -----------------------------------------


def primeFactorization(number):
    """


        input: positive integer 'number'


        returns a list of the prime number factors of 'number'


    """

    import math  # for function sqrt

    # precondition

    assert isinstance(number, int) and number >= 0, \
 \
        "'number' must been an int and >= 0"

    ans = []  # this list will be returns of the function.

    # potential prime number factors.

    factor = 2

    quotient = number

    if number == 0 or number == 1:

        ans.append(number)





    # if 'number' not prime then builds the prime factorization of 'number'

    elif not isPrime(number):

        while (quotient != 1):

            if isPrime(factor) and (quotient % factor == 0):

                ans.append(factor)

                quotient /= factor


            else:

                factor += 1





    else:

        ans.append(number)

    # precondition

    assert isinstance(ans, list), "'ans' must been from type list"

    return ans


# -----------------------------------------


def greatestPrimeFactor(number):
    """


        input: positive integer 'number' >= 0


        returns the greatest prime number factor of 'number'


    """

    # precondition

    assert isinstance(number, int) and (number >= 0), \
 \
        "'number' bust been an int and >= 0"

    ans = 0

    # prime factorization of 'number'

    primeFactors = primeFactorization(number)

    ans = max(primeFactors)

    # precondition

    assert isinstance(ans, int), "'ans' must been from type int"

    return ans


# ----------------------------------------------


def smallestPrimeFactor(number):
    """


        input: integer 'number' >= 0


        returns the smallest prime number factor of 'number'


    """

    # precondition

    assert isinstance(number, int) and (number >= 0), \
 \
        "'number' bust been an int and >= 0"

    ans = 0

    # prime factorization of 'number'

    primeFactors = primeFactorization(number)

    ans = min(primeFactors)

    # precondition

    assert isinstance(ans, int), "'ans' must been from type int"

    return ans


# ----------------------


def isEven(number):
    """


        input: integer 'number'


        returns true if 'number' is even, otherwise false.


    """

    # precondition

    assert isinstance(number, int), "'number' must been an int"

    assert isinstance(number % 2 == 0, bool), "compare bust been from type bool"

    return number % 2 == 0


# ------------------------


def isOdd(number):
    """


        input: integer 'number'


        returns true if 'number' is odd, otherwise false.


    """

    # precondition

    assert isinstance(number, int), "'number' must been an int"

    assert isinstance(number % 2 != 0, bool), "compare bust been from type bool"

    return number % 2 != 0


# ------------------------


def goldbach(number):
    """


        Goldbach's assumption


        input: a even positive integer 'number' > 2


        returns a list of two prime numbers whose sum is equal to 'number'


    """

    # precondition

    assert isinstance(number, int) and (number > 2) and isEven(number), \
 \
        "'number' must been an int, even and > 2"

    ans = []  # this list will returned

    # creates a list of prime numbers between 2 up to 'number'

    primeNumbers = getPrimeNumbers(number)

    lenPN = len(primeNumbers)

    # run variable for while-loops.

    i = 0

    j = 1

    # exit variable. for break up the loops

    loop = True

    while (i < lenPN and loop):

        j = i + 1;

        while (j < lenPN and loop):

            if primeNumbers[i] + primeNumbers[j] == number:
                loop = False

                ans.append(primeNumbers[i])

                ans.append(primeNumbers[j])

            j += 1;

        i += 1

    # precondition

    assert isinstance(ans, list) and (len(ans) == 2) and \
 \
           (ans[0] + ans[1] == number) and isPrime(ans[0]) and isPrime(ans[1]), \
 \
        "'ans' must contains two primes. And sum of elements must been eq 'number'"

    return ans


# ----------------------------------------------


def gcd(number1, number2):
    """


        Greatest common divisor


        input: two positive integer 'number1' and 'number2'


        returns the greatest common divisor of 'number1' and 'number2'


    """

    # precondition

    assert isinstance(number1, int) and isinstance(number2, int) \
 \
           and (number1 >= 0) and (number2 >= 0), \
 \
        "'number1' and 'number2' must been positive integer."

    rest = 0

    while number2 != 0:
        rest = number1 % number2

        number1 = number2

        number2 = rest

    # precondition

    assert isinstance(number1, int) and (number1 >= 0), \
 \
        "'number' must been from type int and positive"

    return number1


# ----------------------------------------------------


def kgV(number1, number2):
    """


        Least common multiple


        input: two positive integer 'number1' and 'number2'


        returns the least common multiple of 'number1' and 'number2'


    """

    # precondition

    assert isinstance(number1, int) and isinstance(number2, int) \
 \
           and (number1 >= 1) and (number2 >= 1), \
 \
        "'number1' and 'number2' must been positive integer."

    ans = 1  # actual answer that will be return.

    # for kgV (x,1)

    if number1 > 1 and number2 > 1:

        # builds the prime factorization of 'number1' and 'number2'

        primeFac1 = primeFactorization(number1)

        primeFac2 = primeFactorization(number2)





    elif number1 == 1 or number2 == 1:

        primeFac1 = []

        primeFac2 = []

        ans = max(number1, number2)

    count1 = 0

    count2 = 0

    done = []  # captured numbers int both 'primeFac1' and 'primeFac2'

    # iterates through primeFac1

    for n in primeFac1:

        if n not in done:

            if n in primeFac2:

                count1 = primeFac1.count(n)

                count2 = primeFac2.count(n)

                for i in range(max(count1, count2)):
                    ans *= n





            else:

                count1 = primeFac1.count(n)

                for i in range(count1):
                    ans *= n

            done.append(n)

    # iterates through primeFac2

    for n in primeFac2:

        if n not in done:

            count2 = primeFac2.count(n)

            for i in range(count2):
                ans *= n

            done.append(n)

    # precondition

    assert isinstance(ans, int) and (ans >= 0), \
 \
        "'ans' must been from type int and positive"

    return ans


# ----------------------------------


def getPrime(n):
    """


        Gets the n-th prime number.


        input: positive integer 'n' >= 0


        returns the n-th prime number, beginning at index 0


    """

    # precondition

    assert isinstance(n, int) and (n >= 0), "'number' must been a positive int"

    index = 0

    ans = 2  # this variable holds the answer

    while index < n:

        index += 1

        ans += 1  # counts to the next number

        # if ans not prime then

        # runs to the next prime number.

        while not isPrime(ans):
            ans += 1

    # precondition

    assert isinstance(ans, int) and isPrime(ans), \
 \
        "'ans' must been a prime number and from type int"

    return ans


# ---------------------------------------------------


def getPrimesBetween(pNumber1, pNumber2):
    """


        input: prime numbers 'pNumber1' and 'pNumber2'


                pNumber1 < pNumber2


        returns a list of all prime numbers between 'pNumber1' (exclusiv)


                and 'pNumber2' (exclusiv)


    """

    # precondition

    assert isPrime(pNumber1) and isPrime(pNumber2) and (pNumber1 < pNumber2), \
 \
        "The arguments must been prime numbers and 'pNumber1' < 'pNumber2'"

    number = pNumber1 + 1  # jump to the next number

    ans = []  # this list will be returns.

    # if number is not prime then

    # fetch the next prime number.

    while not isPrime(number):
        number += 1

    while number < pNumber2:

        ans.append(number)

        number += 1

        # fetch the next prime number.

        while not isPrime(number):
            number += 1

    # precondition

    assert isinstance(ans, list) and ans[0] != pNumber1 \
 \
           and ans[len(ans) - 1] != pNumber2, \
 \
        "'ans' must been a list without the arguments"

    # 'ans' contains not 'pNumber1' and 'pNumber2' !

    return ans


# ----------------------------------------------------


def getDivisors(n):
    """


        input: positive integer 'n' >= 1


        returns all divisors of n (inclusive 1 and 'n')


    """

    # precondition

    assert isinstance(n, int) and (n >= 1), "'n' must been int and >= 1"

    from math import sqrt

    ans = []  # will be returned.

    for divisor in range(1, n + 1):

        if n % divisor == 0:
            ans.append(divisor)

    # precondition

    assert ans[0] == 1 and ans[len(ans) - 1] == n, \
 \
        "Error in function getDivisiors(...)"

    return ans


# ----------------------------------------------------


def isPerfectNumber(number):
    """


        input: positive integer 'number' > 1


        returns true if 'number' is a perfect number otherwise false.


    """

    # precondition

    assert isinstance(number, int) and (number > 1), \
 \
        "'number' must been an int and >= 1"

    divisors = getDivisors(number)

    # precondition

    assert isinstance(divisors, list) and (divisors[0] == 1) and \
 \
           (divisors[len(divisors) - 1] == number), \
 \
        "Error in help-function getDivisiors(...)"

    # summed all divisors up to 'number' (exclusive), hence [:-1]

    return sum(divisors[:-1]) == number


# ------------------------------------------------------------


def simplifyFraction(numerator, denominator):
    """


        input: two integer 'numerator' and 'denominator'


        assumes: 'denominator' != 0


        returns: a tuple with simplify numerator and denominator.


    """

    # precondition

    assert isinstance(numerator, int) and isinstance(denominator, int) \
 \
           and (denominator != 0), \
 \
        "The arguments must been from type int and 'denominator' != 0"

    # build the greatest common divisor of numerator and denominator.

    gcdOfFraction = gcd(abs(numerator), abs(denominator))

    # precondition

    assert isinstance(gcdOfFraction, int) and (numerator % gcdOfFraction == 0) \
 \
           and (denominator % gcdOfFraction == 0), \
 \
        "Error in function gcd(...,...)"

    return (numerator // gcdOfFraction, denominator // gcdOfFraction)


# -----------------------------------------------------------------


def factorial(n):
    """


        input: positive integer 'n'


        returns the factorial of 'n' (n!)


    """

    # precondition

    assert isinstance(n, int) and (n >= 0), "'n' must been a int and >= 0"

    ans = 1  # this will be return.

    for factor in range(1, n + 1):
        ans *= factor

    return ans


# -------------------------------------------------------------------


def fib(n):
    """


        input: positive integer 'n'


        returns the n-th fibonacci term , indexing by 0


    """

    # precondition

    assert isinstance(n, int) and (n >= 0), "'n' must been an int and >= 0"

    tmp = 0

    fib1 = 1

    ans = 1  # this will be return

    for i in range(n - 1):
        tmp = ans

        ans += fib1

        fib1 = tmp

    return ans


# -*- coding: utf-8 -*-


"""


Created on Thu Oct  5 16:44:23 2017






@author: Christian Bender






This python library contains some useful functions to deal with


prime numbers and whole numbers.






Overview:






isPrime(number)


sieveEr(N)


getPrimeNumbers(N)


primeFactorization(number)


greatestPrimeFactor(number)


smallestPrimeFactor(number)


getPrime(n)


getPrimesBetween(pNumber1, pNumber2)






----






isEven(number)


isOdd(number)


gcd(number1, number2)  // greatest common divisor


kgV(number1, number2)  // least common multiple


getDivisors(number)    // all divisors of 'number' inclusive 1, number


isPerfectNumber(number)






NEW-FUNCTIONS






simplifyFraction(numerator, denominator)


factorial (n) // n!


fib (n) // calculate the n-th fibonacci term.






-----






goldbach(number)  // Goldbach's assumption






"""


def isPrime(number):
    """


        input: positive integer 'number'


        returns true if 'number' is prime otherwise false.


    """

    import math  # for function sqrt

    # precondition

    assert isinstance(number, int) and (number >= 0), \
 \
        "'number' must been an int and positive"

    status = True

    # 0 and 1 are none primes.

    if number <= 1:
        status = False

    for divisor in range(2, int(round(math.sqrt(number))) + 1):

        # if 'number' divisible by 'divisor' then sets 'status'

        # of false and break up the loop.

        if number % divisor == 0:
            status = False

            break

    # precondition

    assert isinstance(status, bool), "'status' must been from type bool"

    return status


# ------------------------------------------


def sieveEr(N):
    """


        input: positive integer 'N' > 2


        returns a list of prime numbers from 2 up to N.





        This function implements the algorithm called


        sieve of erathostenes.





    """

    # precondition

    assert isinstance(N, int) and (N > 2), "'N' must been an int and > 2"

    # beginList: conatins all natural numbers from 2 upt to N

    beginList = [x for x in range(2, N + 1)]

    ans = []  # this list will be returns.

    # actual sieve of erathostenes

    for i in range(len(beginList)):

        for j in range(i + 1, len(beginList)):

            if (beginList[i] != 0) and \
 \
                    (beginList[j] % beginList[i] == 0):

            beginList[j] = 0


# filters actual prime numbers.


ans = [x for x in beginList if x != 0]

# precondition


assert isinstance(ans, list), "'ans' must been from type list"

return ans


# --------------------------------


def getPrimeNumbers(N):
    """


        input: positive integer 'N' > 2


        returns a list of prime numbers from 2 up to N (inclusive)


        This function is more efficient as function 'sieveEr(...)'


    """

    # precondition

    assert isinstance(N, int) and (N > 2), "'N' must been an int and > 2"

    ans = []

    # iterates over all numbers between 2 up to N+1

    # if a number is prime then appends to list 'ans'

    for number in range(2, N + 1):

        if isPrime(number):
            ans.append(number)

    # precondition

    assert isinstance(ans, list), "'ans' must been from type list"

    return ans


# -----------------------------------------


def primeFactorization(number):
    """


        input: positive integer 'number'


        returns a list of the prime number factors of 'number'


    """

    import math  # for function sqrt

    # precondition

    assert isinstance(number, int) and number >= 0, \
 \
        "'number' must been an int and >= 0"

    ans = []  # this list will be returns of the function.

    # potential prime number factors.

    factor = 2

    quotient = number

    if number == 0 or number == 1:

        ans.append(number)





    # if 'number' not prime then builds the prime factorization of 'number'

    elif not isPrime(number):

        while (quotient != 1):

            if isPrime(factor) and (quotient % factor == 0):

                ans.append(factor)

                quotient /= factor


            else:

                factor += 1





    else:

        ans.append(number)

    # precondition

    assert isinstance(ans, list), "'ans' must been from type list"

    return ans


# -----------------------------------------


def greatestPrimeFactor(number):
    """


        input: positive integer 'number' >= 0


        returns the greatest prime number factor of 'number'


    """

    # precondition

    assert isinstance(number, int) and (number >= 0), \
 \
        "'number' bust been an int and >= 0"

    ans = 0

    # prime factorization of 'number'

    primeFactors = primeFactorization(number)

    ans = max(primeFactors)

    # precondition

    assert isinstance(ans, int), "'ans' must been from type int"

    return ans


# ----------------------------------------------


def smallestPrimeFactor(number):
    """


        input: integer 'number' >= 0


        returns the smallest prime number factor of 'number'


    """

    # precondition

    assert isinstance(number, int) and (number >= 0), \
 \
        "'number' bust been an int and >= 0"

    ans = 0

    # prime factorization of 'number'

    primeFactors = primeFactorization(number)

    ans = min(primeFactors)

    # precondition

    assert isinstance(ans, int), "'ans' must been from type int"

    return ans


# ----------------------


def isEven(number):
    """


        input: integer 'number'


        returns true if 'number' is even, otherwise false.


    """

    # precondition

    assert isinstance(number, int), "'number' must been an int"

    assert isinstance(number % 2 == 0, bool), "compare bust been from type bool"

    return number % 2 == 0


# ------------------------


def isOdd(number):
    """


        input: integer 'number'


        returns true if 'number' is odd, otherwise false.


    """

    # precondition

    assert isinstance(number, int), "'number' must been an int"

    assert isinstance(number % 2 != 0, bool), "compare bust been from type bool"

    return number % 2 != 0


# ------------------------


def goldbach(number):
    """


        Goldbach's assumption


        input: a even positive integer 'number' > 2


        returns a list of two prime numbers whose sum is equal to 'number'


    """

    # precondition

    assert isinstance(number, int) and (number > 2) and isEven(number), \
 \
        "'number' must been an int, even and > 2"

    ans = []  # this list will returned

    # creates a list of prime numbers between 2 up to 'number'

    primeNumbers = getPrimeNumbers(number)

    lenPN = len(primeNumbers)

    # run variable for while-loops.

    i = 0

    j = 1

    # exit variable. for break up the loops

    loop = True

    while (i < lenPN and loop):

        j = i + 1;

        while (j < lenPN and loop):

            if primeNumbers[i] + primeNumbers[j] == number:
                loop = False

                ans.append(primeNumbers[i])

                ans.append(primeNumbers[j])

            j += 1;

        i += 1

    # precondition

    assert isinstance(ans, list) and (len(ans) == 2) and \
 \
           (ans[0] + ans[1] == number) and isPrime(ans[0]) and isPrime(ans[1]), \
 \
        "'ans' must contains two primes. And sum of elements must been eq 'number'"

    return ans


# ----------------------------------------------


def gcd(number1, number2):
    """


        Greatest common divisor


        input: two positive integer 'number1' and 'number2'


        returns the greatest common divisor of 'number1' and 'number2'


    """

    # precondition

    assert isinstance(number1, int) and isinstance(number2, int) \
 \
           and (number1 >= 0) and (number2 >= 0), \
 \
        "'number1' and 'number2' must been positive integer."

    rest = 0

    while number2 != 0:
        rest = number1 % number2

        number1 = number2

        number2 = rest

    # precondition

    assert isinstance(number1, int) and (number1 >= 0), \
 \
        "'number' must been from type int and positive"

    return number1


# ----------------------------------------------------


def kgV(number1, number2):
    """


        Least common multiple


        input: two positive integer 'number1' and 'number2'


        returns the least common multiple of 'number1' and 'number2'


    """

    # precondition

    assert isinstance(number1, int) and isinstance(number2, int) \
 \
           and (number1 >= 1) and (number2 >= 1), \
 \
        "'number1' and 'number2' must been positive integer."

    ans = 1  # actual answer that will be return.

    # for kgV (x,1)

    if number1 > 1 and number2 > 1:

        # builds the prime factorization of 'number1' and 'number2'

        primeFac1 = primeFactorization(number1)

        primeFac2 = primeFactorization(number2)





    elif number1 == 1 or number2 == 1:

        primeFac1 = []

        primeFac2 = []

        ans = max(number1, number2)

    count1 = 0

    count2 = 0

    done = []  # captured numbers int both 'primeFac1' and 'primeFac2'

    # iterates through primeFac1

    for n in primeFac1:

        if n not in done:

            if n in primeFac2:

                count1 = primeFac1.count(n)

                count2 = primeFac2.count(n)

                for i in range(max(count1, count2)):
                    ans *= n





            else:

                count1 = primeFac1.count(n)

                for i in range(count1):
                    ans *= n

            done.append(n)

    # iterates through primeFac2

    for n in primeFac2:

        if n not in done:

            count2 = primeFac2.count(n)

            for i in range(count2):
                ans *= n

            done.append(n)

    # precondition

    assert isinstance(ans, int) and (ans >= 0), \
 \
        "'ans' must been from type int and positive"

    return ans


# ----------------------------------


def getPrime(n):
    """


        Gets the n-th prime number.


        input: positive integer 'n' >= 0


        returns the n-th prime number, beginning at index 0


    """

    # precondition

    assert isinstance(n, int) and (n >= 0), "'number' must been a positive int"

    index = 0

    ans = 2  # this variable holds the answer

    while index < n:

        index += 1

        ans += 1  # counts to the next number

        # if ans not prime then

        # runs to the next prime number.

        while not isPrime(ans):
            ans += 1

    # precondition

    assert isinstance(ans, int) and isPrime(ans), \
 \
        "'ans' must been a prime number and from type int"

    return ans


# ---------------------------------------------------


def getPrimesBetween(pNumber1, pNumber2):
    """


        input: prime numbers 'pNumber1' and 'pNumber2'


                pNumber1 < pNumber2


        returns a list of all prime numbers between 'pNumber1' (exclusiv)


                and 'pNumber2' (exclusiv)


    """

    # precondition

    assert isPrime(pNumber1) and isPrime(pNumber2) and (pNumber1 < pNumber2), \
 \
        "The arguments must been prime numbers and 'pNumber1' < 'pNumber2'"

    number = pNumber1 + 1  # jump to the next number

    ans = []  # this list will be returns.

    # if number is not prime then

    # fetch the next prime number.

    while not isPrime(number):
        number += 1

    while number < pNumber2:

        ans.append(number)

        number += 1

        # fetch the next prime number.

        while not isPrime(number):
            number += 1

    # precondition

    assert isinstance(ans, list) and ans[0] != pNumber1 \
 \
           and ans[len(ans) - 1] != pNumber2, \
 \
        "'ans' must been a list without the arguments"

    # 'ans' contains not 'pNumber1' and 'pNumber2' !

    return ans


# ----------------------------------------------------


def getDivisors(n):
    """


        input: positive integer 'n' >= 1


        returns all divisors of n (inclusive 1 and 'n')


    """

    # precondition

    assert isinstance(n, int) and (n >= 1), "'n' must been int and >= 1"

    from math import sqrt

    ans = []  # will be returned.

    for divisor in range(1, n + 1):

        if n % divisor == 0:
            ans.append(divisor)

    # precondition

    assert ans[0] == 1 and ans[len(ans) - 1] == n, \
 \
        "Error in function getDivisiors(...)"

    return ans


# ----------------------------------------------------


def isPerfectNumber(number):
    """


        input: positive integer 'number' > 1


        returns true if 'number' is a perfect number otherwise false.


    """

    # precondition

    assert isinstance(number, int) and (number > 1), \
 \
        "'number' must been an int and >= 1"

    divisors = getDivisors(number)

    # precondition

    assert isinstance(divisors, list) and (divisors[0] == 1) and \
 \
           (divisors[len(divisors) - 1] == number), \
 \
        "Error in help-function getDivisiors(...)"

    # summed all divisors up to 'number' (exclusive), hence [:-1]

    return sum(divisors[:-1]) == number


# ------------------------------------------------------------


def simplifyFraction(numerator, denominator):
    """


        input: two integer 'numerator' and 'denominator'


        assumes: 'denominator' != 0


        returns: a tuple with simplify numerator and denominator.


    """

    # precondition

    assert isinstance(numerator, int) and isinstance(denominator, int) \
 \
           and (denominator != 0), \
 \
        "The arguments must been from type int and 'denominator' != 0"

    # build the greatest common divisor of numerator and denominator.

    gcdOfFraction = gcd(abs(numerator), abs(denominator))

    # precondition

    assert isinstance(gcdOfFraction, int) and (numerator % gcdOfFraction == 0) \
 \
           and (denominator % gcdOfFraction == 0), \
 \
        "Error in function gcd(...,...)"

    return (numerator // gcdOfFraction, denominator // gcdOfFraction)


# -----------------------------------------------------------------


def factorial(n):
    """


        input: positive integer 'n'


        returns the factorial of 'n' (n!)


    """

    # precondition

    assert isinstance(n, int) and (n >= 0), "'n' must been a int and >= 0"

    ans = 1  # this will be return.

    for factor in range(1, n + 1):
        ans *= factor

    return ans


# -------------------------------------------------------------------


def fib(n):
    """


        input: positive integer 'n'


        returns the n-th fibonacci term , indexing by 0


    """

    # precondition

    assert isinstance(n, int) and (n >= 0), "'n' must been an int and >= 0"

    tmp = 0

    fib1 = 1

    ans = 1  # this will be return

    for i in range(n - 1):
        tmp = ans

        ans += fib1

        fib1 = tmp

    return ans


https: // github.com / TheAlgorithms / Python / blob / 7
bb26e9b2a032cb61a06308700853f57e106f151 / other / primelib.py

from __future__ import print_function

# Primality Testing with the Rabin-Miller Algorithm


import random


def rabinMiller(num):
    s = num - 1

    t = 0

    while s % 2 == 0:
        s = s // 2

        t += 1

    for trials in range(5):

        a = random.randrange(2, num - 1)

        v = pow(a, s, num)

        if v != 1:

            i = 0

            while v != (num - 1):

                if i == t - 1:

                    return False


                else:

                    i = i + 1

                    v = (v ** 2) % num

    return True


def isPrime(num):
    if (num < 2):
        return False

    lowPrimes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59,

                 61, 67, 71, 73, 79, 83, 89, 97, 101, 103, 107, 109, 113, 127,

                 131, 137, 139, 149, 151, 157, 163, 167, 173, 179, 181, 191,

                 193, 197, 199, 211, 223, 227, 229, 233, 239, 241, 251, 257,

                 263, 269, 271, 277, 281, 283, 293, 307, 311, 313, 317, 331,

                 337, 347, 349, 353, 359, 367, 373, 379, 383, 389, 397, 401,

                 409, 419, 421, 431, 433, 439, 443, 449, 457, 461, 463, 467,

                 479, 487, 491, 499, 503, 509, 521, 523, 541, 547, 557, 563,

                 569, 571, 577, 587, 593, 599, 601, 607, 613, 617, 619, 631,

                 641, 643, 647, 653, 659, 661, 673, 677, 683, 691, 701, 709,

                 719, 727, 733, 739, 743, 751, 757, 761, 769, 773, 787, 797,

                 809, 811, 821, 823, 827, 829, 839, 853, 857, 859, 863, 877,

                 881, 883, 887, 907, 911, 919, 929, 937, 941, 947, 953, 967,

                 971, 977, 983, 991, 997]

    if num in lowPrimes:
        return True

    for prime in lowPrimes:

        if (num % prime) == 0:
            return False

    return rabinMiller(num)


def generateLargePrime(keysize=1024):
    while True:

        num = random.randrange(2 ** (keysize - 1), 2 ** (keysize))

        if isPrime(num):
            return num


if __name__ == '__main__':
    num = generateLargePrime()

    print(('Prime number:', num))

    print(('isPrime:', isPrime(num)))

https: // github.com / TheAlgorithms / Python / blob / 0
9
cc7696609ad64585feea17567ad3c6ffcf86e1 / ciphers / rabin_miller.py

from __future__ import print_function

import random, sys, os

import rabin_miller as rabinMiller, cryptomath_module as cryptoMath


def main():
    print('Making key files...')

    makeKeyFiles('rsa', 1024)

    print('Key files generation successful.')


def generateKey(keySize):
    print('Generating prime p...')

    p = rabinMiller.generateLargePrime(keySize)

    print('Generating prime q...')

    q = rabinMiller.generateLargePrime(keySize)

    n = p * q

    print('Generating e that is relatively prime to (p - 1) * (q - 1)...')

    while True:

        e = random.randrange(2 ** (keySize - 1), 2 ** (keySize))

        if cryptoMath.gcd(e, (p - 1) * (q - 1)) == 1:
            break

    print('Calculating d that is mod inverse of e...')

    d = cryptoMath.findModInverse(e, (p - 1) * (q - 1))

    publicKey = (n, e)

    privateKey = (n, d)

    return (publicKey, privateKey)


def makeKeyFiles(name, keySize):
    if os.path.exists('%s_pubkey.txt' % (name)) or os.path.exists('%s_privkey.txt' % (name)):
        print('\nWARNING:')

        print(
            '"%s_pubkey.txt" or "%s_privkey.txt" already exists. \nUse a different name or delete these files and re-run this program.' % (
                name, name))

        sys.exit()

    publicKey, privateKey = generateKey(keySize)

    print('\nWriting public key to file %s_pubkey.txt...' % name)

    with open('%s_pubkey.txt' % name, 'w') as fo:
        fo.write('%s,%s,%s' % (keySize, publicKey[0], publicKey[1]))

    print('Writing private key to file %s_privkey.txt...' % name)

    with open('%s_privkey.txt' % name, 'w') as fo:
        fo.write('%s,%s,%s' % (keySize, privateKey[0], privateKey[1]))


if __name__ == '__main__':
    main()
https: // github.com / TheAlgorithms / Python / blob / 0
9
cc7696609ad64585feea17567ad3c6ffcf86e1 / ciphers / rsa_key_generator.py

# Part of Cosmos by OpenGenus Foundation


Integer = int(input("Enter an Number :  "))

absInteger = abs(Integer)

num = 1

prime_num = []

if absInteger > 0:

    while num <= absInteger:

        x = 0

        if absInteger % num == 0:

            y = 1

            while y <= num:

                if num % y == 0:
                    x = x + 1

                y = y + 1

            if x == 2:
                prime_num.append(num)

        num = num + 1

    print("Your Input: " + str(Integer))

    print("Prime Factors : " + str(prime_num))


elif absInteger == 0:

    print("Your Input: 0")

    print("Prime Factors : [0]")


else:

    print("Please Input a number")

https: // github.com / OpenGenus / cosmos / blob / b983138c5c1ba03aed84df6b78cb25fc64380b82 / code / mathematical_algorithms / src / prime_factors / prime_factors.py


# computes the sieve for the euler totient function


def ETF_sieve(N=1000000):
    sieve = [i for i in range(N)]

    for i in range(2, N, 1):

        if sieve[i] == i:  # this i would be a prime

            for j in range(i, N, i):
                sieve[j] *= (1 - 1 / i)

    return sieve


https: // github.com / OpenGenus / cosmos / blob / b983138c5c1ba03aed84df6b78cb25fc64380b82 / code / mathematical_algorithms / src / euler_totient / euler_totient_sieve.py

import random


def check(a, s, d, n):
    x = pow(a, d, n)

    if x == 1:
        return True

    for i in xrange(s - 1):

        if x == n - 1:
            return True

        x = pow(x, 2, n)

    return x == n - 1


def isPrime(n, k=10):
    if n == 2:
        return True

    if not n & 1:
        return False

    s = 0

    d = n - 1

    while d % 2 == 0:
        d >>= 1

        s += 1

    for i in xrange(k):

        a = random.randint(2, n - 1)

        if not check(a, s, d, n):
            return False

    return True


https: // github.com / OpenGenus / cosmos / blob / b983138c5c1ba03aed84df6b78cb25fc64380b82 / code / mathematical_algorithms / src / primality_tests / miller_rabin_primality_test / miller_rabin_primality_test.py

import sys
import argparse


# computes (a^b)%m


# fermats little theorem is used assuming m is prime


def power(a, b, m):
    if b == 0:
        return 1

    p = power(a, b // 2, m)

    p = p % m

    p = (p * p) % m

    if b & 1:
        p = (p * a) % m

    return p


def stringToInt(a, m):
    a_mod_m = 0

    for i in range(len(a)):
        a_mod_m = (a_mod_m * 10 % m + int(a[i]) % m) % m

    return a_mod_m


def findPowerModuloP(args):
    cases = args.cases

    p = args.prime or 1000000007

    for case in cases:
        a_str, b_str = case.split(',')

        a = stringToInt(a_str, p)

        b = stringToInt(b_str, p - 1)  # using Fermats little theorem, (a^(p-1))%p = 1

        pow_ab_mod_m = power(a, b, p)

        print("%s^%s modulo %d = %d" % (a_str, b_str, p, pow_ab_mod_m))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('cases', type=str, nargs='+',

                        help='comma seperated values of a and b in a^b')

    parser.add_argument('--prime', type=int,

                        help='prime number aginst which to take the modulo (default: 1000000007)')

    args = parser.parse_args()

    findPowerModuloP(args)



# Rabin Karp Algorithm in python using hash values


# d is the number of characters in input alphabet


d = 2560


def search(pat, txt, q):
    M = len(pat)

    N = len(txt)

    i = 0

    j = 0

    p = 0

    t = 0

    h = 1

    for i in xrange(M - 1):
        h = (h * d) % q

    for i in xrange(M):
        p = (d * p + ord(pat[i])) % q

        t = (d * t + ord(txt[i])) % q

    for i in xrange(N - M + 1):

        if p == t:

            for j in xrange(M):

                if txt[i + j] != pat[j]:
                    break

            j += 1

            if j == M:
                print
                "Pattern found at index " + str(i)

        if i < N - M:

            t = (d * (t - ord(txt[i]) * h) + ord(txt[i + M])) % q

            if t < 0:
                t = t + q


# Driver program to test the above function


txt = "ALL WORLDS IS A STAGE AND ALL OF US ARE A PART OF THE PLAY"

pat = "ALL"

q = 101  # A prime number

search(pat, txt, q)



# Pollard-Rho-Brent Integer factorisation


# Complexity: O(n^(1/4) * log2(n))


# Output is list of primes factors & exponents.


# Example, N = 180 gives : [[2, 2], [3, 2], [5, 1]]


import sys

import random

# For Python 2 & 3 compatibility


if (sys.version_info > (3, 0)):

    from queue import Queue

    RANGE = range

    INPUT = input


else:

    from Queue import Queue

    RANGE = xrange

    INPUT = raw_input


def gcd(a, b):
    while b:
        a, b = b, a % b

    return a


def expo(a, b):
    x, y = 1, a

    while (b > 0):

        if (b & 1):
            x = x * y

        y = y * y

        b >>= 1

    return x


primes = [0] * 100000


def sieve():
    primes[1] = 1

    primes[2] = 2

    j = 4

    while (j < 100000):
        primes[j] = 2

        j += 2

    j = 3

    while (j < 100000):

        if (primes[j] == 0):

            primes[j] = j

            i = j * j

            k = j << 1

            while (i < 100000):
                primes[i] = j

                i += k

        j += 2


# Checks if p is prime or not.


def rabin_miller(p):
    if (p < 100000):
        # Precomputation make checking for small numbers O(1).

        return primes[p] == p

    if (p % 2 == 0):
        return False

    s = p - 1

    while (s % 2 == 0):
        s >>= 1

    for i in RANGE(5):

        a = random.randrange(p - 1) + 1

        temp = s

        mod = pow(a, temp, p)

        while (temp != p - 1 and mod != 1 and mod != p - 1):
            mod = (mod * mod) % p

            temp = temp * 2

        if (mod != p - 1 and temp % 2 == 0):
            return False

    return True


# Returns a prime factor of N.


def brent(N):
    if (N % 2 == 0):
        return 2

    if (N < 100000):
        return primes[N]

    y, c, m = random.randint(1, N - 1), random.randint(1, N - 1), random.randint(1, N - 1)

    g, r, q = 1, 1, 1

    while g == 1:

        x = y

        for i in range(r):
            y = ((y * y) % N + c) % N

        k = 0

        while (k < r and g == 1):

            ys = y

            for i in range(min(m, r - k)):
                y = ((y * y) % N + c) % N

                q = q * (abs(x - y)) % N

            g = gcd(q, N)

            k = k + m

        r = r * 2

    if g == N:

        while True:

            ys = ((ys * ys) % N + c) % N

            g = gcd(abs(x - ys), N)

            if g > 1:
                break

    return g


def factorise(n):
    if (n == 1):
        return []

    Q_1 = Queue()

    Q_2 = []

    Q_1.put(n)

    while (not Q_1.empty()):

        l = Q_1.get()

        if (rabin_miller(l)):
            Q_2.append(l)

            continue

        d = brent(l)

        if (d == l):

            Q_1.put(l)


        else:

            Q_1.put(d)

            Q_1.put(l // d)

    return Q_2


if __name__ == "__main__":

    sieve()

    t = int(INPUT())  # Denotes number of testcases.

    for _ in range(t):

        n = int(INPUT())

        L = factorise(n)

        L.sort()

        i = 0

        factors = []

        while (i < len(L)):
            cnt = L.count(L[i])

            factors.append([L[i], cnt])

            i += cnt

        print(factors)
https: // github.com / OpenGenus / cosmos / blob / b983138c5c1ba03aed84df6b78cb25fc64380b82 / code / mathematical_algorithms / src / prime_numbers_of_n / prime_numbers_of_n.py

# Part of Cosmos by OpenGenus Foundation


from math import sqrt, ceil


def atkin_sieve(n):
    # Include 2,3,5 in initial results

    if (n >= 5):

        result = [2, 3, 5]


    elif (n >= 3 and n < 5):

        result = [2, 3]


    elif (n == 2):

        result = [2]


    else:

        result = []

    # Initialize sieve; all integers marked as non-prime

    sieve = [0] * n

    root = ceil(sqrt(n))

    # Flip entry in sieve based on n mod 60=r:

    # Per solution to n = 4*x^2 + y^2 if r in [1,13,17,29,37,41,49,53]

    # Per solution to n = 3*x^2 + y^2 if r in [7,19,31,43]

    # Per solution to n = 3*x^2 - y^2 when y<x if r in [11,23,47,59]

    xy = [(x, y) for x in range(1, root + 1)

          for y in range(1, root + 1)]

    for (x, y) in xy:

        i = 4 * x * x + y * y

        if ((i <= n) and (i % 60 in [1, 13, 17, 29, 37, 41, 49, 53])):
            sieve[i - 1] ^= 1

        i = 3 * x * x + y * y

        if ((i <= n) and (i % 60 in [7, 19, 31, 43])):
            sieve[i - 1] ^= 1

        if (x > y):

            i = 3 * x * x - y * y

            if ((i <= n) and (i % 60 in [11, 23, 47, 59])):
                sieve[i - 1] ^= 1

    # Remove multiples of the squares of remaining integers

    for i in range(2, root):

        j = i * i

        while (j < n):
            sieve[j - 1] = 0

            j += i * i

    # Add sieved results to the result list

    result += [i for (i, n) in list(zip(range(1, n + 1), sieve))

               if n == 1]

    return result


https: // github.com / OpenGenus / cosmos / blob / b983138c5c1ba03aed84df6b78cb25fc64380b82 / code / mathematical_algorithms / src / sieve_of_atkin / sieve_of_atkin.py

import sys, pyperclip, cryptomath, random

SYMBOLS = """ !"#$%&'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\] ^_`abcdefghijklmnopqrstuvwxyz{|}~"""  # note the space at the front


def main():
    myMessage = """"A computer would deserve to be called intelligent if it could deceive a human into believing that it was human." -Alan Turing"""

    myKey = 2023

    myMode = 'encrypt'  # set to 'encrypt' or 'decrypt'

    if myMode == 'encrypt':

        translated = encryptMessage(myKey, myMessage)


    elif myMode == 'decrypt':

        translated = decryptMessage(myKey, myMessage)

    print('Key: %s' % (myKey))

    print('%sed text:' % (myMode.title()))

    print(translated)

    pyperclip.copy(translated)

    print('Full %sed text copied to clipboard.' % (myMode))


def getKeyParts(key):
    keyA = key // len(SYMBOLS)

    keyB = key % len(SYMBOLS)

    return (keyA, keyB)


def checkKeys(keyA, keyB, mode):
    if keyA == 1 and mode == 'encrypt':
        sys.exit('The affine cipher becomes incredibly weak when key A is set to 1. Choose a different key.')

    if keyB == 0 and mode == 'encrypt':
        sys.exit('The affine cipher becomes incredibly weak when key B is set to 0. Choose a different key.')

    if keyA < 0 or keyB < 0 or keyB > len(SYMBOLS) - 1:
        sys.exit('Key A must be greater than 0 and Key B must be between 0 and %s.' % (len(SYMBOLS) - 1))

    if cryptomath.gcd(keyA, len(SYMBOLS)) != 1:
        sys.exit('Key A (%s) and the symbol set size (%s) are not relatively prime. Choose a different key.' % (
            keyA, len(SYMBOLS)))


def encryptMessage(key, message):
    keyA, keyB = getKeyParts(key)

    checkKeys(keyA, keyB, 'encrypt')

    ciphertext = ''

    for symbol in message:

        if symbol in SYMBOLS:

            # encrypt this symbol

            symIndex = SYMBOLS.find(symbol)

            ciphertext += SYMBOLS[(symIndex * keyA + keyB) % len(SYMBOLS)]


        else:

            ciphertext += symbol  # just append this symbol unencrypted

    return ciphertext


def decryptMessage(key, message):
    keyA, keyB = getKeyParts(key)

    checkKeys(keyA, keyB, 'decrypt')

    plaintext = ''

    modInverseOfKeyA = cryptomath.findModInverse(keyA, len(SYMBOLS))

    for symbol in message:

        if symbol in SYMBOLS:

            # decrypt this symbol

            symIndex = SYMBOLS.find(symbol)

            plaintext += SYMBOLS[(symIndex - keyB) * modInverseOfKeyA % len(SYMBOLS)]


        else:

            plaintext += symbol  # just append this symbol undecrypted

    return plaintext


def getRandomKey():
    while True:

        keyA = random.randint(2, len(SYMBOLS))

        keyB = random.randint(2, len(SYMBOLS))

        if cryptomath.gcd(keyA, len(SYMBOLS)) == 1:
            return keyA * len(SYMBOLS) + keyB
