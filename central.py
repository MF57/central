import requests
from flask import Flask
import uuid
import time
import json

app = Flask(__name__)


def cleanup(src_ip, dst_ip, measurement_id):
    try:
        requests.delete("http://" + src_ip + ":5000/measurement/udp/sender/" + measurement_id)
        requests.delete("http://" + dst_ip + ":5000/measurement/udp/responder/" + measurement_id)
        return True
    except:
        return False


@app.route('/udp/<src>/<dst>/<interval>/<measurement_type>')
def udp(src, dst, interval, measurement_type):
    measurement_id = str(uuid.uuid4())
    dst_ip = dst.split(":")[0]
    dst_port = dst.split(":")[1]
    src_ip = src.split(":")[0]
    src_port = src.split(":")[1]

    try:
        response = requests.post("http://" + dst_ip + ":5000/measurement/udp/responder/" + measurement_id +
                                 "?self_port=" + dst_port, timeout=5)
        if response.status_code != 200:
            cleanup(src_ip, dst_ip, measurement_id)
            return "COULD NOT START LISTENING ON HOST " + dst, 500
    except:
        cleanup(src_ip, dst_ip, measurement_id)
        return "COULD NOT START LISTENING ON HOST " + dst, 500

    try:
        response = requests.post("http://" + src_ip + ":5000/measurement/udp/sender/" + measurement_id +
                                 "?self_port=" + src_port + "&target_address=" + dst_ip + "&target_port=" + dst_port +
                                 "&interval_s=" + str(interval))
        if response.status_code != 200:
            cleanup(src_ip, dst_ip, measurement_id)
            return "COULD NOT START BROADCASTING ON HOST " + src, 500
    except:
        cleanup(src_ip, dst_ip, measurement_id)
        return "COULD NOT START BROADCASTING ON HOST " + src, 500

    print "Created measurements"

    time.sleep(float(interval) + 1.0)

    print "Sleep ended"

    try:
        responder_response = requests.get("http://" + dst_ip + ":5000/measurement/udp/responder/" + measurement_id)
        if responder_response.status_code != 200:
            cleanup(src_ip, dst_ip, measurement_id)
            return "COULD NOT RETRIEVE RESPONDER TIME FROM HOST " + dst, 500
    except:
        cleanup(src_ip, dst_ip, measurement_id)
        return "COULD NOT RETRIEVE RESPONDER TIME FROM HOST " + dst, 500

    try:
        sender_response = requests.get("http://" + src_ip + ":5000/measurement/udp/sender/" + measurement_id)
        if sender_response.status_code != 200:
            cleanup(src_ip, dst_ip, measurement_id)
            return "COULD NOT RETRIEVE SENDER TIME FROM HOST " + src, 500
    except:
        cleanup(src_ip, dst_ip, measurement_id)
        return "COULD NOT RETRIEVE SENDER TIME FROM HOST " + src, 500

    try:
        receiver_response = requests.get("http://" + src_ip + ":5000/measurement/udp/receiver/" + measurement_id)
        if receiver_response.status_code != 200:
            cleanup(src_ip, dst_ip, measurement_id)
            return "COULD NOT RETRIEVE RECEIVER TIME FROM HOST " + src, 500
    except:
        cleanup(src_ip, dst_ip, measurement_id)
        return "COULD NOT RETRIEVE RECEIVER TIME FROM HOST " + src, 500

    try:
        responder_time = json.loads(responder_response.text)['timestamp']
        sender_time = json.loads(sender_response.text)['timestamp']
        receiver_time = json.loads(receiver_response.text)['timestamp']

        print "Results Readed"

        cleanup(src_ip, dst_ip, measurement_id)

        print "Measurements Deleted"

        if measurement_type == "one_way_source_target":
            return responder_time - sender_time, 200
        elif measurement_type == "one_way_target_source":
            return receiver_time - responder_time, 200
        elif measurement_type == "two_way":
            return receiver_time - sender_time, 200

        return 'NOT SUPPORTED MEASUREMENT TYPE', 500
    except:
        cleanup(src_ip, dst_ip, measurement_id)
        return "COULD NOT COMPUTE TIME FROM HOSTS RESPONSES", 500


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
