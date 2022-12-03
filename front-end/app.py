from flask import Flask, jsonify, render_template, request
import requests

app = Flask(__name__)

@app.route('/', methods=['GET','POST']) #allow both POST & GET requests in case of future edits

def index():
    if request.method == "POST":

        #collect all inputs from the form

        name = request.form['name']
        email = request.form['email']
        message = request.form['message']

        #sends a POST request to activate the lambda function with the information from the form

        url = 'https://5bgn5ayjal.execute-api.us-west-2.amazonaws.com/Stage/static-mailer'

        if name and email and message: #checks if all the inputs are given

            post_request = requests.post(url, json=
                            {'name': name,
                            'email': email,
                            'message': message})

            return jsonify({'output':'Thank you for subscribing!'}) #returns this response to the div with the output id 


 
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True, port=5000, host='0.0.0.0')