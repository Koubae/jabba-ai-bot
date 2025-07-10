jabba-ai-bot
============


The AI Bot of jabba-ai  🧠


* [jabba-ai](https://github.com/Koubae/jabba-ai)

<p align="center">
  <img src="docs/imgs/jabba.webp" />
</p>



QuickStart
----------


### Local development

```bash
make run
```

* http://127.0.0.1:20003

**Keep in mind that this will start with the `testings-mock` ML Model**

### Set a specific ML model

You can either change in your `.env` variable

* `BOT_ML_MODEL=testings-mock`
* `BOT_ML_MODEL=openchat`
* `BOT_ML_MODEL=neural-chat`

Or use these Make commands

```bash
make run-ml-testings-mock
make run-ml-openchat
make run-neural-chat
```

### Run a Chat client

there are 2 simple chat clients for testings

#### HTTP

* [test_multi_client_http_protocol.html](./tests/e2e/test_multi_client_http_protocol.html) **_(recommended)_**

#### WebSockets

* [test_multi_client.html](./tests/e2e/test_multi_client.html) **_(recommended)_**
* [test_client.html](./tests/e2e/test_client.html)

### Send Chat message via HTTP

```bash
 curl -X POST http://127.0.0.1:20003/ai/http/bot/send-message/session-001 -H "Content-Type: application/json" -d '{"message": "Hello World"}'; echo
```


### Install black (formatter) globally

```bash
sudo apt install black -y
```


### All endpoints

* http://127.0.0.1:20003
* http://127.0.0.1:20003/ping
* http://127.0.0.1:20003/alive
* http://127.0.0.1:20003/ready
* http://127.0.0.1:20003/docs


### About the different ML models

At the moment there are 3 ML models; well really 2 as the 3rd one is a fake model used for testings/mocking

#### testings-mock

Is a mock ML, is not even an ML. 
It should be used for testing or while developing.
The only thing that it does is reversing the prompt.

Example 
* prompt: `hello`
* reply: `olleh` (to make you feel Spanish, and if you already are then Spanish x 2)

#### openchat

#### neural-chat
