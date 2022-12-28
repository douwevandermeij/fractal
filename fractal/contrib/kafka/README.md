# Kafka

To test Kafka, you can use the enclosed `docker-compose.yml` and use the following settings:

    self.EVENT_BUS_BACKEND = os.getenv("EVENT_BUS_BACKEND", "kafka")

    self.KAFKA_HOST = os.getenv("KAFKA_HOST", "localhost")
    self.KAFKA_PORT = os.getenv("KAFKA_PORT", "9093")
    self.KAFKA_USERNAME = os.getenv("KAFKA_USERNAME", "")
    self.KAFKA_PASSWORD = os.getenv("KAFKA_PASSWORD", "")

And in your context:

    def load_event_projectors(self):
        ...

        if Settings().EVENT_BUS_BACKEND == "kafka":
            from fractal.contrib.kafka.projectors import (
                KafkaEventBusProjector,
            )
            from app.service.domain.events.sending import ...

            projectors.append(
                KafkaEventBusProjector(
                    host=Settings().KAFKA_HOST,
                    port=Settings().KAFKA_PORT,
                    username=Settings().KAFKA_USERNAME,
                    password=Settings().KAFKA_PASSWORD,
                    service_name=Settings().APP_NAME,
                    aggregate="...",
                    event_classes=[
                        ...
                    ],
                )
            )
