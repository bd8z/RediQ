import redis
import uuid
from datetime import datetime
import json
class RediQ:
    def __init__(self):
        self.redis = redis.Redis(host='localhost', port=6379, db=0)
        name = 'rediQ:' + str(uuid.uuid4()).replace("-","")
        self.QueueName = name
        self.holdQueueName = name + "_hold"
        self.visibleTime = 100 #visible time

    def set_message(self, dictValue):
        u_ = self.QueueName + "_" + str(uuid.uuid4()).replace("-","")
        self.redis.rpush(self.QueueName, u_)
        hv_ = {"content":json.dumps(dictValue)}
        hv_["setTime"] = datetime.now().isoformat()
        hv_["messageID"] = u_
        hv_["queueID"] = self.QueueName
        hv_["visibleTime"] = self.visibleTime
        for ky in list(hv_.keys()):
            self.redis.hset(u_, ky, str(hv_[ky]))

    def get_message(self):
        self._reset_visiblity()
        b_ = self.redis.lpop(self.QueueName)
        self.redis.rpush(self.holdQueueName, b_)
        r_ = {}
        hv_ = self.redis.hgetall(b_)
        for ky in list(hv_.keys()):
            r_[ky.decode('utf-8')] = hv_[ky].decode('utf-8')
        r_["content"] = json.loads(r_["content"])
        return r_
    
    def consume_message(self,messageID):
        self._reset_visiblity()
        if self._check_message_visibility(messageID):    
            if not(self.redis.exists(messageID) == 0):
                self.redis.delete(messageID)
                self.redis.lrem(self.holdQueueName, 0, messageID)
        else:
            pass
    
    def _reset_visiblity(self):
        def _reset_visiblity_func():
            b_ = self.redis.rpop(self.holdQueueName)
            t_ = self.redis.hget(b_, "setTime").decode('utf-8')
            v_ = int(self.redis.hget(b_, "visibleTime").decode('utf-8'))
            dt = datetime.now() - datetime.fromisoformat(t_)
            secFromLastUpdate = dt.total_seconds()
            if secFromLastUpdate > v_:
                self.redis.rpush(self.QueueName, b_)
            else:
                self.redis.rpush(self.holdQueueName, b_)
        len_ = self.redis.llen(self.holdQueueName)
        for _ in range(len_):                
            _reset_visiblity_func()

    def _check_message_visibility(self,mesID):
        if self.redis.exists(mesID) == 0:
            return False
        else:
            hv_ = self.redis.hgetall(mesID)
            dt = datetime.now() - datetime.fromisoformat(hv_[b"setTime"].decode('utf-8'))
            secFromLastUpdate = dt.total_seconds()
            if secFromLastUpdate > int(hv_[b"visibleTime"].decode('utf-8')):
                return False
            else:
                return True

    def check_queue_length(self):
        self._reset_visiblity()
        return self.redis.llen(self.QueueName)
    
    def check_holdqueue_length(self):
        self._reset_visiblity()
        return self.redis.llen(self.holdQueueName)