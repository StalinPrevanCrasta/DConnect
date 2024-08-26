from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
from pymongo import MongoClient
from flask_socketio import SocketIO, emit, send
from bson import ObjectId
from bson import binary
from bson.objectid import ObjectId
import socketio
from werkzeug.utils import secure_filename
import os
import gridfs
from io import BytesIO
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'secret_key'
socketio = SocketIO(app) 


#Razorpay
import razorpay

# Initialize Razorpay client
razorpay_client = razorpay.Client(auth=(""))

# MongoDB connection
client = MongoClient('mongodb+srv://test:<db_password>@cluster0.xcpssoq.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0')
db = client['loginapp']
users_collection = db['users']
postride_collection = db['post-rides']
selectrides_collection = db['select-rides']
photo_collection = gridfs.GridFS(db)

@app.route('/update-location', methods=['POST'])
def update_location():
    data = request.get_json()
    latitude = data.get('latitude')
    longitude = data.get('longitude')
    rider_name = data.get('rider_name')
    timestamp = datetime.utcnow()

    #Find the users collection where rider_name matches the rider_name in the request and update the location field in the document
    users_collection.update_one({'username': rider_name}, {'$set': {'location': {'type': 'Point', 'coordinates': [longitude, latitude], 'timestamp': timestamp}}})
    return jsonify({'status': 'success', 'message': 'Location updated successfully'})



@app.route('/')
def index():
    return render_template('login.html')



@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']

    # Check if username and password match a document in the users collection
    user = users_collection.find_one({'username': username, 'password': password})

    if user:
        session['user_id'] = str(user['_id'])
        # Successful login
        return redirect(url_for('dashboard'))
    else:
        # Login failed, redirect back to login page
        message = "User not found! Please sign up"  # Adjust this message as needed
        return render_template('login.html', message=message)
    

    
@app.route('/signup-page')
def signup_page():
    return render_template('signup.html')



@app.route('/back-to-login')
def back_to_login():
    return render_template('login.html')



@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return render_template('login.html')



@app.route('/back-to-dashboard')
def back_to_dashboard():
    if 'user_id' in session:
        user_id = session['user_id']
        user = users_collection.find_one({'_id': ObjectId(user_id)})
        data = {
            'username': user['username']
        }
    return render_template('dashboard.html', data=data)

@app.route('/back-to-selected-rides')
def back_to_selected_rides():
    if 'user_id' in session:
        user_id = session['user_id']
        user = users_collection.find_one({'_id': ObjectId(user_id)})
        data = {
            'username': user['username']
        }
    return render_template('selected-rides.html', data=data)



@app.route('/dashboard')
def dashboard():
    if 'user_id' in session:
        user_id = session['user_id']
        user = users_collection.find_one({'_id': ObjectId(user_id)})
        data = {
            'username': user['username']
        }
    return render_template('dashboard.html', data=data)

    

@app.route('/signup', methods=['POST'])
def signup():
    username = request.form['username']
    password = request.form['password']

    # Check if username already exists in the users collection
    user = users_collection.find_one({'username': username})

    if user:
        # Username already exists, redirect back to login page
        return "User already exists!"
    else:
        # Insert new user document into the users collection
        users_collection.insert_one({'username': username, 'password': password})
        return render_template('login.html')
    

    
@app.route('/ride-details')
def ridedetails():
    if 'user_id' in session:
         user_id = session['user_id']
         user = users_collection.find_one({'_id': ObjectId(user_id)})
         data = {
             'username': user['username']
         }
    
    return render_template('ride-details.html', data=data)



@app.route('/search-rides')
def searchrides():
    if 'user_id' in session:
        user_id = session['user_id']
        user = users_collection.find_one({'_id': ObjectId(user_id)})
        data = {
            'username': user['username']
        }
    return render_template('search-options.html' , data=data)

@app.route('/search-option1')
def search_option1():
    if 'user_id' in session:
        user_id = session['user_id']
        user = users_collection.find_one({'_id': ObjectId(user_id)})
        data = {
            'username': user['username']
        }
    return render_template('search-option1.html' , data=data)

@app.route('/search-option2')
def search_option2():
    if 'user_id' in session:
        user_id = session['user_id']
        user = users_collection.find_one({'_id': ObjectId(user_id)})
        data = {
            'username': user['username']
        }
    return render_template('search-option2.html' , data=data)

@app.route('/search-option3')
def search_option3():
    if 'user_id' in session:
        user_id = session['user_id']
        user = users_collection.find_one({'_id': ObjectId(user_id)})
        data = {
            'username': user['username']
        }
    return render_template('search-option3.html' , data=data)


@app.route('/search-results1', methods=['POST'])
def search_results1():
    if 'user_id' in session:
        user_id = session['user_id']
        user = users_collection.find_one({'_id': ObjectId(user_id)})
        data = {
            'username': user['username']
        }
    start_point = request.form.get('start_point')
    end_point = request.form.get('end_point')
    start_time = request.form.get('start_time')
    date = request.form.get('date')
    rides = postride_collection.find({'start_point': start_point, 'end_point': end_point, 'start_time': start_time, 'date': date})
    # Include the rating for each rider
    rides_with_ratings = []
    for ride in rides:
        rider = users_collection.find_one({'username': ride['rider_name']})
        if rider and 'feedback' in rider and len(rider['feedback']) > 0:
            # Assuming 'rating' is a field in the 'feedback' array
            ratings = [feedback['rating'] for feedback in rider['feedback']]
            average_rating = sum(ratings) / len(ratings)
            ride['rating'] = average_rating
        else:
            ride['rating'] = 0
        rides_with_ratings.append(ride)
    return render_template('search-results.html', rides=rides_with_ratings, data=data)

@app.route('/search-results2', methods=['POST'])
def search_results2():
    if 'user_id' in session:
        user_id = session['user_id']
        user = users_collection.find_one({'_id': ObjectId(user_id)})
        data = {
            'username': user['username']
        }
    end_point = request.form.get('end_point')
    start_time = request.form.get('start_time')
    date = request.form.get('date')
    rides = postride_collection.find({'end_point': end_point, 'start_time': start_time, 'date': date})
    return render_template('search-results.html', rides=rides, data=data)

@app.route('/search-results3', methods=['POST'])
def search_results3():
    if 'user_id' in session:
        user_id = session['user_id']
        user = users_collection.find_one({'_id': ObjectId(user_id)})
        data = {
            'username': user['username']
        }
    end_point = request.form.get('end_point')
    date = request.form.get('date')
    rides = postride_collection.find({'end_point': end_point, 'date': date})
    return render_template('search-results.html', rides=rides, data=data)



# Assuming you have a 'static/uploads' folder for storing uploaded files
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER



@app.route('/post-ride', methods=['POST'])
def post_ride():
    if 'user_id' in session:
        user_id = session['user_id']
        user = users_collection.find_one({'_id': ObjectId(user_id)})
        data = {
            'username': user['username']
        }
    if request.method == 'POST':
        rider_id = session.get('user_id')
        if rider_id:
            # Convert rider_id to ObjectId (assuming it's stored as ObjectId in users_collection)
            rider_document = users_collection.find_one({'_id': ObjectId(rider_id)})

            if rider_document:
                rider_name = str(rider_document['username'])
                if rider_name:
                    vehicleNumber = request.form.get('vehicleNumber')
                    vehicleModel = request.form.get('vehicleModel')
                    ac = request.form.get('ac')
                    vacantSeats = request.form.get('vacantSeats')
                    startPoint = request.form.get('startPoint')
                    endPoint = request.form.get('endPoint')
                    start_time = request.form.get('startTime')
                    date = request.form.get('date')
                    phone_number = request.form.get('phonenumber')
                    price = request.form.get('price')

                    # Strip out the rupee symbol and convert to integer
                    price = int(price.replace('₹', '').strip())

                    # Handle photo upload
                    photo = request.files['photo']
                    if photo:
                        # Store photo in GridFS
                        photo_id = photo_collection.put(photo, filename=secure_filename(photo.filename))

                        # Insert into MongoDB
                        postride_collection.insert_one({
                            'rider_id': str(rider_id),
                            'rider_name': str(rider_name),
                            'vehicle_no': str(vehicleNumber),
                            'vehicle_model': str(vehicleModel),
                            'ac': str(ac),
                            'vacant_seats': int(vacantSeats),
                            'start_point': str(startPoint),
                            'end_point': str(endPoint),
                            'start_time': str(start_time),
                            'date': str(date),
                            'vehicle_photo_id': photo_id,  # Store photo_id in the document
                            'vehicle_photo_filename': secure_filename(photo.filename),
                            'phone_number': int(phone_number),
                            'price': price  # Store the price as an integer
                        })

                        # Optionally, remove the file after saving to database if it's no longer needed

    return render_template('ride-post-success.html', data=data)


    

    
@app.route('/get-photo/<photo_id>')
def get_photo(photo_id):
    photo_document = photo_collection.find_one({'_id': ObjectId(photo_id)})
    if photo_document:
        response = app.response_class(photo_document.read(), mimetype='application/octet-stream')
        return response
    else:
        return 'Photo not found', 404
    


@app.route('/seat-booking', methods=['POST'])
def seat_booking():
    if 'user_id' in session:
        user_id = session['user_id']
        user = users_collection.find_one({'_id': ObjectId(user_id)})
        data = {'username': user['username']}

    rider_id = request.form.get('rider_id')
    start_point = request.form.get('start_point')
    end_point = request.form.get('end_point')
    start_time = request.form.get('start_time')
    date = request.form.get('date')
    booked_seats = int(request.form.get('booked_seats'))
    rider = postride_collection.find_one({
        'rider_id': rider_id,
        'start_point': start_point,
        'end_point': end_point,
        'start_time': start_time,
        'date': date
    })

    if not rider:
        return jsonify({'error': 'Rider not found'}), 404

    # Update vacant seats
    vacant_seats = rider['vacant_seats']
    if booked_seats > vacant_seats:
        message = "Not enough seats available"
        # Redirect back to the search results page with an error message
        return render_template('search-results.html', message=message, data=data)

    # Redirect to the payment page with parameters in URL
    return redirect(url_for('initiate_payment', rider_id=rider_id, start_point=start_point, end_point=end_point, start_time=start_time, booked_seats=booked_seats, date=date))


@app.route('/initiate-payment/<rider_id>/<booked_seats>/<start_point>/<end_point>/<start_time>/<date>', methods=['GET'])
def initiate_payment(rider_id, booked_seats, start_point, end_point, start_time, date):
    if 'user_id' in session:
        user_id = session['user_id']
        user = users_collection.find_one({'_id': ObjectId(user_id)})
        rider = postride_collection.find_one({
            'rider_id': rider_id,
            'start_point': start_point,
            'end_point': end_point,
            'start_time': start_time,
            'date': date
        })

        if not rider:
            return jsonify({'error': 'Rider not found'}), 404

        # Debugging: Print the rider document
        print(f'Rider document: {rider}')

        if 'price' not in rider:
            return jsonify({'error': 'Price not found in rider details'}), 500

        # Calculate the amount to be paid
        amount = rider['price'] * int(booked_seats) * 100  # Amount in paise

        rider_id_slice = rider_id[:10] if len(rider_id) > 10 else rider_id
        user_id_slice = user_id[:10] if len(user_id) > 10 else user_id

        # Create a shortened receipt string
        receipt = f'rec_{rider_id_slice}_{user_id_slice}'

        # Create Razorpay order
        order_data = {
            'amount': amount,
            'currency': 'INR',
            'receipt': receipt,
            'payment_capture': 1
        }
        order = razorpay_client.order.create(data=order_data)

        # Render the payment page with order details
        return render_template('payment_page.html', order=order, user=user, rider=rider, rider_id=rider_id, user_id=user_id, start_point=start_point, end_point=end_point, start_time=start_time, date=date, booked_seats=booked_seats)


@app.route('/payment-success/<rider_id>/<user_id>/<start_point>/<end_point>/<start_time>/<date>', methods=['POST'])
def payment_success(rider_id, user_id, start_point, end_point, start_time, date):
    payment_id = request.form.get('razorpay_payment_id')
    order_id = request.form.get('razorpay_order_id')
    signature = request.form.get('razorpay_signature')

    # Verify payment signature (optional, based on your requirements)
    try:
        razorpay_client.utility.verify_payment_signature({
            'razorpay_order_id': order_id,
            'razorpay_payment_id': payment_id,
            'razorpay_signature': signature
        })
    except razorpay.errors.SignatureVerificationError:
        return "Payment verification failed", 400

    # Update booking status in database
    booked_seats = int(request.form.get('booked_seats'))
    rider = postride_collection.find_one({'rider_id': rider_id, 'start_point': start_point, 'end_point': end_point, 'start_time': start_time, 'date': date})
    if not rider:
        return "Rider not found", 404

    vacant_seats = rider['vacant_seats']
    vacant_seats -= booked_seats
    postride_collection.update_one({'rider_id': rider_id, 'start_time': start_time, 'end_point': end_point, 'start_point': start_point, 'date': date}, {'$set': {'vacant_seats': vacant_seats}})

    # Insert ride booking details
    selectrides_collection.insert_one({
        'rider_id': rider_id,
        'rider_name': rider['rider_name'],
        'vehicle_number': rider['vehicle_no'],
        'vehicle_model': rider['vehicle_model'],
        'ac': rider['ac'],
        'vacant_seats': vacant_seats,
        'start_point': rider['start_point'],
        'end_point': rider['end_point'],
        'start_time': rider['start_time'],
        'date': rider['date'],
        'phone_number': rider['phone_number'],
        'vehicle_photo_id': rider['vehicle_photo_id'],
        'booked_seats': booked_seats,
        'passenger_id': user_id,
        'passenger_name': users_collection.find_one({'_id': ObjectId(user_id)})['username']
    })

    if 'user_id' in session:
        user_id = session['user_id']
        user = users_collection.find_one({'_id': ObjectId(user_id)})
        data = {'username': user['username']}

    return render_template('payment-success.html', data=data)



@app.route('/get-locations', methods=['GET'])
def get_locations():
    rider_id = request.args.get('rider_id')
    passenger_id = session.get('user_id')

    # Get rider's location
    rider = users_collection.find_one({'_id': ObjectId(rider_id)})
    if not rider or 'location' not in rider:
        return jsonify({'error': 'Rider location not found'}), 404

    rider_location = rider['location']['coordinates']

    # Get passenger's location
    passenger = users_collection.find_one({'_id': ObjectId(passenger_id)})
    if not passenger or 'location' not in passenger:
        return jsonify({'error': 'Passenger location not found'}), 404

    passenger_location = passenger['location']['coordinates']

    return jsonify({
        'rider_location': {'lat': rider_location[1], 'lng': rider_location[0]},
        'passenger_location': {'lat': passenger_location[1], 'lng': passenger_location[0]}
    })


@app.route('/posted-rides', methods=['GET'])
def posted_rides():
    if 'user_id' in session:
        user_id = session['user_id']
        user = users_collection.find_one({'_id': ObjectId(user_id)})
        data = {
            'username': user['username']
        }
    rider_id = session.get('user_id')
    rides = postride_collection.find({'rider_id': rider_id})
    return render_template('posted-rides.html', rides=rides, data=data)


@app.route('/selected-rides', methods=['GET'])
def selected_rides():
    if 'user_id' in session:
        user_id = session['user_id']
        user = users_collection.find_one({'_id': ObjectId(user_id)})
        data = {
            'username': user['username']
        }
    passenger_id = session.get('user_id')
    rides = selectrides_collection.find({'passenger_id': passenger_id})
    return render_template('selected-rides.html', rides=rides, data=data)


@app.route('/show-passenger-map', methods=['POST'])
def show_passenger_map():
    if 'user_id' in session:
        user_id = session['user_id']
        user = users_collection.find_one({'_id': ObjectId(user_id)})
        data = {
            'username': user['username']
        }
    rider_id = request.form.get('rider_id')
    # Get rider's location
    passenger_id = session.get('user_id')
    rider_user = users_collection.find_one({'_id': ObjectId(rider_id)})
    if not rider_user or 'location' not in rider_user:
        return jsonify({'error': 'Rider location not found'}), 404

    rider_location = rider_user['location']['coordinates']

    passenger = selectrides_collection.find_one({'rider_id': rider_id})
    destination = passenger['end_point']

    # Get passenger's location
    passenger_id = session.get('user_id')
    passenger_document = users_collection.find_one({'_id': ObjectId(passenger_id)})
    if not passenger_document or 'location' not in passenger_document:
        return jsonify({'error': 'Passenger location not found'}), 404

    passenger_location = passenger_document['location']['coordinates']
    return render_template('map.html', rider_location=rider_location, passenger_location=passenger_location, rider_id=rider_id, data=data, destination=destination, passenger_id=passenger_id)


@app.route('/show-rider-map', methods=['POST'])
def show_rider_map():
    if 'user_id' in session:
        user_id = session['user_id']
        user = users_collection.find_one({'_id': ObjectId(user_id)})
        data = {
            'username': user['username']
        }
    # Get passenger's location
    passenger_id = request.form.get('passenger_id')
    passenger = users_collection.find_one({'_id': ObjectId(passenger_id)})
    if not passenger or 'location' not in passenger:
        return jsonify({'error': 'Passenger location not found'}), 404

    passenger_location = passenger['location']['coordinates']
    
    # Get passenger's location
    rider_id = session.get('user_id')
    rider_document = users_collection.find_one({'_id': ObjectId(rider_id)})
    if not rider_document or 'location' not in rider_document:
        return jsonify({'error': 'Rider location not found'}), 404
    
    passenger = selectrides_collection.find_one({'rider_id': rider_id})
    destination = passenger['end_point']
    rider_location = rider_document['location']['coordinates']
    return render_template('map.html', rider_location=rider_location, passenger_location=passenger_location, rider_id=rider_id, data=data, destination=destination, passenger_id=passenger_id)

    
    

@app.route('/booked-rides', methods=['GET'])
def booked_rides():
    if 'user_id' in session:
        user_id = session['user_id']
        user = users_collection.find_one({'_id': ObjectId(user_id)})
        data = {
            'username': user['username']
        }
    rider_id = session.get('user_id')
    rides = selectrides_collection.find({'rider_id': rider_id})
    return render_template('booked-rides.html', rides=rides, data=data)

@app.route('/cancel-ride-passenger', methods=['GET'])
def cancel_ride_passenger():
    rider_id = request.args.get('rider_id')
    passenger_id = request.args.get('passenger_id')
    start_point = request.args.get('start_point')
    end_point = request.args.get('end_point')
    start_time = request.args.get('start_time')
    date = request.args.get('date')
    selectrides_collection.delete_one({'rider_id': rider_id, 'passenger_id': passenger_id, 'start_point': start_point, 'end_point': end_point, 'start_time': start_time, 'date': date})
    rider = postride_collection.find_one({'rider_id': rider_id, 'start_point': start_point, 'end_point': end_point, 'start_time': start_time, 'date': date})
    vacant_seats = rider['vacant_seats']
    vacant_seats += int(request.args.get('booked_seats'))
    postride_collection.update_one({'rider_id': rider_id, 'start_time': start_time, 'end_point': end_point, 'start_point': start_point, 'date': date}, {'$set': {'vacant_seats': vacant_seats}})
    return redirect(url_for('selected_rides'))


@app.route('/delete-ride-rider', methods=['POST'])
def delete_ride_rider():
    if 'user_id' in session:
        user_id = session['user_id']
        user = users_collection.find_one({'_id': ObjectId(user_id)})
        data = {
            'username': user['username']
        }
    rider_id = request.args.get('rider_id')
    start_point = request.args.get('start_point')
    end_point = request.args.get('end_point')
    start_time = request.args.get('start_time')
    date = request.args.get('date')
    print(rider_id, start_point, end_point, start_time, date)
    selectrides_collection.delete_one({'rider_id': rider_id, 'start_point': start_point, 'end_point': end_point, 'start_time': start_time, 'date': date})
    postride_collection.delete_one({'rider_id': rider_id, 'start_time': start_time, 'end_point': end_point, 'start_point': start_point, 'date': date})
    return render_template('posted-rides.html', data=data)


@app.route('/feedback/<rider_id>/<passenger_id>', methods=['GET'])
def feedback(rider_id, passenger_id):
    if rider_id == session.get('user_id'):
        data = {
            'username': users_collection.find_one({'_id': ObjectId(passenger_id)})['username']
        }
        return render_template('feedback.html', data=data)
    elif passenger_id == session.get('user_id'):
        data = {
            'username': users_collection.find_one({'_id': ObjectId(rider_id)})['username']
        }
        return render_template('feedback.html', data=data)
    else:
        return "Unauthorized", 403
    
@app.route('/feedback-of-user', methods=['POST'])
def feedback_of_user():
    data = request.json
    username = data['username']
    rating = data['rating']
    feedback_text = data['feedback']

    user = users_collection.find_one({"username": username})

    if user:
        feedback_list = user.get('feedback', [])
        if feedback_list is None:
            feedback_list = []
        feedback_list.append({'rating': rating, 'feedback': feedback_text})

        total_ratings = sum(f['rating'] for f in feedback_list)
        average_rating = total_ratings / len(feedback_list)

        users_collection.update_one(
            {"username": username},
            {"$set": {"feedback": feedback_list}}
        )
    else:
        users_collection.insert_one({
            "username": username,
            "feedback": [{'rating': rating, 'feedback': feedback_text}],
            "rating": rating
        })

    return jsonify({'status': 'success'}), 200


if __name__ == '__main__':
    app.run(debug=True)
