from flask import Flask, render_template, request, redirect
import plotly.express as px
from database import Vehicle
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from werkzeug.utils import secure_filename

app = Flask(__name__)

def getdb():
    engine = create_engine('sqlite:///project.sqlite')  # Creating Database Engine
    DBSession = sessionmaker(bind=engine)   # Creating Session for Database
    session = scoped_session(DBSession)
    return session

def load_gapminder():
    df = px.data.gapminder()    # Loading a Dataset
    return df

@app.route('/')
def index():
    name = "Sample Project One"     # Random Name for a Button
    return render_template('index.html', title=name)

@app.route('/home', methods=['GET', 'POST'])
def home():
    df = load_gapminder()   # Getting the Dataset
    fig1 = None             # To Store the Graph
    if request.method=='POST':
        country = request.form.get('country')   # Getting data from the Form having vlaue for Country
        year = request.form.get('year')         # Getting data from the Form having vlaue for Year
        if len(country) == 0 and len(year) != 0:    # only year is given
            year = int(year)
            result = df.query("year == @year")  # Select query condition
            fig1 = px.sunburst(result, path=['continent', 'country'], values='pop')     # Plotted Graph for all Countries
            fig1 = fig1.to_html()               # Making Graph HTML compatible
        elif len(year) == 0 and len(country) != 0:  # Only Country given
            result = df.query("country == @country")
            fig1 = px.area(result, x='year', y='pop')   # Plotted graph for all the years
            fig1 = fig1.to_html()
        elif len(country) != 0 and len(year) != 0:  # If both are given
            year = int(year)
            result = df.query("country == @country").query("year == @year")     # Applying more than one conditions
        else:
            result = df
        return render_template('home.html', result=result.to_html(), fig1 = fig1)   # Passing Dataset and Graph
    return render_template('home.html')

@app.route('/vehicle/add', methods=['GET', 'POST'])
def add_vehicle():
    if request.method == 'POST':
        name = request.form.get('name')         # Extract name from HTML Form
        contact = request.form.get('contact')   # Extract contact from HTML Form
        image = request.files.get('file')       # Extract file from HTML Form
        # validate the data
        if len(name) == 0 or len(contact) == 0 or image is None:
            print("Please fill all the fields")
            return redirect('/vehicle/add')
        # save the file in a folder
        filename = secure_filename(image.filename)  # Converts the passed filename to a computer-friendly filename
        filepath = 'static/images/'+filename
        image.save(filepath)        # Saving the file
        print('file saved')
        print(f'{name}\n{contact}\n{filepath}')
        # save the data in the database
        db = getdb()            # Creating db access session
        print('database opened')
        db.add(Vehicle(name=name, contact=contact, image=filepath))     # Adding a row in the db
        print('data added to database')
        db.commit()
        print('Changes Committed to database')
        db.close()
        print('data saved')
        return redirect('/vehicle/add') 

    return render_template('vehicle.html')

if __name__ == '__main__':
  app.run(host='0.0.0.0', port=8000, debug=True)