# Company Document Manager

In this project we create a basic infraestructure for an application running in an AWS EC2 instance. Here we upload the structure, the styles, and the api logic so our application runs from the cloud. The AWS FASTAPI will manage the requests so we can upload and download pictures from an S3 Bucket that our EC2 instance has access to.

<br>


## Description

This practice is a web application developed with FastAPI and AWS S3 that enables organizations to upload documents in a AWS S3 Bucket, where the members of the company can have access to the documents, can search by filters and upload new resources. The idea is to establish the basic structure to communicate an EC2 instance, where our app runs, with the Bucket. With this we have a simple system where the app with the logic of main.py receives requests from the client, and the instance is in charge of communicating with the bucket to upload or get documents.

<br>


## Configuration of AWS Credentials

**Enter to AWS Sandbox and copy new credentials**    
```Details - Show - AWS CLI - Show```

<br>

**Configure credentials in Ubuntu bash**   
Open ubunto bash:       
```aws configure```  

Enter this data:     
```AWS Access Key ID```  
```AWS Secret Access Key```  
```AWS Session Token```  
```Default region name [us-east-1]```    
```Default output format [json]``` 

<br>

**See if AWS credentials were correctly configured**     
```cat ~/.aws/credentials```   

<br>

**Deactivate paginator less to avoid visual errors:**     
```export AWS_PAGER=cat```

<br>

**Create SSH key pair and saves in document:**    
```aws ec2 create-key-pair --key-name <ssh-key-name> --query 'KeyMaterial' --output text > <ssh-key-name>.pem ```
    
<br>

**Establish permisions for SSH remote connection:**   
```chmod 400 <ssh-key-name>.pem```  

<br>


## Create Resources

### S3 bucket:

Here we will have our Application where the user manages the documents. Our EC2 instance has the following components:
- main.py: our API with all the application logic
- index.html: the interface of our application

**Create bucket:**   
```aws s3 mb s3://<bucket-name> --region us-east-1```        

<br>


### EC2 Instance

**Create security groups (virtual firewall for EC2):**    
```aws ec2 create-security-group --group-name <security-group-name> --description "<security-group-description>" --region us-east-1 --query 'GroupId' --output text```

Last command returns the security group: ```<sg-id>```

<br>

**Open SSH port 22 to manage EC2 instance:**     
```aws ec2 authorize-security-group-ingress --group-id <sg-id> --protocol tcp --port 22 --cidr 0.0.0.0/0 ```   

<br>

**Open SSH port 8080 to access the EC2 instnace:**     
```aws ec2 authorize-security-group-ingress --group-id <sg-id> --protocol tcp --port 8080 --cidr 0.0.0.0/0```     

<br>

**Verify the ports are correctly opened:**    
```aws ec2 describe-security-groups --group-ids <sg-id> --query 'SecurityGroups[].IpPermissions'```    

<br>

**Create EC2 instance**  
```aws ec2 run-instances --image-id ami-0c1fe732b5494dc14 --count 1 --instance-type <instance-type-size> --key-name <ssh-key-name> --security-groups <security-group-name> --region us-east-1 --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=<instance-name>}]'```   

<br>

**Obtain public IP to connect to app with SSH**  
```aws ec2 describe-instances --filters "Name=tag:Name,Values=<instance-name>" --query 'Reservations[].Instances[].PublicIpAddress' --output text --region us-east-1```

Last command returns the instance ip: ```<ec2-ip>```

<br>


## Application

### Copy app code using (Secure Copy Protocol) SCP 

Copy local code to a new remote or local host via SSH, for deploying, updating settings or moving from servers our apps.     
For this open 2 terminals one to conect to EC2 instance and the other to copy the code.

**Terminal 1:**

**Conect to remote with SSH**    
```ssh -i <ssh-key-name.pem> ec2-user@<ec2-ip>```  

<br>

**Remote sesion uses color color palette of 256**    
```export TERM=xterm-256color```

<br>

**Terminal 2:**

**Go to the directory where the files you want to copy to EC2 instance**         
```cd "/mnt/d/<project-folder-route>"```

<br>

**Copy Copies files and folders to remote system using SCP Protocol**    
```scp -i ~/<ssh-key-name.pem> -r src ec2-user@<ec2-ip>:/home/ec2-user  ```

Return to Terminal 1

<br>

**Verify files were uploaded**   
```cd src```     
```ls```

<br>

**Install and update dependencies**      
```cd ..```      
```sudo yum update -y```     
```sudo yum install -y python3.13```     
```sudo yum install -y ca-certificates```    
```sudo update-ca-trust```  

<br>

**Get AWS Credentials**  
```Details - Show - AWS CLI - Show```

<br>

**Create folder and paste credentials**  
```mkdir -p ~/.aws```    
```vi ~/.aws/credentials ```

<br>

**Exit credentials file**    
```esc```    
```:wq```

<br>

**See if AWS credentials were correctly configured**     
```cat ~/.aws/credentials```

<br>

**Run server application from a virtual environment to the EC2 instance**    
```cd src```     
```python3.13 -m venv venv```    
```source venv/bin/activate```   
```pip install -r requirements.txt```    
```python main.py```

<br>


### Test Application

**See automatic documentation generated**    
```<ec2-ip>:8080/docs ```

<br>

**See interface**    
```<ec2-ip>:8080```

**You can use these commands**   
```curl -X POST -F "file=@/path/to/pic01.jpeg" http://<ec2-ip>:8080/upload```

```curl "http://<ec2-ip>:8080/list"```

```curl "http://<ec2-ip>:8080/download/pic01.jpeg" -o downloaded.jpg```
