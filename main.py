import app as a
import contollers as c

a.app.register_blueprint(c.routes)



if __name__ == '__main__':
    a.app.run(host='0.0.0.0')
