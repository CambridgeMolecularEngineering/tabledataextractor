from sympy import symbols
from sympy import factor

expression = 'a*c*d + a*c*e + a*c*f + b*c*d + b*c*e + b*c*f'

print(expression)
print("")
print (factor(expression))

expression = '2006*c*d + 2006*c*e + 2006*c*f + 2007*c*d + 2007*c*e + 2007*c*f'

print(expression)
print("")
print (factor(expression))

*symbs, = symbols('2006, c, d, 2006, c, e, 2006, c, f, 2007, c, d, 2007, c, e, 2007, c, f')
expression = '2006*c*d + 2006*c*e + 2006*c*f + 2007*c*d + 2007*c*e + 2007*c*f'
print("")
print(symbs[1])

print(symbs[0]*symbs[1]*symbs[2] + symbs[3]*symbs[4]*symbs[5] + symbs[6]*symbs[7]*symbs[8] + symbs[9]*symbs[10]*symbs[11] + symbs[12]*symbs[13]*symbs[14] + symbs[15]*symbs[16]*symbs[17])

print(factor(symbs[0]*symbs[1]*symbs[2] + symbs[3]*symbs[4]*symbs[5] + symbs[6]*symbs[7]*symbs[8] + symbs[9]*symbs[10]*symbs[11] + symbs[12]*symbs[13]*symbs[14] + symbs[15]*symbs[16]*symbs[17]))
#print(factor('2006'*'c'*'d' + '2006'*'c'*'e' + '2006'*'c'*'f' + '2007'*'c'*'d' + '2007'*'c'*'e' + '2007'*'c'*'f'))