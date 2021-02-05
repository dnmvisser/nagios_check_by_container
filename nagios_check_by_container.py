#!/usr/bin/env python3
# Wrapper script to run a service check from a Docker container
import argparse
import sys
import re
import docker
from pprint import pprint

def nagios_exit(message, code):
    print(message)
    sys.exit(code)

try:
    parser = argparse.ArgumentParser(description='Check service using Docker container run')
    parser.add_argument('--image',
            help='The image to run',
            required=True
            )
    parser.add_argument('--command',
            help='The command to run in the container',
            required=False
            )
    parser.add_argument('--env_file',
            help='The path to a file with "KEY=VALUE" lines to use as environment variables',
            required=False
            )
    # FIXME this needs more work
    parser.add_argument('--warning',
            help='Raise a WARNING if the result is more than this number',
            required=False,
            default=0
            )

    args = parser.parse_args()

    image = args.image
    command = args.command
    env_file = args.env_file
    warn_at = args.warning


    client = docker.from_env()

    my_envs = docker.utils.parse_env_file(env_file)

    d = client.containers.run(
            image = image,
            command = command,
            environment = my_envs,
            auto_remove = True,
            )

    # start with clean slate
    ok_msg = [d.decode('utf-8')]
    warn_msg = []
    crit_msg = []


#    if 'Strict-Transport-Security' in req.headers:
#        hsts = req.headers['Strict-Transport-Security']
#        m = re.match("max-age=\"?\\b(\\d+)\\b\"?", hsts, re.IGNORECASE)
#        if m:
#            found_age = int(m.group(1))
#            if found_age < maxage:
#                warn_msg.append(
#                    "max-age directive found, but not long-lived ({0}, while {1} is required).".
#                    format(found_age, maxage))
#            else:
#                ok_msg.append("Long-lived max-age directive found ({0}).".format(found_age))
except Exception as e:
    nagios_exit("UNKNOWN: Unknown error: {0}.".format(e), 3)

# Exit with accumulated message(s)
if crit_msg:
    nagios_exit("CRITICAL: " + ' '.join(crit_msg + warn_msg), 2)
elif warn_msg:
    nagios_exit("WARNING: " + ' '.join(warn_msg), 1)
else:
    nagios_exit("OK: " + ' '.join(ok_msg), 0)
