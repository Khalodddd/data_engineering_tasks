from flask import Flask, request, Response
import math

app = Flask(__name__)

def lcm(a, b):
    if a == 0 and b == 0:
        return 0
    return abs(a // math.gcd(a, b) * b)

@app.route('/khaledsoliman1599_gmail_com', methods=['GET'])
def compute_lcm():
    x = request.args.get('x')
    y = request.args.get('y')

    if x is None or y is None:
        return Response("NaN", mimetype="text/plain")

    if not (x.isdigit() and y.isdigit()):
        return Response("NaN", mimetype="text/plain")

    result = lcm(int(x), int(y))
    return Response(str(result), mimetype="text/plain")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
