import glob
import os

from subprocess import Popen, PIPE
from background_task import background


def miseq_directory_list(cmd):
    """
    Pass in a command line command to the genesippr Docker container
    """
    cmd = 'docker exec ' \
          'sipping_portal_genesipprv2 ' \
          '{}'.format(cmd)

    p = Popen(cmd, shell=True, stdout=PIPE)
    output = p.communicate()[0].splitlines()  # wait until the script completes before resuming the code

    return output
