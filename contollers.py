from flask import jsonify, request,Blueprint, render_template
import requests
import json
import mysql.connector
from datetime import datetime

routes = Blueprint('routes',__name__)


@routes.route('/')
def main():

    return render_template('index.html')

@routes.route('/stopBus', methods=['POST'])
def getPeopleByImage():
    jso = request.get_json()
    hd = {
        "Content-Type": "application/json",
        'Ocp-Apim-Subscription-Key': '21c6a27ac6424470bd5436936cc7ae03'
    }
    # Consume modelo de Computer Vision 

    api = requests.post("https://tigrehackjoyar.cognitiveservices.azure.com/computervision/imageanalysis:analyze?api-version=2023-02-01-preview&features=people&language=en&gender-neutral-caption=False",
                  data=json.dumps(jso),
                  headers=hd)
    # Obtenemos datos
    people = api.json()['peopleResult']['values']

    filtered_people = [person for person in people if person['confidence'] > 0.5]
        

    #Conectando a la base de datos
    conn = mysql.connector.connect(user='admin',password='12345678',host='hackaton.camnjaenmouk.us-east-1.rds.amazonaws.com',port='3306',database='busSchedule')
    cursor = conn.cursor()

    comando = "INSERT INTO Flow (id,numPersons,hours,dates, busesID) VALUES (NULL,%s,%s,%s,%s)"
    values = (len(filtered_people), datetime.now().time() , datetime.now().date(), 1)

    cursor.execute(comando,values)
    conn.commit()
    cursor.close()
    conn.close()


    return jsonify(filtered_people)

@routes.route('/estimations/<idRoute>', methods=['POST'])
def getEstimations(idRoute):
    #a
    #pasBus
    #BusDis
    #HoraInicio
    #horaFin
    req = request.get_json()
    date = req['date']
    pic = req['img']
    print(date)
    conn = mysql.connector.connect(user='admin',password='12345678',host='hackaton.camnjaenmouk.us-east-1.rds.amazonaws.com',port='3306',database='busSchedule')
    cursor = conn.cursor()

    comando = "select AVG(numPersons) as pasMinProm from Flow where dates = %s group by dates, busesID having busesID = %s "
    values = (date,idRoute)

    cursor.execute(comando,values)
    result = cursor.fetchall()

    a = float(result[0][0])

    comando = "select capacity from Buses where id = " + idRoute

    cursor.execute(comando)
    result = cursor.fetchall()

    c = float(result[0][0])

    comando = "select available from Buses where id = " + idRoute

    cursor.execute(comando)
    result = cursor.fetchall()

    b = float(result[0][0])

    cursor.close()
    conn.close()

    print(a)
    print(c)
    print(b)
    #Average service according to INEGI
    s = 1.3
    t_arrival = 1 / a
    f_min = 15 * 60
    t_service = s * 60
    u = ((t_service * a) / c * b) /100
    Wq = ((t_arrival * p(pic))**2) / (2 * (1- u))
    w = Wq + t_service
    B_min = (t_arrival * f_min) / (c * w)

    estimations = {
        "percentFill": u,
        "averageTimeWait": Wq,
        "totalAverageTime": w,
        "minimumQuantity": B_min
    }


    return jsonify(estimations)

def p(img):
    jso = {"url":img}
    hd = {
        "Content-Type": "application/json",
        'Ocp-Apim-Subscription-Key': '21c6a27ac6424470bd5436936cc7ae03'
    }
    # Consume modelo de Computer Vision 

    api = requests.post("https://tigrehackjoyar.cognitiveservices.azure.com/computervision/imageanalysis:analyze?api-version=2023-02-01-preview&features=people&language=en&gender-neutral-caption=False",
                  data=json.dumps(jso),
                  headers=hd)
    # Obtenemos datos
    people = api.json()['peopleResult']['values']

    filtered_people = [person for person in people if person['confidence'] > 0.5]

    return len(filtered_people)