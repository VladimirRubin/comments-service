import json
from ws4redis.publisher import RedisPublisher
from ws4redis.redis_store import RedisMessage


def notification_comment(content_type, object_id, data):
    redis_publisher = RedisPublisher(facility='notification-{0}-{1}'.format(content_type, object_id), broadcast=True)
    message = RedisMessage(json.dumps(data))
    redis_publisher.publish_message(message)
