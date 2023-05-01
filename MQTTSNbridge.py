from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
import MQTTSNclient
import json
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--port', type=int, help='Port number', default=1885)
parser.add_argument('--host', help='Host MQTT-SN',default='localhost')
parser.add_argument('--topic', help='Topic',default='sensors')
args = parser.parse_args()

port = args.port
host = args.host
topic = args.topic

# clients for MQTT and MQTTS
MQTTClient = AWSIoTMQTTClient("MQTTSNbridge")
MQTTSNClient = MQTTSNclient.Client("bridge", port=port, host=host)

class Callback:
  # function that replies a message from the MQTTSN broker to the MQTT one
  # and inserts into the database the message just arrived
  def messageArrived(self, topicName, payload, qos, retained, msgid):
      message = payload.decode("utf-8")
      print(topicName, message)
      MQTTClient.publish(topicName, message, qos)
      return True

# path that indicates the certificates position
path = "./certs/"

# configure the access with the AWS MQTT broker
MQTTClient.configureEndpoint("a27i3bls8pki37-ats.iot.us-east-1.amazonaws.com", 8883)
MQTTClient.configureCredentials(path+"AmazonRootCA1.pem",
                                path+"private.pem.key",
                                path+"certificate.pem.crt")

# configure the MQTT broker
MQTTClient.configureOfflinePublishQueueing(-1)  # Infinite offline Publish queueing
MQTTClient.configureDrainingFrequency(2)  # Draining: 2 Hz
MQTTClient.configureConnectDisconnectTimeout(10)  # 10 sec
MQTTClient.configureMQTTOperationTimeout(5)  # 5 sec

# register the callback
MQTTSNClient.registerCallback(Callback())

# make connections to the clients
MQTTClient.connect()
MQTTSNClient.connect()

MQTTSNClient.subscribe(topic)
# cycle that wait for a command to close the program
while True:
    if input("Enter 'quit' to exit from the program.\n")=="quit":
        break

# disconnect from the clients
MQTTSNClient.disconnect()
MQTTClient.disconnect()
