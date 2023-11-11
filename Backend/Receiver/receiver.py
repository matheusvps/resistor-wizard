from flask import Flask, request, jsonify

app = Flask(__name__, static_url_path='')

@app.route('/api/send_resistances', methods=['POST'])
def receive_resistances():
    data = request.get_json() #When request is send, data contains the resistances info
    return jsonify({'message': 'Dados recebidos com sucesso!'}), 200

#Then, handle the infos

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)