
import os, sys

def split(total, payments):
    subtotal = sum(payments)

    tax_and_tip = total - subtotal

    for i, val in enumerate(payments):
        percent_cut = val / subtotal 
        tax_and_tip_cut = tax_and_tip * percent_cut

        payment_cut = tax_and_tip_cut + val

        pritty_print = '${:,.2f}'.format(payment_cut)
        print("Payment %d: %s" % (i+1, pritty_print ))


def main():
    args = sys.argv[1:]

    args = [float(i) for i in args]


    if (len(args) > 1):
        split(args[0], args[1:])
    else:
        print("Usage: venmo-split <total> <cost1> <cost2> ...")



if __name__ == "__main__":
    main()