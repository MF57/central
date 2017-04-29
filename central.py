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
    if "udp;" + src + ";" + dst in measurements:
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
    print measurements
    return "MEASUREMENT SUCCESSFULLY CREATED"


@app.route('/tcp/<src>/<dst>/<interval>', methods=["POST"])
def tcp_start(src, dst, interval):
    global measurements
    if "tcp;" + src + ";" + dst in measurements:
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
    print measurements
    return "MEASUREMENT SUCCESSFULLY CREATED"


@app.route('/icmp/<src>/<dst>/<interval>', methods=["POST"])
def icmp_start(src, dst, interval):
    global measurements
    global icmp_counter
    if "icmp;" + src + ";" + dst in measurements:
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
    print measurements
    return "MEASUREMENT SUCCESSFULLY CREATED"


###################################### DELETE  ###############################################################


@app.route('/udp/<src>/<dst>', methods=["DELETE"])
def udp_delete(src, dst):
    global measurements
    try:
        measurement = measurements["udp" + ';' + src + ';' + dst]
    except:
        return "THERE IS NO SUCH MEASUREMENT RUNNING", 500
    dst_ip = dst.split(":")[0]
    src_ip = src.split(":")[0]

    if cleanup_udp(src_ip, dst_ip, measurement):
        measurements.pop("udp" + ';' + src + ';' + dst, None)
        print measurements
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
    try:
        measurement = measurements["tcp" + ';' + src + ';' + dst]
    except:
        return "THERE IS NO SUCH MEASUREMENT RUNNING", 500
    dst_ip = dst.split(":")[0]
    src_ip = src.split(":")[0]

    if cleanup_tcp(src_ip, dst_ip, measurement):
        measurements.pop("tcp" + ';' + src + ';' + dst, None)
        print measurements
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
    try:
        measurement = measurements["icmp" + ';' + src + ';' + dst]
    except:
        return "THERE IS NO SUCH MEASUREMENT RUNNING", 500
    src_ip = src.split(":")[0]

    if cleanup_icmp(src_ip, measurement):
        measurements.pop("icmp" + ';' + src + ';' + dst, None)
        print measurements
        return "MEASUREMENT SUCCESSFULLY DELETED"
    else:
        return "THERE WERE ERRORS DURING DELETING MEASUREMENT", 500


def cleanup_icmp(src_ip, measurement_id):
    try:
        requests.delete("http://" + src_ip + ":5000/measurement/icmp/sender/" + measurement_id)
        return True
    except:
        return False


############################################################# GET   ###################################################

@app.route('/udp/<src>/<dst>/<measurement_type>/<measurement_section>', methods=["GET"])
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

        if measurement_section == "one_way_source_target":
            return handleResultData(measurement_type, responder_time, sender_time), 200
        elif measurement_section == "one_way_target_source":
            return handleResultData(measurement_type, receiver_time, responder_time), 200
        elif measurement_section == "two_way":
            return handleResultData(measurement_type, receiver_time, sender_time), 200

        print measurements
        return 'NOT SUPPORTED MEASUREMENT TYPE', 500
    except:
        cleanup_udp(src_ip, dst_ip, measurement_id)
        return "COULD NOT COMPUTE TIME FROM HOSTS RESPONSES", 500


@app.route('/tcp/<src>/<dst>/<measurement_type>', methods=["GET"])
def tcp(src, dst, measurement_type):
    global measurements
    measurement_id = measurements["tcp" + ';' + src + ';' + dst]
    dst_ip = dst.split(":")[0]
    src_ip = src.split(":")[0]

    try:
        server_response = requests.get("http://" + dst_ip + ":5000/measurement/tcp/server/" + measurement_id)
        if server_response.status_code != 200:
            cleanup_tcp(src_ip, dst_ip, measurement_id)
            return "COULD NOT RETRIEVE SERVER TIME FROM HOST " + dst, 500
    except:
        cleanup_tcp(src_ip, dst_ip, measurement_id)
        return "COULD NOT RETRIEVE RESPONDER TIME FROM HOST " + dst, 500

    try:
        client_response = requests.get("http://" + src_ip + ":5000/measurement/tcp/client/" + measurement_id)
        if client_response.status_code != 200:
            cleanup_tcp(src_ip, dst_ip, measurement_id)
            return "COULD NOT RETRIEVE SENDER TIME FROM HOST " + src, 500
    except:
        cleanup_tcp(src_ip, dst_ip, measurement_id)
        return "COULD NOT RETRIEVE SENDER TIME FROM HOST " + src, 500

    try:
        server_time = json.loads(server_response.text)
        client_time = json.loads(client_response.text)
        print measurements
        return handleResultData(measurement_type, server_time, client_time), 200

    except:
        cleanup_tcp(src_ip, dst_ip, measurement_id)
        return "COULD NOT COMPUTE TIME FROM HOSTS RESPONSES", 500


@app.route('/icmp/<src>/<dst>/<measurement_type>/<measurement_section>', methods=["GET"])
def icmp(src, dst, measurement_type, measurement_section):
    global measurements
    measurement_id = measurements["icmp" + ';' + src + ';' + dst]
    dst_ip = dst.split(":")[0]
    src_ip = src.split(":")[0]

    try:
        responder_response = requests.get("http://" + dst_ip + ":5000/measurement/icmp/responder/" + measurement_id)
        if responder_response.status_code != 200:
            cleanup_udp(src_ip, dst_ip, measurement_id)
            return "COULD NOT RETRIEVE RESPONDER TIME FROM HOST " + dst, 500
    except:
        cleanup_udp(src_ip, dst_ip, measurement_id)
        return "COULD NOT RETRIEVE RESPONDER TIME FROM HOST " + dst, 500

    try:
        sender_response = requests.get("http://" + src_ip + ":5000/measurement/icmp/sender/" + measurement_id)
        if sender_response.status_code != 200:
            cleanup_udp(src_ip, dst_ip, measurement_id)
            return "COULD NOT RETRIEVE SENDER TIME FROM HOST " + src, 500
    except:
        cleanup_udp(src_ip, dst_ip, measurement_id)
        return "COULD NOT RETRIEVE SENDER TIME FROM HOST " + src, 500

    try:
        receiver_response = requests.get("http://" + src_ip + ":5000/measurement/icmp/receiver/" + measurement_id)
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

        if measurement_section == "one_way_source_target":
            return handleResultData(measurement_type, responder_time, sender_time), 200
        elif measurement_section == "one_way_target_source":
            return handleResultData(measurement_type, receiver_time, responder_time), 200
        elif measurement_section == "two_way":
            return handleResultData(measurement_type, receiver_time, sender_time), 200

        print measurements
        return 'NOT SUPPORTED MEASUREMENT TYPE', 500
    except:
        cleanup_udp(src_ip, dst_ip, measurement_id)
        return "COULD NOT COMPUTE TIME FROM HOSTS RESPONSES", 500



def handleResultData(measurement_type, leftData, rightData):
    return "Siemaneczko"


if __name__ == '__main__':
    app.run(threaded=True, port=5005)
