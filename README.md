# README

AWS SQS provides features like visibility timeout, queues, and messages, making it easier to use queues in distributed systems. Distributed processing is not limited to AWS; there are various scenarios where it can be useful, such as inter-application communication within the same computer or on-premises environments. This time, we prepared a Python implementation that enables SQS-like queue operations using Redis. To access Redis from Python, we used [redis-py](https://github.com/redis/redis-py).

## Queue Operations

### 1. Creating a Queue and Setting Data (Supports dict Type)
```python
from RediQ import RediQ
redisObj = RediQ()    
for i in range(1000):
    redisObj.set_message({'value':"a"+str(i),'number':1000-i})
```
### 2. Checking Queue Length (Visible Queue/Invisible Queue)

```python
print(redisObj.check_queue_length())
print(redisObj.check_holdqueue_length())
```
### 3. Retrieving and Consuming Messages
```python
for i in range((redisObj.check_queue_length())):
    mes = redisObj.get_message()
    mesId = mes['messageID']
    #---something job----
    redisObj.consume_message(messageID=mesId)
```

### Reference: Message Structure
```python
{'queueID': 'rediQ:b4a9e49ccac14106bcc3feaa11a08c6d',
 'setTime': '2025-04-05T17:09:54.182529',
 'messageID': 'rediQ:b4a9e49ccac14106bcc3feaa11a08c6d_38bdd7576ca446439cd587bff71e818c',
 'content': {'value': 'a999', 'number': 1},
 'visibleTime': '100'}
```
### License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.