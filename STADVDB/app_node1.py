from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from app.config_node2 import Config
from sqlalchemy import Column, String, Float, Date
from sqlalchemy.sql import text
from datetime import datetime



app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
    

class Game(db.Model):
    __tablename__ = 'games'
    appid = Column(String(50), primary_key=True)
    name = Column(String(100), nullable=False)
    price = Column(Float)
    releasedate_cleaned = Column(Date) 
    
@app.route('/')
def index():
    return render_template('index.html')  


from datetime import datetime

@app.route('/create', methods=['POST'])
def create_game():
    try:

        data = request.json
        appid = data.get('appid')
        name = data.get('name', '')
        price = data.get('price', '')
        releasedate_cleaned = data.get('releasedate_cleaned', datetime.now().strftime('%Y-%m-%d'))

        if not appid:
            return jsonify({"error": "appid is required"}), 400


        if price is None or price == '':
            price = 0.0

        if isinstance(releasedate_cleaned, str):
            try:
                releasedate_cleaned = datetime.strptime(releasedate_cleaned, '%Y-%m-%d').date()
            except ValueError:
                return jsonify({"error": "Invalid date format. Please use 'YYYY-MM-DD'"}), 400

        print(releasedate_cleaned)
        sql = "INSERT INTO steamGames (appid, name, price, releasedate_cleaned) VALUES (:appid, :name, :price, :releasedate_cleaned)"
        db.session.execute(text(sql), {
            'appid': appid,
            'name': name,
            'price': price,
            'releasedate_cleaned': releasedate_cleaned
        })
        db.session.commit()

        return jsonify({"message": "Game created successfully!"})
    
    except Exception as e:
        print(f"Unexpected error in /create: {e}")
        db.session.rollback()  
        return jsonify({"error": str(e)}), 500


@app.route('/read', methods=['GET'])
def read_games():
    # Change to use request.args for GET request
    appid = request.args.get('appid')
    name = request.args.get('name')
    price = request.args.get('price')
    
    try:

        base_query = "SELECT * FROM steamGames WHERE 1=1"
        params = {}

        if appid:
            base_query += " AND appid = :appid"
            params['appid'] = appid
        
        if name:
            base_query += " AND name LIKE :name"
            params['name'] = f"%{name}%"  
        
        if price:

            if price.startswith('<='):
                base_query += " AND price <= :price"
                params['price'] = float(price[2:])
            elif price.startswith('>='):
                base_query += " AND price >= :price"
                params['price'] = float(price[2:])
            elif price.startswith('<'):
                base_query += " AND price < :price"
                params['price'] = float(price[1:])
            elif price.startswith('>'):
                base_query += " AND price > :price"
                params['price'] = float(price[1:])
            else:
                # Exact price or partial match
                try:
                    exact_price = float(price)
                    base_query += " AND price = :price"
                    params['price'] = exact_price
                except ValueError:
 
                    base_query += " AND CAST(price AS CHAR) LIKE :price"
                    params['price'] = f"%{price}%"

        result = db.session.execute(text(base_query), params)
        

        columns = result.keys()
        games = [dict(zip(columns, row)) for row in result]
        

        if not games:
            return jsonify({"message": "No games found"}), 404
        
        return jsonify(games)

    except Exception as e:
        print(f"Error in /read: {e}")  
        return jsonify({"error": str(e)}), 500

@app.route('/update', methods=['PUT'])
def update_game():
    data = request.json
    appid = data.get('appid')
    name = data.get('name')  
    price = data.get('price')  

    if not appid:
        return jsonify({"error": "appid is required"}), 400

    if price == '':
        price = 0.0 


    try:
        price = float(price)
    except ValueError:
        return jsonify({"error": "Invalid price value"}), 400

    query = "UPDATE steamGames SET "
    params = {}

    if name:
        query += "name = :name, "
        params["name"] = name

    if price is not None:
        query += "price = :price, "
        params["price"] = price

    query = query.rstrip(', ')
    query += " WHERE appid = :appid"
    params["appid"] = appid

    try:
        db.session.execute(text(query), params)
        db.session.commit()
        return jsonify({"message": "Game updated successfully!"})

    except Exception as e:
        print(f"Error in /update: {e}")  # Log the error for debugging
        return jsonify({"error": str(e)}), 500

@app.route('/delete', methods=['DELETE'])
def delete_game():
    data = request.json
    appid = data.get('appid')

    if not appid:
        return jsonify({"error": "appid is required"}), 400

    try:
        sql = "DELETE FROM steamGames WHERE appid = :appid"

        db.session.execute(text(sql), {'appid': appid})
        db.session.commit()

        return jsonify({"message": "Game deleted successfully!"})

    except Exception as e:
        db.session.rollback() 
        return jsonify({"error": str(e)}), 500


    
@app.route('/server-status', methods=['GET'])
def database_status():
    try:
        # Querying from the central database (master)
        with db.get_engine(bind='node1').connect() as conn:
            result = conn.execute(text("SELECT DATABASE();"))
            master_db = [row[0] for row in result]

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})
    
if __name__ == '__main__':
    app.run(debug=True,port=5001)

