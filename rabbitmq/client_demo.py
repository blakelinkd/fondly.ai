import pika

# RabbitMQ connection parameters
rabbitmq_host = 'localhost'
rabbitmq_port = 5672
rabbitmq_username = 'guest'
rabbitmq_password = 'guest'
rabbitmq_virtual_host = '/'

# Create a connection to RabbitMQ
credentials = pika.PlainCredentials(rabbitmq_username, rabbitmq_password)
parameters = pika.ConnectionParameters(host=rabbitmq_host, port=rabbitmq_port, virtual_host=rabbitmq_virtual_host, credentials=credentials)
connection = pika.BlockingConnection(parameters)
channel = connection.channel()

# Declare a queue
queue_name = 'my_queue'
channel.queue_declare(queue=queue_name)

# Publish a message
message = 'Hello, RabbitMQ!'
channel.basic_publish(exchange='', routing_key=queue_name, body=message)
print("Message published:", message)

# Consume a message
def callback(ch, method, properties, body):
    print("Message received:", body.decode())
    ch.basic_ack(delivery_tag=method.delivery_tag)

channel.basic_consume(queue=queue_name, on_message_callback=callback)
channel.start_consuming()

# Close the connection
connection.close()
