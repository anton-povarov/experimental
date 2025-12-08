# Task 6: Identify problems in this code
#
# Give them:
#
# def load_users(path=[]):
#     with open(path) as f:
#         return f.read().split("\n")
#
# cache = {}
#
# def get_user(id):
#     if id not in cache:
#         cache[id] = load_users("users.txt")[id]
#     return cache[id]
#
# Ask:
# Identify at least 7 issues and propose fixes.
#
# Includes:
# 	•	mutable default arg bug
# 	•	no bounds checking
# 	•	global mutable cache race conditions
# 	•	wasted reads (open/parse for every lookup)
# 	•	poor separation of concerns
# 	•	no error handling
# 	•	etc.
#
# What this tests
# 	•	Real-world debugging
# 	•	Code hygiene
# 	•	Ability to reason about side effects and performance

# 1. path=[] the default arg will be evaluated only once, when function is defined
#    the issue: default arg - is not an issue imo, as path is never modified, so diff callers would not interfere
#    the issue: if the call is made with no params -> uses default value -> we're opening what then? open will raise probably
#    resolution: explicitly type it as str or the complicated FileDescriptorOrPath object that open() actually accepts
# 2. multiple files read into memory, potentially consuming it all
#    even if just one file - it can be too large, read by lines should solve
#    resolution: read file by lines at the very least, this brings just a sliding buffer over a file to memory
# 3. no typing hints, hurts readability and is actually the source of a couple of bugs in this code (like list/dict)
#    resolution: typehint everything (won't catch all bugs, but will help pinpoint the under-designed pieces)
# 4. cache[id] = load_users("users.txt")[id] - the user id might not exist in the file, will raise
#    resolution: at least bounds check against the result list size
# 5. minor: using a global variable `cache` - should explicitly mention global cache
#    resolution: keep it as is for now, fix other problems and then take a look at the final design
#    resolution: maybe rename into `_cache` to signify it's private
# 6. for any user not in cache - will re-read and re-parse the file (and likely, the user will still not be there!)
#    resolution: read the file once
#      - i.e. if cache is None, or
#      - let caller pass a flag to re-read, or
#      - re-read if enough time has passed since last file read
# 7. load_users() returns a list, not a dict, so it's a bit misleading that you then get a user by offset essentially
#    resolution: return a dict, even if id is still an implicit "line offset in the file", avoids the bounds check issue as well
# 8. #7 leads to another issue - if new user information is added to the file _at the top_ or in the middle
#    then all users on the following lines are essentially invalidated and no longer match the cache
#    resolution: store user_id in the file explicitly, validate and parse file contents properly
# 9. no information is parsed for user, it's just a string, unclear what are you actually getting from the cache (name? email? etc.)
#    resolution: define something like a class UserData, make it a pydantic model, validate


#
# added by ChatGPT
#

# 🟥 Category 1 — Dangerous Default Argument
# ✔ You partially caught this, but here is the full critical insight:
# path=[] is a mutable default argument, shared across calls.
# Even if the function doesn’t mutate it now, this is still a bug because:
#
# ❗ Bug 1.1: The default type is wrong
# The default value should be a string — but it’s a list.
# Passing it to open(list) → TypeError at runtime.
#
# ❗ Bug 1.2: Future mutation risk
#
# Even if today you don’t mutate it, this is considered a bug because:
# 	•	later code might append to it and silently break behavior
# 	•	reviewers and linters treat it as a red flag
#
# This is part of why interviewers include this trap.

# 🟥 Category 2 — Incorrect Return Type
# ✔ You mentioned the mismatch but here are the specifics:
#
# load_users() returns a list of raw strings.
# But get_user() treats the file content as indexed by user ID:
# This assumes:
# 	•	each line is a separate user entry
# 	•	user ID == line index
# 	•	IDs are 0-based
# 	•	file contains no blank lines
# 	•	file order never changes
# 	•	file never has deleted users
#
# 👆 All of these assumptions are unsafe.

# 🟥 Category 3 — File Read Happens on Every Cache Miss
# ✔ You mentioned this.
# Additional insight:
# Even worse:
# If ID is not present in file → on every call:
# 	•	re-read full file
# 	•	still fail
# 	•	no negative caching (cache “user not found”)
#
# ❗ Bug 3.1: No negative caching
# This causes O(N) repeated reads for non-existent IDs.

# 🟥 Category 4 — No Error Handling for File I/O
# ❗ Missing problems:
# 	•	file may not exist
# 	•	file may be unreadable
# 	•	file may be huge
# 	•	file may contain invalid UTF-8
# 	•	partial read, OS errors, I/O exceptions
# You’re not catching any, so:
#    FileNotFoundError
#    UnicodeDecodeError
#    PermissionError
# will bubble up in unpredictable ways.
#
#
# 🟥 Category 5 — Using id as a variable
# !  You didn’t mention this — **** this is a big Python interview red flag ****.
#   id() is a built-in function.
#   Overwriting it silently breaks debugging and tooling.

# 🟥 Category 6 — Global Mutable Cache
# ✔ You partially covered this, but more issues:
# ! ❗ Bug 6.1: Not thread-safe
# If this ever runs:
# 	•	in a multithreaded webserver
# 	•	or async environment using threads
# You have race conditions on:
# 	•	.get()
# 	•	mutations
# 	•	inconsistent cache state
#
# ❗ Bug 6.2: Cache never invalidates
# Once value is there — it’s eternal.
# Even if users.txt changes, the program won’t reload it.
#
# ❗ Bug 6.3: Cache leaks memory
# If someone calls get_user(10**10) you store a useless entry.


# 🟥 Category 7 — Poor Separation of Concerns
#
# ! ************* This one usually gets missed. *******************
#
# get_user() decides where data comes from (users.txt).
# ! This makes function impossible to test.
#
# Better design:
# 	•	load_users(path)
# 	•	get_user(id, user_map)
#
# Now the caller controls data source.

# 🟥 Category 8 — Inefficient Reading Method
# You caught the big part, but a subtle improvement:
# ❗ Bug 8.1: Splitting on “\n” creates empty string on trailing newline
# Typical files end with a newline → extra empty entry → shifts indices.

# 🟥 Category 9 — Missing Type Conversions
#
# You mentioned type hints, but there’s another issue:
# What if the file stores:
# 123,John
# 124,Alice
# Then indexing by id (e.g., 124) doesn’t work and should not.
# Without a proper parser, this code can never be safe.


def load_users(path=[]):
    with open(path) as f:
        return f.read().split("\n")


cache = {}


def get_user(id):
    if id not in cache:
        cache[id] = load_users("users.txt")[id]
    return cache[id]


if __name__ == "__main__":
    load_users()
    load_users()
