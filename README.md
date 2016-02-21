# A boilerplate for python Telegram Bots
Get your telegram bot key and insert into the bot.py file. Follow deployment instructions to get the initial environment setup.

I use the [Telepot](https://github.com/nickoala/telepot "Telepot") framework.

To run locally inside of your virtual environment, just run
	python bot.py

## Deployment to AWS instructions
* Create the bot
* Configure dev environment
* Configure an AWS IAM role with permissions to execute bot related things
* Write an AWS Lambda function in Python to handle incoming bot messages
* Deploy the Lambda function
* Test the Lambda function
* Create an AWS API Gateway endpoint that when hit, activates your Lambda function
* Deploy and test the API endpoint
* Set the bot's webhook to the API Gateway endpoint


### Creating the bot
You can easily create a bot by talking to the [BotFather](https://telegram.me/botfather "Telegram BotFather") on Telegram. I won't rewrite the instructions, because they are already [on the Telegram website,](https://core.telegram.org/bots#botfather "Botfather instructions") and the BotFather also provides pretty solid instructions as you go. Just make sure you copy your API key down once it's given to you.

### Configuring dev environment
To quickly create working bots, I use the [Telepot](https://github.com/nickoala/telepot "Telepot python telegram bot framework") python framework instead of using the Requests library to directly hit the Telegram HTTP API. Telepot is a light framework and takes care of many annoying things right out of the box. Other than using Telepot, the only important characteristic is to make sure the dev environment is running Python 2.7, because that is what AWS Lambda supports. If you are mainly operating in Python 3+ at this point like I am, be sure to create your virtual environment like this

	virtualenv -p /usr/bin/python2.7 venv

### Configuring an AWS IAM role
As with anything AWS-related, you need an IAM role with access to specific resources and must give it a set of execution permissions before anything starts working properly. If you are like me, configuring IAM permissions is by far the most annoying part and is always where I stumble on new projects. To set one up that can run your Telegram bot, login to the [IAM console](https://aws.amazon.com/iam/ "AWS IAM console") and navigate to the "Roles" section. Create a new role. I name mine "lambda-gateway-execution-role." In the permissions section, attach the following policies to the role:

* AWSLambdaBasicExecutionRole
* AmazonAPIGatewayInvokeFullAccess
* AmazonAPIGatewayPushToCloudWatchLogs
* CloudWatchFullAccess
* CloudWatchLogsFullAccess
* AmazonAPIGateWayAdministrator


### Writing the Lambda function that handles incoming bot messages
Allow me to briefly nerd out about [AWS Lambda](https://aws.amazon.com/lambda/ "AWS Lmbda"), which is just really cool and awesome and useful service. Lambda functions are executed based on event triggers, which is great, but an even better thing is that you don't need to configure or provision any servers. Amazon only charges you for the compute time you consume, which for a basic Telegram bot, is basically nothing. Event driven architectures are da bomb, yo!!

There are two important parts to getting a Telegram bot to work as an AWS Lambda Function: 

1. A default Lambda handler to deal with incoming events (you need to specify the name of this handler when you create your Lambda function)
2. A function to parse the incoming messages and return the appropriate response

The Lambda event handler I use is dead simple. I print the incoming event to the console then pass it through to my parsing function. It looks like this

	def my_handler(event, context):
    	print("Received event: " + json.dumps(event, indent=2))
    	handle(event['message'])

The parsing function -- "handle(event['message'])" in the above code snippet -- will totally differ depending on what you actually want your bot to do. Most of my bots just parse various commands and then call helper functions to generate the appropriate responses. Regardless, Telegram recommends that every bot start with support for at least three commands: start, help, and settings. For those, the simple skeleton below will work. 

	def handle(msg):
	   flavor = telepot.flavor(msg)
	   # normal message
	   if flavor == ‘normal’:
	       content_type, chat_type, chat_id = telepot.glance2(msg)
	       print(‘Normal Message:’, content_type, chat_type, chat_id)
	       command = msg[‘text’]
	       if command == ‘/start’:
	           bot.sendMessage(chat_id, text='Hi! I am a Telegram Bot!!')
	       elif command == ‘/help’:
	           bot.sendMessage(chat_id, text="I don't have any help commands yet!")
	       elif command == ‘/settings’:
	           bot.sendMessage(chat_id, text="I cannot be configured via any settings yet. Check back soon!")
	       else:
	           bot.sendMessage(chat_id, text="Sorry, I didn't understand that command.")

	       return(‘Message sent’)
	 
	   else:
	       raise telepot.BadFlavor(msg)

I've created a [simple boilerplate](https://github.com/mamcmanus/telegram-awslambda-bot-boilerplate "Bot boilerplate") that you can use to get a bot supporting the start, settings, and help commands up and running in seconds.

	mkdir telegram-bot
	cd telegram-bot
	git init
	git clone https://github.com/mamcmanus/telegram-awslambda-bot-boilerplate.git
	virtualenv -p /usr/bin/python2.7 venv
	source venv/bin/activate
	pip install -r requirements.txt

Open bot.py and put your API key in on line 34.
	
	bot = telepot.Bot('BOT KEY')

Then, make sure you've added the bot on Telegram, and run the bot locally to start chatting with it! 
	
	python bot.py

### Deploying the Lambda function
To deploy, you need to first create a .ZIP of your lambda function, a requirements.txt file that lists any dependencies, and all of the contents of your venv/lib/python2.7/site-packages directory. 

You can then create a function using the AWS Lambda web console, and upload the .ZIP file as your source package. Follow these steps

* Sign into [AWS](https://aws.amazon.com "AWS console") and open the Lambda console. You can find the link for Lambda in the upper left corner under the "Compute" section.
* Create a new Lambda function
* Skip over the first step of selecting a blueprint, you already have one
* Name your function "bot" and set the runtime to Python 2.7
* Choose "Upload a .ZIP file" and upload the .ZIP of your function that you created 
* Set the Handler to "bot.my_handler" and create a basic execution role if you don't have one already
* Review and submit

### Testing the Lambda function

To test the Lambda function, you need data that simulates an actual person sending a message to the bot -- the JSON message body of a POST request to the Bot API, which looks like this

	{
	  "update_id": 8888,
	  "message": {
	    "chat": {
	      "first_name": "Matt",
	      "id": put_your_id_here,
	      "last_name": "McManus",
	      "type": "private",
	      "rolename": "mcman_s"
	    },
	    "date": 1453851465,
	    "from": {
	      "first_name": "Matt",
	      "id": put_your_id_here,
	      "last_name": "McManus",
	      "rolename": "mcman_s"
	    },
	    "message_id": 2,
	    "text": "/start"
	  }
	}

You need to replace "put_your_id_here" with your chat ID. You can get that ID by running the bot locally, sending it a message, and copying the id from the output in your terminal window. 

Once you have your test JSON blob, click the "Actions" dropdown and choose "Configure test event." Copy the JSON blob and hit "Save and test." 

You should get a message from your bot as if you had sent it the "/start" command.

### Creating an AWS API Gateway endpoint to activate the Lambda function
Go back to the AWS console, find "API Gateway" under the "Application Services" section and click on it. Then do some some stuff:

* Create a new API and name it "TelegramWebHook"
* Create a new POST method
* Select "Lambda function" as the integration type, select the region in which your Lambda function is deployed, and type in the name of your bot, which should auto-complete, then save it
* Deploy your API by creating a new stage, call it whatever you want, I just use the default "prod"
* Write down the Invoke URL for later

### Testing the API endpoint

* In the API Gateway console, navigate to the "/ - POST - Method Execution" page and click "Test"
* In the Request Body section, copy the same JSON blob you used to test your Lambda function, and then fire away

Once again, you should get a message from your bot as if you had sent it the "/start" command.

### Setting the bot's webhook
The final part to getting your bot up and running is setting up a webhook that calls your API gateway endpoint. To do that, curl the Telegram set webhook API endpoint and pass it the invoke url of your API endpoint that you copied down earlier. The curl command looks like this

	curl -X POST https://api.telegram.org/bot{your-api-key}/setWebhook \
	-d'url={your invocation url}}'

Add your own invocation url and bot API key

Now, send your bot a command and it should respond. 