

# Print Progress
def printpr(counter, modulo=10000):
	if counter % modulo == 0:
		print(".",end='',flush=True)
	if counter % (modulo*100) == 0:
		print(f' {counter:,} lines parsed',flush=True)



