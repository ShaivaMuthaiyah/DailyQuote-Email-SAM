import boto3
import simplejson as json 
import os 
import uuid
from datetime import datetime
import logging
import requests
import random
from sendgrid import SendGridAPIClient #Third party mailer app named SendGrid(requires layer)
from sendgrid.helpers.mail import Mail #Third party mailer app named SendGrid(requires layer)

s3 = boto3.client('s3')   #access the s3 bucket from aws
bucket = os.environ.get('QUOTE_BUCKET')

dynamodb = boto3.resource('dynamodb') #access the dynamodb table from aws
table_name = os.environ.get('USERS_TABLE')
table = dynamodb.Table(table_name) 


obj = s3.get_object(Bucket=bucket, Key= "quotes.json") #access the quotes.json file that has the quotes we want 
file_content = obj['Body'].read().decode('utf-8')
quotes = json.loads(file_content)

sns_client = boto3.client('sns') #access sns from aws
topic = os.environ.get('QUOTES_TOPIC')

logger = logging.getLogger('customer_details')   #logging helps print log messages
logger.setLevel(logging.INFO)


#looks at the s3 document and fetches a random quote along with its respective author
def get_quote(event, context):

    random_number = random.randint(0, len(quotes['quotes']))

    random_quote = quotes['quotes'][random_number]['quote']
    author_quote = quotes['quotes'][random_number]['author']

    return {
        'statusCode': 200,
        'headers': {'Content-type':'application/json'},
        'body': json.dumps({'quote': random_quote, 'author': author_quote })

    }


#looks through the dynamodb table and gets a list of emails of whoever has subscribed
def getSubscribers(event, context):

    email_content = table.scan(AttributesToGet=['email'])

    mailer_list =[] #empty list of emails

    number_of_emails = len(email_content['Items'])

    for n in range(0, number_of_emails) :

        single_email = email_content['Items'][n]['email'] #looping through items in the table and fetching email

        mailer_list.append(single_email) #list of emails to return


    return {
            'statusCode': 200,
            'headers': {'Content-type':'application/json',
                        'Access-Control-Allow-Origin':'*'},
            'body': json.dumps(mailer_list)
        }


#takes details from the form submitted and extracts it, saves it to the table with id and other information
def save_user_details(event, context): 

    now = datetime.now() #store the current time details 

    data = json.loads(event['body'])


    if isinstance(data['email'], str) != True :  #if the data in the email field is not a string it will be an error

        logger.info('Validation Failed')

        return

    else :

        subscriber_details= {

                    'userid': str(uuid.uuid4()), #generates a random large id 
                    'email': data['email'],
                    'subscribed': True,        #fills the table with id and attributes for the primary key
                    'createdAt': str(now.strftime("%d/%m/%Y %H:%M:%S")),
                    'updatedAt': str(now.strftime("%d/%m/%Y %H:%M:%S")), #creates a timestamp for the info saved
                }

        response = table.put_item(  #puts the information into the dynamodb table we created

            Item = subscriber_details

        )    


        return {
            'statusCode': 200,
            'headers': {'Content-type':'application/json',
                        'Access-Control-Allow-Origin':'*'},
            'body': json.dumps(subscriber_details)
        }
    
#sends api requests to activate other functions and notify the owner of subscriber details
def staticMailer(event, context):

    data = json.loads(event['body']) #takes the information from the body of the request
   
    url =  'https://5bgn5ayjal.execute-api.us-west-2.amazonaws.com/Stage/static-mailer'  
    
    post_request = requests.post(url, {'email': data['email']})   #makes a POST requests with the email as the body

    emailBody = buildEmailBody(event["requestContext"]["identity"], data)  #body of the email sent to the owner about the new subscriber

    save_url =  'https://5bgn5ayjal.execute-api.us-west-2.amazonaws.com/Stage/subscribe' #POST api to activate the subscriber information

    save_details = requests.post(save_url, json=data) #activates the function to store details into dynamodb

    publishToSNS(input_message= emailBody) #sends the details of the subscriber to the owner


    return {

            'statusCode': 200,
            'headers': {'Access-Control-Allow-Credentials': False,
                        'Access-Control-Allow-Origin':'*'},
            'body': json.dumps({'message': 'Ok'}),
        }

#the main function that sends the email by gathering all the necessary information
def sendEmail(event, context):


    subscribers_json = getSubscribers(event, context)  #get list of subscribers in json format

    subscribers = json.loads(subscribers_json['body']) #convert the json into a list

    quote_content = get_quote(event, context) #get the quote and author from the table in json

    content_json = json.loads(quote_content['body']) #extract the information from the body of the response in python format

    random_quote = content_json['quote'] #get the quote from the body of the content

    author = content_json['author']  #get the author of the quote from the body of the content

    content = createEmail(random_quote=random_quote, author=author) #create the email with the necessary inputs like quote and author

    sendGridEmail(subscribers= subscribers, content= content) #send the email to sendgrid to send to everyone else

    return {

            'statusCode': 200,
            'headers': {'Access-Control-Allow-Credentials': False,
                        'Access-Control-Allow-Origin':'*'},
            'body': json.dumps({'Email': 'Sent'}),   #default response for our POST request
        }



#notification to the owner on who has registered or submitted the form
def publishToSNS(input_message) :

    sns_client.publish(  #publish our message to SNS
            TopicArn=topic,
            Message= json.dumps({'default': json.dumps(input_message)}),   #turns the message into json format to publish to SNS
            MessageStructure= 'json',
    )

#creates a dictionary from the items returned from the front-end form
def buildEmailBody(id, form):

    return {

        'Message': form['message'],
        'Name': form['name'],
        'Email': form['email'],
        'Service_Information': id['sourceIp'],
    }

#integration with the sendgrid third part mailer that sends the mails to the subscribers
def sendGridEmail(subscribers, content):

    message = Mail(    #the final email that is composed for sending
    from_email='ShaivaMuthaiya@gmail.com',
    to_emails= subscribers,
    subject='Quotes to brighten up your day',
    html_content= content )


    sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))  #api key to access the sendgrid email functionality
    response = sg.send(message)
    print(response.status_code)
    print(response.body)
    print(response.headers)

#except Exception as e:
    #print(e.message)


#the html body of the email that is sent to the subscriber
def createEmail(random_quote, author):

    #the first and second will replace the '%s' values in the html template dynamically
    first = random_quote
    second = author

    return  ('''<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
            <html lang="en">
        
            
            <body>
            <div class="container", style="min-height: 40vh;
            padding: 0 0.5rem;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;"> 
            <div class="card" style="margin-left: 20px;margin-right: 20px;">
                <div style="font-size: 14px;">
                <div class='card' style=" background: #DAF7A6 ;
                border-radius: 5px;
                padding: 1.75rem;
                font-size: 1.1rem;
                font-family: Menlo, Monaco, Lucida Console, Liberation Mono,
                    DejaVu Sans Mono, Bitstream Vera Sans Mono, Courier New, monospace;">
            
                <p>%s</p>
                <blockquote>by %s</blockquote>
            
            </div>
                <br>
                </div>
                
                
                <div class="footer-links" style="display: flex;justify-content: center;align-items: center;">
                    <a href="/" style="text-decoration: none;margin: 8px;color: #9CA3AF;">Unsubscribe?</a>
                
                </div>
                </div>
            
                    </div>
                
            </body>
            </html>'''%(first, second))

