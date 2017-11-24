import glob
import os

from django.core import serializers

from subprocess import Popen, PIPE
from background_task import background


def miseq_directory_list(cmd):
    """
    Pass in a command line command to the genesippr Docker container
    """
    cmd = 'docker exec sippingportal_genesipprv2 {}'.format(cmd)
    p = Popen(cmd, shell=True, stdout=PIPE)
    output = p.communicate()[0].splitlines()  # wait until the script completes before resuming the code
    return output


def execute_command(cmd):
    p = Popen(cmd, shell=True)
    p.communicate()


@background(schedule=1)
def start_sipping(target_folder, json_model):
    print('\nSuccessfully called start_sipping method on {}'.format(target_folder))

    # Deserialize JSON model
    run_model = serializers.deserialize('json', json_model)

    # Make output folder
    cmd = 'docker exec sippingportal_genesipprv2 ' \
          'mkdir miseq_output/{}'.format(target_folder)
    execute_command(cmd)

    # Run genesippr
    cmd = 'docker exec sippingportal_genesipprv2 ' \
          'method.py miseq_output/{target_folder} ' \
          '-t /targets ' \
          '-m /miseq ' \
          '-f {target_folder} ' \
          '-b -C -r2 0'.format(target_folder=target_folder)
    execute_command(cmd)

    # Update model status
    for obj in run_model:
        obj.object.genesippr_status = 'Complete'
        obj.save()
        print('Updated genesippr_status to {}'.format(obj.object.genesippr_status))

    print('Genesippr job for {} complete'.format(target_folder))
