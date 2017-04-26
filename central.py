import requests
from flask import Flask
import uuid
import time
from threading import Thread

app = Flask(__name__)


@app.route('/udp/<src>/<dst>/<interval>/<measurement_type>')
def udp(src, dst, interval, measurement_type):
    measurement_id = str(uuid.uuid4())
    dst_ip = dst.split(":")[0]
    dst_port = dst.split(":")[1]
    src_ip = src.split(":")[0]
    src_port = src.split(":")[1]
    requests.post("http://" + dst_ip + ":5000/measurement/udp/responder/" + measurement_id + "?self_port=" + dst_port)
    requests.post("http://" + src_ip + ":5000/measurement/udp/sender/" + measurement_id + "?self_port=" + src_port
                  + "&target_address=" + dst_ip + "&target_port=" + dst_port + "&interval_s=" + str(interval))

    print "Created measurements"

    time.sleep(float(interval) + 1.0)

    print "Sleep ended"

    responder_time = requests.get("http://" + dst_ip + ":5000/measurement/udp/responder/" + measurement_id)
    sender_time = requests.get("http://" + src_ip + ":5000/measurement/udp/sender/" + measurement_id)
    receiver_time = requests.get("http://" + src_ip + ":5000/measurement/udp/receiver/" + measurement_id)

    print "Results Readed"

    requests.delete("http://" + src_ip + ":5000/measurement/udp/sender/" + measurement_id)
    requests.delete("http://" + dst_ip + ":5000/measurement/udp/responder/" + measurement_id)

    if measurement_type == "one_way_source_target":
        return responder_time - sender_time
    elif measurement_type == "one_way_target_source":
        return receiver_time - responder_time
    elif measurement_type == "two_way":
        return receiver_time - sender_time

    return 'NOT SUPPORTED MEASUREMENT TYPE'


@app.route('/tcp/<src>/<dst>')
def tcp(src, dst):
    print 'http://' + src + "/trac/" + dst
    r = requests.get('http://' + src + "/trac/" + dst)
    return 'Hello World!'


@app.route('/icmp/<src>/<dst>')
def icmp(src, dst):
    print 'http://' + src + "/trac/" + dst
    r = requests.get('http://' + src + "/trac/" + dst)
    return 'Hello World!'


if __name__ == '__main__':
    app.run(threaded=True, port=5005)
