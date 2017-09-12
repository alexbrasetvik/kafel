#!/usr/bin/env python
# You may need to run me with LD_PRELOAD="$(pwd)/libkafel.so"
import os, flask, sys, yaml, json, time
from cffi import FFI

# Load Kafel
ffi = FFI()
ffi.cdef("int kafel_set_policy(const char* source, int sync_all_threads);")
ffi.verify()
kafel = ffi.dlopen("./libkafel.so")

if os.environ.get("DANGEROUSLY_DISABLE_SECCOMP", False):
    print "This dangerous service is now even less secure"
else:
    # Set a seccomp policy that will get us killed if we attempt to spawn a subprocess.
    policy = "POLICY a { KILL { execve, clone, fork } } USE a DEFAULT ALLOW"
    sync_all_threads = 1
    rc = kafel.kafel_set_policy(policy, sync_all_threads)
    if (rc):
        print 'Could not set policy :('
        sys.exit(1)

# This is what yaml.load _should_ have been named! We're deliberately not using the yaml.safe_load here.
yaml.dangerouslyRunArbitraryCodeAndMaybeLoadSomeData = yaml.load

app = flask.Flask(__name__)
start = time.time()


@app.route('/', methods=['GET', 'POST'])
def root():
    if time.time() - start > 300:
        # In case we're forgotten and left running.
        return "Sorry, we're closed."
    if not flask.request.data:
        return 'Feed me some yummy YAML, and I shall convert it to JSON for you. Surely I can trust you?'
    return json.dumps(yaml.dangerouslyRunArbitraryCodeAndMaybeLoadSomeData(flask.request.data))


# This service is intentionally insecure, don't expose it too wide :)
app.run(host='127.0.0.1', port=1234)

# If you start this service with DANGEROUSLY_DISABLE_SECCOMP=1, then the following request will
# be running arbitrary code: 
# curl -v localhost:1234 -H 'content-type: application/json' -d 'your_files: !!python/object/apply:subprocess.check_output ["ls"]'
# If run with the seccomp-policy on, the process will crash instead if sent that request.
#
# Note that the seccomp policy in no way makes this a safe service, as e.g. this still works:
# curl -v localhost:1234 -H 'content-type: application/json' -d 'arbitrary_file: !!python/object/apply:eval [open("/etc/passwd").read()]'
