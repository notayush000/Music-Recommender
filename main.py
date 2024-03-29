from musicf import app, create_database

if __name__ == "__main__":
    create_database(app)
    app.run(debug=True)