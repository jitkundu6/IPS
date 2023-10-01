from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///devices.db'
db = SQLAlchemy(app)


class Device(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    x_coordinate = db.Column(db.Float, nullable=False)
    y_coordinate = db.Column(db.Float, nullable=False)
    mac_id = db.Column(db.String(20), nullable=False, unique=True)
    bt_id = db.Column(db.String(20), nullable=False, unique=True)
    static = db.Column(db.Boolean, default=True)


@app.route('/devices', methods=['GET'])
def get_devices():
    static = request.args.get('static')
    if static is None:
        devices = Device.query.all()
    else:
        devices = Device.query.filter_by(static=static).all()

    device_list = []
    for device in devices:
        device_data = {
            'id': device.id,
            'name': device.name,
            'x_coordinate': device.x_coordinate,
            'y_coordinate': device.y_coordinate,
            'mac_id': device.mac_id,
            'bt_id': device.bt_id,
            'static': device.static
        }
        device_list.append(device_data)

    return jsonify({'devices': device_list})


@app.route('/devices/<int:device_id>', methods=['GET'])
def get_device(device_id):
    device = Device.query.get(device_id)
    if device is None:
        return jsonify({'message': 'Device not found'}), 404

    device_data = {
        'id': device.id,
        'name': device.name,
        'x_coordinate': device.x_coordinate,
        'y_coordinate': device.y_coordinate,
        'mac_id': device.mac_id,
        'bt_id': device.bt_id,
        'static': device.static
    }

    return jsonify({'device': device_data})


@app.route('/devices', methods=['POST'])
def create_device():
    data = request.json
    new_device = Device(
        name=data['name'],
        x_coordinate=data['x_coordinate'],
        y_coordinate=data['y_coordinate'],
        mac_id=data['mac_id'],
        bt_id=data['bt_id'],
        static=data['static']
    )
    db.session.add(new_device)
    db.session.commit()

    return jsonify({'message': 'Device created successfully'}), 201


@app.route('/devices/<int:device_id>', methods=['PUT'])
def update_device(device_id):
    device = Device.query.get(device_id)
    if device is None:
        return jsonify({'message': 'Device not found'}), 404

    data = request.json
    device.name = data['name']
    device.x_coordinate = data['x_coordinate']
    device.y_coordinate = data['y_coordinate']
    device.mac_id = data['mac_id']
    device.bt_id = data['bt_id']
    device.static = data['static']

    db.session.commit()

    return jsonify({'message': 'Device updated successfully'})


@app.route('/devices/<int:device_id>', methods=['DELETE'])
def delete_device(device_id):
    device = Device.query.get(device_id)
    if device is None:
        return jsonify({'message': 'Device not found'}), 404

    db.session.delete(device)
    db.session.commit()

    return jsonify({'message': 'Device deleted successfully'})


if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)
