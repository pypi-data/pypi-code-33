from Print import Print

print = Print()

print.info("Welcome").group()
print.success("Now we can:", ["Indent stuff", "Use colors", "Attach semantic to the print statements"])
print.warning("Nothing more to say")
print.reset().fail("Ending with a fail message. Bye.")