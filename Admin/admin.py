from flask import Flask, request, render_template, redirect, url_for
from pymongo import MongoClient,ASCENDING
from bson.objectid import ObjectId
import random
from flask import jsonify

app = Flask(__name__)
client = MongoClient('mongodb+srv://kabiranavghan2454:12345@sharespacedb.giliwgs.mongodb.net/?retryWrites=true&w=majority&appName=ShareSpaceDb')
db = client['ShareSpaceDb']
collection = db['workspaces']
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/update_workspace', methods=['POST'])
def update_workspace():
    try:
        # Extract data from the form submission
        workspace_id = request.form.get('workspace_id')
        name = request.form.get('name')
        description = request.form.get('description')
        location = request.form.get('location')
        price_plan = request.form.get('price_plan')
        images = [img.strip() for img in request.form.get('images').split(',')]
        availability_status = request.form.get('availability_status')
        maintenance_status = request.form.get('maintenance_status')
        workspace_category = request.form.get('workspace_category')

        # Update workspace document in MongoDB
        result = collection.update_one(
            {'_id': ObjectId(workspace_id)},
            {'$set': {
                'name': name,
                'description': description,
                'location': location,
                'price_plan': price_plan,
                'images': images,
                'availability_status': availability_status,
                'maintenance_status': maintenance_status,
                'workspace_category': workspace_category
            }}
        )

        if result.modified_count > 0:
            # Redirect to the page where the update form was submitted from
            return redirect(url_for('update'))  # Assuming 'update' is the function name for rendering the page with workspaces
        else:
            return jsonify({'success': False, 'message': 'No workspace found for the provided ID'})

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})


@app.route('/workspace_details/<workspace_id>', methods=['GET'])
def get_workspace_details(workspace_id):
    # Fetch workspace details from MongoDB based on workspace_id
    workspace = collection.find_one({'_id': ObjectId(workspace_id)})
    if workspace:
        # Convert ObjectId to string for JSON serialization, if needed
        workspace['_id'] = str(workspace['_id'])
        return jsonify(workspace)
    else:
        return jsonify({'error': 'Workspace not found'}), 404
    
@app.route('/workspaces', methods=['GET'])
def update():
    # Fetch all workspaces from MongoDB, sorted by workspace_id in ascending order
    workspaces = list(collection.find().sort('workspace_id', ASCENDING))
    return render_template('update.html', workspaces=workspaces)



@app.route('/home')
def home():
    workspaces = list(collection.find())
    
    # Initialize a dictionary to store counts of each workspace category
    category_counts = {}
    count=0
    unav=0
    ava=0
    # Count available workspaces by category
    for workspace in workspaces:
        category = workspace['workspace_category']
        availability_status = workspace['availability_status']
        maintenance_status=workspace['maintenance_status']
        if availability_status=='not_available':
            ava=ava+1
        if availability_status == 'available':
            
            if category in category_counts:
                category_counts[category] += 1
            else:
                category_counts[category] = 1
            count=count+1
        if maintenance_status=='under_maintenance':
            unav=unav+1
    
    return render_template('home.html', categories=category_counts,count=count,unav=unav,ava=ava)


@app.route('/add')
def add():
    return render_template('workspace.html')

@app.route('/addworkspace')
def addworkspace():
    return render_template('add-rooms.html')

def generate_workspace_id():
    # Find the highest workspace_id in the collection
    highest_id = collection.find_one(sort=[('workspace_id', -1)])
    if highest_id:
        return highest_id['workspace_id'] + 1
    else:
        return 1
    

@app.route('/add_workspace', methods=['POST'])
def add_workspace():
    if request.method == 'POST':
        workspace_id = generate_workspace_id()
        name = request.form['name']
        description = request.form['description']
        location = request.form['location']
        price_plan = request.form['price_plan']
        images = request.form['images'].split(',')
        availability_status = request.form['availability_status']
        maintenance_status = request.form['maintenance_status']
        workspace_category = request.form['workspace_category']
        # Prepare workspace data to be inserted into MongoDB
        workspace_data = {
            'workspace_id': workspace_id,
            'name': name,
            'description': description,
            'location': location,
            'price_plan': price_plan,
            'images': images,
            'availability_status': availability_status,
            'maintenance_status': maintenance_status,
            'workspace_category':workspace_category
        }

        # Insert workspace data into MongoDB collection
        try:
            collection.insert_one(workspace_data)
            return redirect(url_for('addworkspace'))  # Redirect to index page after successful insertion
        except Exception as e:
            return f"Error inserting workspace: {e}"

    return 'Method Not Allowed', 405  # Handle cases where method is not POST


if __name__ == '__main__':
    app.run(port=5003, debug=True)
