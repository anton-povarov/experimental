# decided to build this in Go, see the go subdir
# the idea is to search for substring in text, finding all occurrences
# interesting questions to the interviewer
#  1. should we expect strings shorter than 3 chars?
#  2. if the string is shorter - do we assume it's at the start or still want to find in the middle?
#     if any psition - then we'd need to generate all possible trigrams on the sides
#     if start only - we can prefix the string with some number of underscores
