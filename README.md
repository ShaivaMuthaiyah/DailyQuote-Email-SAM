<!-- ABOUT THE PROJECT -->
## About The Project

This is a serverless application that sends automated emails to its subscribers using AWS architecture integrated with a front-end subscription form. The form collects information and calls API's to AWS to store information in DynamoDB. Once the details are stored, the application pulls content from S3 and triggers lambdas to call API's to form the email. The owner of the site is also notied using SNS whenever someone signs up. Once the content is pulled from the bucket, the lambdas also fetch the emails of the subscribers from the database and sends it to a third party app called SendGrid. This helps send the mails that are scheduled using event bridge.

Important:
* This project was done for us-west-2 (Oregon)
* Most of the items can be copied directly but some configuration has to be done

### Built With

This section should list any major frameworks/libraries used to bootstrap your project. Leave any add-ons/plugins for the acknowledgements section. Here are a few examples.

* Python
* AWS Lambda, SNS, API Gateway, EventBridge, DynamoDB, S3 and SAM
* YAML
* Python Flask
* HTML & CSS with AJAX 

### Prerequisites

Two key things required for this project are :

* AWS CLI 
* Send Grid verified email ( you can sign up for free at https://sendgrid.com/ )

<!-- GETTING STARTED -->
### Getting Started

After setting up the AWS CLI you can use this command inside whicever directory you want to start the project

* Initialise a SAM Project
  ```sh
  sam init
  ```

Set it up with the language you want to work with and choose the 'Hello World' example project as a base. You can follow this guide here (https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-getting-started-hello-world.html)
