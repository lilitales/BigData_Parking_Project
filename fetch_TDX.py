
import json
import datasource.mongodb as mongodb
from datasource.data import DataAccess
from datetime import datetime
from kafka import KafkaProducer, KafkaConsumer
import time
import random

city = 'Tainan'
db = mongodb.obtain_db()
data = DataAccess()
dateFormat = r"%Y-%m-%dT%H:%M:%S%z"
parkingAvail_collection_name = 'Time_ParkingAvailability'
realTime_parkingAvail_collection_name = 'RealTime_ParkingAvailability'


def insert_parkingAvail(parkInfo):
    col = db[parkingAvail_collection_name]
    # 用時間替代id
    str_now = datetime.strftime(datetime.now(), dateFormat)
    parkInfo['_id'] = str_now
    col.insert_one(parkInfo)


def deal_parkingAvail():
    """
    取剩餘車位,處理,存入DB流程
    """
    parkInfo = data.get_parkingAvail(city)
    insert_parkingAvail(parkInfo)


def reset_realTime_parkingAvail():
    """
    最新剩餘車位更新
    """
    col = db[parkingAvail_collection_name]
    # -1 :大到小排序
    cursor = col.find().sort({'_id': -1}).limit(1)
    latest_parkInfo = list(cursor)[0]

    insert_col = db[realTime_parkingAvail_collection_name]
    # 舊有清空
    insert_col.delete_many({})
    insert_col.insert_one(latest_parkInfo)


class KafkaImplParkingAvail():
    def __init__(self) -> None:
        # 取kafka address和topic name
        config = mongodb.load_json_file('config')
        server_config = mongodb.load_json_file('secret_connection')
        self.topic_name = config['topic_parkingAvail']
        self.server_address = server_config['kafka-server']

        producer = KafkaProducer(
            bootstrap_servers=self.server_address,
            # 讓json object 序列化
            value_serializer=lambda jsonObj:
                json.dumps(jsonObj).encode()
        )
        self.producer = producer

        consumer = KafkaConsumer(
            self.topic_name,
            bootstrap_servers=self.server_address,
            consumer_timeout_ms=5_000,
            enable_auto_commit=True,
            # TODO 不要使用earliest，這樣只會從最早的開始讀
            # TODO auto_offset_reset="earliest"
            auto_offset_reset='latest',
            auto_commit_interval_ms=2_000,  # 每x秒提交一次 offset
            group_id='test-group'
        )
        self.consumer = consumer

    def __del__(self):
        if self.producer:
            self.producer.close()
        # if self.consumer:
        #     self.consumer.close()

    def get_producer(self):
        return self.producer

    def get_consumer(self):
        return self.consumer

    def produce_parkingAvail(self):
        parkInfo = data.get_parkingAvail(city)

        producer = self.producer
        msg_obj = {'parkInfo': parkInfo,
                   'timestamp': datetime.strftime(datetime.now(), dateFormat)}
        producer.send(self.topic_name, msg_obj)

    def consume_parkingAvail(self):
        consumer = self.consumer
        # 等待topic
        for msg in consumer:
            msg_obj = json.loads(msg.value)
            insert_parkingAvail(msg_obj['parkInfo'])


if __name__ == '__main__':
    # kafka版本
    impl = KafkaImplParkingAvail()
    impl.produce_parkingAvail()
    time.sleep(1)
    print('producer done')
    impl.consume_parkingAvail()
    print('consumer done')

    # reset_realTime_parkingAvail()
