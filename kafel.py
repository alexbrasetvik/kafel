#!/usr/bin/env
import os, threading, time
from cffi import FFI

# Load Kafel
ffi = FFI()
ffi.cdef("int kafel_set_policy(const char* source, int sync_all_threads);")
ffi.verify()
kafel = ffi.dlopen("./libkafel.so")

deny_policy = """POLICY a { ERRNO(1) { listen, execve, clone, fork } }
USE a DEFAULT ALLOW
"""
kill_policy = deny_policy.replace("ERRNO(1)", "KILL")

print 'Some exec before I set a policy: ', os.popen('uname -a').read()

# seccomp-policies can be set on a specific thread
def _run():
   print "In-thread pre-policy exec:", os.popen('uname -a').read()
   kafel.kafel_set_policy(deny_policy, 0)
   # This thread should now be unable to exec:
   try:
     os.popen('uname -a').read()
     print "Expected OSError! :("
   except OSError:
     print "exec prevented in thread"

# Spawn a thread, exec in that thread ...
t = threading.Thread(target=_run)
t.start()
t.join()

# ... then see if we can still exec in the main thread
print "Done with thread, can I still exec?"
print 'Main-thread exec: ', os.popen('uname -a').read()

# Spawn a thread that runs a short while, to see that it runs
# when the main thread is killed
def _print_dots():
    for i in range(5):
        time.sleep(.2)
        print '.'
    print "Baii! Nice knowing you"
    # We've quite deliberately messed up the process at this point, so
    # kill it or ^Z-ing it will be necessary.
    os.kill(os.getpid(), 9)
# Need to make the thread before we set the policy below, as the
# policy will prevent us from making a thread.
threading.Thread(target=_print_dots).start()

# Set a policy that applies to all threads
sync_all_threads = 1
rc = kafel.kafel_set_policy(deny_policy, sync_all_threads)
if(rc):
   print 'Could not set policy :('

print 'I should *not* be able to exec now: '
try:
  if os.system("ls"):
    print 'Trapped'
  print os.popen('cat /etc/passwd').read()
except OSError as e:
  print 'Yup, that failed: ', e

rc = kafel.kafel_set_policy(kill_policy, sync_all_threads)
if(rc):
   print 'Could not set policy :('
else:
   print "You should _not_ see /etc/passwd contents on the next line:"
   os.popen('cat /etc/passwd').read()

print "I should never get here!"
