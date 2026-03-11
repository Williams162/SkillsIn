from flask import Flask, render_template, request
app = Flask(__name__)
@app.route('/')
def home():
    return render_template('Home.html') #This is the first thing one will see when the website is accessed. It is a simple welcome message.

if __name__ == '__main__':
    app.run(debug=True)     #Allows the app to reload when its being accessed
    
