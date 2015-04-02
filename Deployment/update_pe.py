import boto
import os
from boto.s3.key import Key
from boto.s3.connection import S3Connection
import time
import datetime
import os.path
import sys
import codecs
import ntplib

#load
deployment_dir= '/home/pi/3io/Deployment'
credential_file = deployment_dir+'/credentials.csv'
if(os.path.isfile(credential_file) == False):
    sys.exit(0)

success = False;
count = 0;
while((count < 5) and (success ==False)):
    try:
        client = ntplib.NTPClient()
        response = client.request('pool.ntp.org')
        os.system('date ' + time.strftime('%m%d%H%M%Y.%S',time.localtime(response.tx_time)))
        now = datetime.datetime.now()
        print str(now)
        success = True
    except (KeyboardInterrupt, SystemExit):
        raise
    except:
        time.sleep(5)
        count = count + 1
        


#print str(datetime.now())
#except:
#print('Could not sync with time server.')
lines = ""
#with codecs.open(credential_file,'r',encoding='utf8') as txt:
    
txt = open(credential_file, "r")
lines = txt.readlines()

print ', '.join(lines)
data = lines[1].split(',')
username = data[0]
access_key = data[1]
access_secret = data[2]
username = username.replace('"', '')
txt.close()
print "connecting w key: "+access_key+" and secret: "+access_secret
username = username.strip()
access_key = access_key.strip()
access_secret = access_secret.strip()

#s3 = S3Connection(access_key, access_secret)
#s3 = S3Connection("AKIAIY2QVB5E5A36B3EQ", "4NsfcpHy/ulYCSvd1MMWPONBJNTUFrmg+nQRSuQg")
s3 = boto.s3.connect_to_region('us-west-2',
       aws_access_key_id=access_key,
       aws_secret_access_key=access_secret,
       is_secure=True,               # uncommmnt if you are not using ssl
       calling_format = boto.s3.connection.OrdinaryCallingFormat(),
       )
local_path = os.path.dirname(os.path.realpath(__file__))
print "storing to: "+local_path
mybucket = s3.get_bucket('photonmotion', validate=False)

for key in mybucket.list():
    
    keyString = key.name.encode('utf-8')
    #print "running for keystring: "+keyString
    #make sure folder structure exists
    folders = keyString.split("/")
    bucket_path = "/"
    for i in range(len(folders)):
        bucket_path = bucket_path+folders[i]
        if(i == (len(folders)-1)):
            #print "creating file: "+local_path+bucket_path
            key.get_contents_to_filename(local_path+bucket_path)
            os.chmod(local_path+bucket_path, 755)
        else:
            dir = local_path+bucket_path
            if(os.path.isdir(dir) == False):
                #print "creating dir "+dir + " for keystring: "+keyString
                os.makedirs(dir)
                
            bucket_path = bucket_path+"/"

#log that this event actually happened on the server
txt = open(deployment_dir + '/tmplog.txt', 'w')
txt.write(username +" downloaded an updated version of the code at "+datetime.datetime.now().strftime("%H:%M:%S  %m-%d-%y"))
txt.close()

b = s3.get_bucket('photonlog', validate=False) # substitute your bucket name here
k = Key(b)
k.key = username+'/'+datetime.datetime.now().strftime("%H:%M:%S  %m-%d-%y") + 'download_log'
k.set_contents_from_filename(deployment_dir + '/tmplog.txt')
os.remove(deployment_dir + '/tmplog.txt')

