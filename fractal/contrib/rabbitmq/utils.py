from typing import Tuple

import pika
from pika import BlockingConnection, PlainCredentials
from pika.adapters.blocking_connection import BlockingChannel


def setup_rabbitmq_connection(
    host, port, username, password
) -> Tuple[BlockingConnection, BlockingChannel]:
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            host=host,
            port=port,
            credentials=PlainCredentials(
                username=username,
                password=password,
            ),
        )
    )
    channel = connection.channel()
    return connection, channel
