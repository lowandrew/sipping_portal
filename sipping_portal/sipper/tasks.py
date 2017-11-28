import glob
import os

from django.core import serializers

from subprocess import Popen, PIPE
from time import sleep
from background_task import background

from .models import SipperRun

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


@background(schedule=10)
def active_log_reader(json_model, json_metadata_model):
    print('\nCALLED active_log_reader BACKGROUND TASK')

    # Deserialize models
    run_metadata_model = serializers.deserialize('json', json_metadata_model)
    run_model = serializers.deserialize('json', json_model)

    for obj in run_model:
            for meta_obj in run_metadata_model:
                while obj.object.genesippr_status == 'Processing':

                    #print('\nAttempting to pull recent log data from {}'.format(meta_obj.object.log_filepath))
                    recent_output = read_log_recent_line(meta_obj.object.log_filepath)

                    if recent_output is not None:
                        meta_obj.object.recent_output = recent_output
                        meta_obj.save(force_update=True)
                        print('\nSUCCESSFULLY UPDATED RECENT OUTPUT')

                        #print('Updated recent output to {}'.format(meta_obj.object.recent_output))
                    else:
                        print('\nCANNOT DETECT OUTPUT. WAITING.')

                    sleep(30) # Update model every 30 seconds


@background(schedule=1)
def run_genesippr(target_folder, json_model):
    print('\nCALLED run_genesippr BACKGROUND TASK')

    # Deserialize
    run_model = serializers.deserialize('json', json_model)

    # Make output folder
    print('\nCreating output folder for genesippr...')
    mkdir_cmd = 'docker exec sippingportal_genesipprv2 ' \
                'mkdir miseq_output/{}'.format(target_folder)
    execute_command(mkdir_cmd)

    print('\nRunning genesippr...')
    # Run genesippr
    genesippr_cmd = 'docker exec sippingportal_genesipprv2 ' \
                    'method.py miseq_output/{target_folder} ' \
                    '-t /targets ' \
                    '-m /miseq ' \
                    '-f {target_folder} ' \
                    '-b -C -r2 0'.format(target_folder=target_folder)
    execute_command(genesippr_cmd)

    # Update model status
    for obj in run_model:
        obj.object.genesippr_status = 'Complete'
        obj.save(force_update=True)
        print('Updated genesippr_status to {}'.format(obj.object.genesippr_status))

    print('Genesippr job for {} complete'.format(target_folder))


def start_sipping(target_folder, json_model, json_metadata_model):
    print('\nSuccessfully called start_sipping method on {}'.format(target_folder))

    # Call sippr background task
    run_genesippr(target_folder, json_model)

    # Start log reader
    active_log_reader(json_model, json_metadata_model)


def read_log_recent_line(log_filepath):
    current_time = str()

    try:
        log_file = open(log_filepath, 'r')
        log_lines = log_file.readlines()
        log_file.close()
        current_line = log_lines[len(log_lines)-1]
        return current_line
    except FileNotFoundError:
        print('\nCANNOT FIND FILE {}'.format(log_filepath))


def read_log_metadata(log_filepath):
    miseq_path = str()
    miseq_folder = str()
    fastq_destination = str()
    samplesheet = str()
