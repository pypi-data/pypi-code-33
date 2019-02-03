from epicprint.Print import Print

print = Print()

print.info("Welcome").group()
print.success("Now we can").group()
print.success("Indent stuff").success("Use colors").success("Chain")
print.ungroup().warning("This is my first package")
print.reset().fail("Ending with a fail message. Bye.")