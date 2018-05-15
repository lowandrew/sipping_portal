Sipping Portal
==============

The Sipping Portal is a Django web application intended to run locally
on a computer with a direct connection to an Illumina MiSeq. 
The portal will actively monitor a designated MiSeq output folder 
and allow for any completed or in-progress run to be analyzed with 
[GenesipprV2](https://github.com/OLC-Bioinformatics/geneSipprV2).
 

### Requirements
WIP

### Installation
These commands get you up and running:

`docker-compose -f local.yml build`

`docker-compose -f local.yml up`

You may also need to run/make some migrations:

`docker-compose -f local.yml run --rm django python manage.py makemigrations`
`docker-compose -f local.yml run --rm django python manage.py migrate`

For some reason sometimes the sipping app may not have its migrations picked up - to get those added manually:

`docker-compose -f local.yml run --rm django python manage.py makemigrations sipper`

To get background tasks running so genesippr will actually run:

`docker-compose -f local.yml run --rm django python manage.py process_tasks`

Finally, make sure the media folder in sipping_portal is accessible to all users, or genesippr won't be able
to write files like it needs to:

`sudo chmod -R 0777 sipping_portal/media`

### Usage
WIP
