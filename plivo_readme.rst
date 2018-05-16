===============
Installation ::
===============

commands:
--------
  git clone https://github.com/Coder-AMiT/Kiwi-tcms
  
  mv Kiwi-tcms Kiwi  
  
  virtualenv --python=python3.6 ~/virtualenvs/kiwi
  
  . ~/virtualenvs/kiwi/bin/activate
  
  cd Kiwi
  
  sudo pip install -r requirements/mysql.txt
  
  sudo pip install -r requirements/devel.txt
  
  sudo pip install -r requirements/postgres.txt
  

  npm install
  
  ./manage.py migrate
  
  ./manage.py createsuperuser
  
  ./manage.py runserver
  

Now, open http://127.0.0.1:8000/ and should be presented with your brand new Kiwi TCMS homepage!

To run server at different ip:port
  ./manage.py runserver <ip>:<port>


Kiwi Configuration:
-------------
To be able to contact the Kiwi TCMS server
a minimal configuration file ~/.tcms.conf has to be
provided in the user home directory:

  [tcms]
  
  url = https://tcms.server/xml-rpc/
  
  username = your-username
  
  password = your-password
  


Db Configuration:
----------------

By default, kiwi works on mysqlite.
But it can be used on other Db also.
To change Db settings, goto tcms/settings/common.py and change the DATABASES dict Engine value.
and in tcms/settings/devel.py DATABASES dict , change all the configuration according to the Db.

These configuration must be done as soon after downloading the repo clone.


Image configuration:
-------------------
To change status image, change the following image ==> tcms/static/images/ico_status.png
To change the kiwi tcms logo , change ==>   tcms/static/images/kiwi_h20.png
                                            tcms/static/images/kiwi_h80.png


Test case Details configuration:
-------------------------------
By default, it will be attribute named as "Notes" on test case page. To change it "Details"
edit the file ==> tcms/templates/case/get.html
and change the value of this block
<div class="title grey">Notes&nbsp;:</div> ==> <div class="title grey">Details&nbsp;:</div>


Running it on AWS:
------------------
Once you have created the server on aws using above commands n configurations. You can now run it from local
system using SSH.
Use a static ip for this.
  ssh -i /Users/plivo/Documents/plivo-tcms.pem ubuntu@<EC2_Public_DNS> sudo python3  /home/ubuntu/Kiwi/manage.py runserver 0.0.0.0:80

Make sure the port 80 is open.

Once it starts running, open it from local system using global ip ( make it static ).


Configure Site for AWS:
----------------------
To use server from AWS to local, first thing is to configure the site.

  Open <ip>:<port>/admin

  Go to 'Sites'

  Edit the default site value to AWS's static ip.


Reading spreadsheet:
--------------------
To read spreadsheet, google API is being used. To use the API, first time it needs to give authentication
from gmail account and it save a json file locally for next time authentications.
Follow the link for details : https://developers.google.com/sheets/api/quickstart/python



Take backup at Google Drive:
----------------------------
Please follow the link to get details on how to configure for backup from machine to google drive:
http://olivermarshall.net/how-to-upload-a-file-to-google-drive-from-the-command-line/
After the configuration of gdrive, first thing it to take the dump.
Passing password every-time is not handy, so create .pgpass file for auto authentication.
Follow the link :
https://linuxandryan.wordpress.com/2013/03/07/creating-and-using-a-pgpass-file/

  Take Db dump ==>

  pg_dump -w -d kiwi -U postgres > kiwi_Db.dump

  Upload the Dump to google drive ==>

  gdrive upload kiwi/kiwi_Db.dump

  upload to specific folder (Folder id need to be passed) ==>

  gdrive upload -p 1a7fGTdmdukydMlk7Np6X8ymOmSYNk66U kiwi_Db.dump

To make this process scheduled, keep the commands in crontab, make sure that gdrive path is set in crontab job.

  PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin


  pg_dump -w -d kiwi -U postgres > /home/ubuntu/kiwi_backup/kiwi_Db.dump && gdrive upload  -p   1a7fGTdmdukydMlk7Np6X8ymOmSYNk66U /home/ubuntu/kiwi_backup/kiwi_Db.dump

How to create crontab? Follow the link:
  https://askubuntu.com/questions/2368/how-do-i-set-up-a-cron-job



Products Configuration:
----------------------
After adding products and its details on server, it's must to add the details in product.py file
products.py is used to add the default values given in this file for a product while adding test cases,
test plans and test runs from spreadsheet.

Change WAIVED status to UN-AUTO:
-------------------------
  update test_case_run_status set name='UN-AUTO' where case_run_status_id=8;


Reading Job output from Jenkins:
--------------------------------
To read the job output from jenkins, output.xml must be in WS folder ( workspace ).
  http://jenkins.<URL>.com/job/<job_name>/ws/

plivo_tcms commands:
--------------------
Once you are in project directory, Run the below command to get the lists and usage of all the commands.

  python3 plivo_tcms.py -h

command to add test cases from spreadsheet

  python3 plivo_tcms.py -spreadsheetid_product <Spreadsheet_id> <Product>

  python3 plivo_tcms.py -spreadsheetid_product 1K4sY5CuZQgolm82bfs3MzuaEzrByg2BSruS6UQ5FC5Q sms


change the status from jenkins_job to specific the test_runs

  python3 plivo_tcms.py -jenkins_job <job_name> <test_run_id>

  python3 plivo_tcms.py -jenkins_job sms_smoke 15

change the status from jenkins_job to all the test_runs having same test case

  python3 plivo_tcms.py -jenkins_job <job_name>

  python3 plivo_tcms.py -jenkins_job sms_smoke


create a test run and plan from jenkin_job

  python3 plivo_tcms.py -add_testcase_from_jenkins <Job_name> <Product> <Plan_name> <Test_run_name>

  python3 plivo_tcms.py -add_testcase_from_jenkins sms_smoke sms smoke_plan smoke_run



Running server from Local using SSH :
====================================
  ssh -i <path_to_pem_file> ubuntu@<EC2_Public_DNS> sudo python3  /home/ubuntu/Kiwi/manage.py runserver 0.0.0.0:80

  ssh -i <path_to_pem_file> ubuntu@<EC2_Public_DNS>sudo python3  /home/ubuntu/Kiwi/plivo_tcms.py -h

  ssh -i <path_to_pem_file> ubuntu@<EC2_Public_DNS> sudo python3  /home/ubuntu/Kiwi/plivo_tcms.py -spreadsheetid_product 1K4sY5CuZQgolm82bfs3MzuaEzrByg2BSruS6UQ5FC5Q sms
