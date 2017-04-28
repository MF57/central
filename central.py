import requests
from flask import Flask
import uuid
import time
import json

app = Flask(__name__)


#LOL xD
measurements = {}
icmp_counter = 0


@app.route('/udp/<src>/<dst>/<interval>', methods=["POST"])
def udp_start(src, dst, interval):
    global measurements
    if src + ";" + dst in measurements:
        return "THERE IS ALREADY A RUNNING MEASUREMENT FOR THESE HOSTS", 500

    measurement_id = str(uuid.uuid4())
    print measurement_id
    dst_ip = dst.split(":")[0]
    dst_port = dst.split(":")[1]
    src_ip = src.split(":")[0]
    src_port = src.split(":")[1]

    try:
        response = requests.post("http://" + dst_ip + ":5000/measurement/udp/responder/" + measurement_id +
                                 "?self_port=" + dst_port, timeout=5)
        if response.status_code != 200:
            return "COULD NOT START LISTENING ON HOST " + dst, 500
    except:
        return "COULD NOT START LISTENING ON HOST " + dst, 500

    try:
        response = requests.post("http://" + src_ip + ":5000/measurement/udp/sender/" + measurement_id +
                                 "?self_port=" + src_port + "&target_address=" + dst_ip + "&target_port=" + dst_port +
                                 "&interval_s=" + str(interval))
        if response.status_code != 200:
            return "COULD NOT START BROADCASTING ON HOST " + src, 500
    except:
        return "COULD NOT START BROADCASTING ON HOST " + src, 500

    measurements["udp" + ';' + src + ";" + dst] = measurement_id
    return "MEASUREMENT SUCCESSFULLY CREATED"


@app.route('/tcp/<src>/<dst>/<interval>', methods=["POST"])
def tcp_start(src, dst, interval):
    global measurements
    if src + ";" + dst in measurements:
        return "THERE IS ALREADY A RUNNING MEASUREMENT FOR THESE HOSTS", 500

    measurement_id = str(uuid.uuid4())
    dst_ip = dst.split(":")[0]
    dst_port = dst.split(":")[1]
    src_ip = src.split(":")[0]
    src_port = src.split(":")[1]

    try:
        response = requests.post("http://" + dst_ip + ":5000/measurement/tcp/server/" + measurement_id +
                                 "?self_port=" + dst_port, timeout=5)
        if response.status_code != 200:
            return "COULD NOT START LISTENING ON HOST " + dst, 500
    except:
        return "COULD NOT START LISTENING ON HOST " + dst, 500

    try:
        response = requests.post("http://" + src_ip + ":5000/measurement/tcp/client/" + measurement_id +
                                 "?self_port=" + src_port + "&target_address=" + dst_ip + "&target_port=" + dst_port +
                                 "&interval_s=" + str(interval))
        if response.status_code != 200:
            return "COULD NOT START BROADCASTING ON HOST " + src, 500
    except:
        return "COULD NOT START BROADCASTING ON HOST " + src, 500

    measurements["tcp" + ';' + src + ";" + dst] = measurement_id
    return "MEASUREMENT SUCCESSFULLY CREATED"


@app.route('/icmp/<src>/<dst>/<interval>', methods=["POST"])
def icmp_start(src, dst, interval):
    global measurements
    global icmp_counter
    if src + ";" + dst in measurements:
        return "THERE IS ALREADY A RUNNING MEASUREMENT FOR THESE HOSTS", 500

    measurement_id = str(icmp_counter)
    icmp_counter = icmp_counter+1
    dst_ip = dst.split(":")[0]
    src_ip = src.split(":")[0]

    try:
        response = requests.post("http://" + src_ip + ":5000/measurement/icmp/sender/" + measurement_id +
                                 "?target_address=" + dst_ip + "&interval_s=" + str(interval))
        if response.status_code != 200:
            return "COULD NOT START BROADCASTING ON HOST " + src, 500
    except:
        return "COULD NOT START BROADCASTING ON HOST " + src, 500

    measurements["icmp" + ';' + src + ";" + dst] = measurement_id
    return "MEASUREMENT SUCCESSFULLY CREATED"


###################################### DELETE  ###############################################################


@app.route('/udp/<src>/<dst>', methods=["DELETE"])
def udp_delete(src, dst):
    global measurements
    measurement = measurements["udp" + ';' + src + ';' + dst]
    dst_ip = dst.split(":")[0]
    src_ip = src.split(":")[0]

    if cleanup_udp(src_ip, dst_ip, measurement):
        measurements.pop(measurement, None)
        return "MEASUREMENT SUCCESSFULLY DELETED"
    else:
        return "THERE WERE ERRORS DURING DELETING MEASUREMENT", 500


def cleanup_udp(src_ip, dst_ip, measurement_id):
    try:
        requests.delete("http://" + src_ip + ":5000/measurement/udp/sender/" + measurement_id)
        requests.delete("http://" + dst_ip + ":5000/measurement/udp/responder/" + measurement_id)
        return True
    except:
        return False


@app.route('/tcp/<src>/<dst>', methods=["DELETE"])
def tcp_delete(src, dst):
    global measurements
    measurement = measurements["tcp" + ';' + src + ';' + dst]
    dst_ip = dst.split(":")[0]
    src_ip = src.split(":")[0]

    if cleanup_tcp(src_ip, dst_ip, measurement):
        measurements.pop(measurement, None)
        return "MEASUREMENT SUCCESSFULLY DELETED"
    else:
        return "THERE WERE ERRORS DURING DELETING MEASUREMENT", 500


def cleanup_tcp(src_ip, dst_ip, measurement_id):
    try:
        requests.delete("http://" + src_ip + ":5000/measurement/tcp/client/" + measurement_id)
        requests.delete("http://" + dst_ip + ":5000/measurement/tcp/server/" + measurement_id)
        return True
    except:
        return False


@app.route('/icmp/<src>/<dst>', methods=["DELETE"])
def icmp_delete(src, dst):
    global measurements
    measurement = measurements["icmp" + ';' + src + ';' + dst]
    src_ip = src.split(":")[0]

    if cleanup_icmp(src_ip, measurement):
        measurements.pop(measurement, None)
        return "MEASUREMENT SUCCESSFULLY DELETED"
    else:
        return "THERE WERE ERRORS DURING DELETING MEASUREMENT", 500


def cleanup_icmp(src_ip, measurement_id):
    try:
        requests.delete("http://" + src_ip + ":5000/measurement/icmp/sender/" + measurement_id)
        return True
    except:
        return False


@app.route('/udp/<src>/<dst>/<measurement_type>/measurement_section')
def udp(src, dst, measurement_type, measurement_section):
    global measurements
    measurement_id = measurements["udp" + ';' + src + ';' + dst]
    dst_ip = dst.split(":")[0]
    src_ip = src.split(":")[0]

    try:
        responder_response = requests.get("http://" + dst_ip + ":5000/measurement/udp/responder/" + measurement_id)
        if responder_response.status_code != 200:
            cleanup_udp(src_ip, dst_ip, measurement_id)
            return "COULD NOT RETRIEVE RESPONDER TIME FROM HOST " + dst, 500
    except:
        cleanup_udp(src_ip, dst_ip, measurement_id)
        return "COULD NOT RETRIEVE RESPONDER TIME FROM HOST " + dst, 500

    try:
        sender_response = requests.get("http://" + src_ip + ":5000/measurement/udp/sender/" + measurement_id)
        if sender_response.status_code != 200:
            cleanup_udp(src_ip, dst_ip, measurement_id)
            return "COULD NOT RETRIEVE SENDER TIME FROM HOST " + src, 500
    except:
        cleanup_udp(src_ip, dst_ip, measurement_id)
        return "COULD NOT RETRIEVE SENDER TIME FROM HOST " + src, 500

    try:
        receiver_response = requests.get("http://" + src_ip + ":5000/measurement/udp/receiver/" + measurement_id)
        if receiver_response.status_code != 200:
            cleanup_udp(src_ip, dst_ip, measurement_id)
            return "COULD NOT RETRIEVE RECEIVER TIME FROM HOST " + src, 500
    except:
        cleanup_udp(src_ip, dst_ip, measurement_id)
        return "COULD NOT RETRIEVE RECEIVER TIME FROM HOST " + src, 500

    try:
        responder_time = json.loads(responder_response.text)
        sender_time = json.loads(sender_response.text)
        receiver_time = json.loads(receiver_response.text)


        return 'NOT SUPPORTED MEASUREMENT TYPE', 200
    except:
        cleanup_udp(src_ip, dst_ip, measurement_id)
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
