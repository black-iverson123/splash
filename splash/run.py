from app import app, db, socketio
from app.models import User

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User':User}

if __name__=='__main__':
    app.app_context().push()
    db.create_all()
    socketio.run(app, debug=True, allow_unsafe_werkzeug=True)
    #app.run(debug=True) 
