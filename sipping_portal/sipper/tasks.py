import glob
import os

from django.core import serializers

from subprocess import Popen, PIPE
from time import sleep
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


@background(schedule=10)
def active_log_reader(json_model, json_metadata_model):
    print('\nCALLED active_log_reader BACKGROUND TASK')

    # Deserialize models
    run_metadata_model = serializers.deserialize('json', json_metadata_model)
    run_model = serializers.deserialize('json', json_model)
    read_log_metadata = True

    for obj in run_model:
            for meta_obj in run_metadata_model:
                while obj.object.genesippr_status == 'Processing':
                    raw_lines = read_logfile(meta_obj.object.log_filepath)

                    # Read if the log can be found
                    if raw_lines is not None:

                        # Parse the actual output lines
                        recent_output = remove_extraneous_log_metadata(raw_lines)

                        # Read the log once for file locations
                        if read_log_metadata:
                            miseq_path, miseq_folder, fastq_destination, samplesheet = pull_log_metadata(raw_lines)
                            meta_obj.object.miseq_path = miseq_path
                            meta_obj.object.miseq_folder = miseq_folder
                            meta_obj.object.fastq_destination = fastq_destination
                            meta_obj.object.samplesheet = samplesheet
                            meta_obj.save(force_update=True)

                            # Skip this next time around
                            read_log_metadata = False

                        # Rather unfortunate looking model update
                        try:
                            meta_obj.object.recent_output_1_time, \
                            meta_obj.object.recent_output_1 = time_content_log_split(recent_output[0])
                        except IndexError:
                            pass
                        try:
                            meta_obj.object.recent_output_2_time, \
                            meta_obj.object.recent_output_2 = time_content_log_split(recent_output[1])
                        except IndexError:
                            pass
                        try:
                            meta_obj.object.recent_output_3_time, \
                            meta_obj.object.recent_output_3 = time_content_log_split(recent_output[2])
                        except IndexError:
                            pass
                        try:
                            meta_obj.object.recent_output_4_time, \
                            meta_obj.object.recent_output_4 = time_content_log_split(recent_output[3])
                        except IndexError:
                            pass
                        try:
                            meta_obj.object.recent_output_5_time, \
                            meta_obj.object.recent_output_5 = time_content_log_split(recent_output[4])
                        except IndexError:
                            pass

                        # Save
                        meta_obj.save(force_update=True)
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


def read_logfile(log_filepath):
    try:
        log_file = open(log_filepath, 'r')
        log_lines = log_file.readlines()
        log_file.close()
        return log_lines
    except FileNotFoundError:
        print('\nCANNOT FIND FILE {}'.format(log_filepath))


def pull_log_metadata(line_list):
    miseq_path = str()
    miseq_folder = str()
    fastq_destination = str()
    samplesheet = str()

    for item in line_list[:10]:
        if item.startswith('MiSeqPath:'):
            miseq_path = item.replace(',', '').replace('MiSeqPath: ', '')
        elif item.startswith('MiSeqFolder'):
            miseq_folder = item.replace(',', '').replace('MiSeqFolder: ', '')
        elif item.startswith('Fastq destination'):
            fastq_destination = item.replace(',', '').replace('Fastq destination: ', '')
        elif item.startswith('SampleSheet'):
            samplesheet = item.replace(',', '').replace('SampleSheet: ', '')
    return miseq_path, miseq_folder, fastq_destination, samplesheet


def remove_extraneous_log_metadata(line_list):
    cleaned_list = []

    for item in line_list:
        if item.startswith('MiSeqPath:'):
            miseq_path = item.replace(',', '').replace('MiSeqPath: ', '')
        elif item.startswith('MiSeqFolder'):
            miseq_folder = item.replace(',', '').replace('MiSeqFolder: ', '')
        elif item.startswith('Fastq destination'):
            fastq_destination = item.replace(',', '').replace('Fastq destination: ', '')
        elif item.startswith('SampleSheet'):
            samplesheet = item.replace(',', '').replace('SampleSheet: ', '')
        else:
            cleaned_list.append(item)
        # Take last 5 items
        cleaned_list = cleaned_list[-5:]
    return cleaned_list


def time_content_log_split(log_line):
    tmp = log_line.replace('[', '')
    tmp = tmp.split('] ')

    time = tmp[0]
    content = tmp[1]

    return time, content
