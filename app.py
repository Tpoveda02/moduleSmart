
#Importación de librerías para visualizar el arbol
import os.path

import pandas as pd #Analisís de datos
from sklearn.model_selection import train_test_split #Crear archivos de prueba y entrenamiento
from sklearn import tree  #Construir arbol de desición - grafico.



#Importación para implementar el sitio web
from flask import Flask, render_template
from flask_wtf import FlaskForm
from flask import jsonify
from wtforms import FileField, SubmitField
from wtforms.validators import InputRequired
from werkzeug.utils import secure_filename
import os
#Conexión con la BD
from flask_mysqldb import MySQL

app = Flask(__name__)
app.config['SECRET_KEY'] = 'supersecretkey'
app.config['UPLOAD_FOLDER'] = 'static/files'
app.config['MYSQL_HOST'] = 'au77784bkjx6ipju.cbetxkdyhwsb.us-east-1.rds.amazonaws.com'
app.config['MYSQL_USER'] = 'hctnsvwig5l3wmrt'
app.config['MYSQL_PASSWORD'] = 'ni53mc1wc0ytuz1g'
app.config['MYSQL_DB'] = 'mqybuney6fs71v7s'
mysql = MySQL(app)



#Atributos botón - cargar arvhivo
class Proccess(FlaskForm):
    file = FileField("File", validators=[InputRequired()])
    submit = SubmitField()

#Obtener el archivo cargado desde la web
@app.route('/', methods=['GET',"POST"])
@app.route('/home', methods=['GET',"POST"])
def home():
    form = Proccess()
    succes_file = ""
    if form.validate_on_submit():
        file = form.file.data # First grab the file
        #file.to_cvs()
        file.save(os.path.join(os.path.abspath(os.path.dirname(__file__)),app.config['UPLOAD_FOLDER'], secure_filename(file.name)))
        succes_file = "Archivo cargado"
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM TIPO_ESTRAS")
    tipo_estra = cursor.fetchall()
    cursor.execute("SELECT * FROM TIPO_HERRAS")
    tipo_herra = cursor.fetchall()
    return render_template('index.html', form=form, tipo_estras=tipo_estra, tipo_herras=tipo_herra, message=succes_file)

@app.route("/estra/<string:id>", methods=["GET"])
def getEstras(id):
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM ESTRAS WHERE TIPO_ESTRA_ID =" + id)
    estra = cursor.fetchall()
    return jsonify(estra)

@app.route("/valid_user/<string:password>", methods=["GET"])
def getUser(password):
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM USERS WHERE id = '1' AND password = " + password)
    user = cursor.fetchall()
    return jsonify(user)

@app.route("/prediction/<string:estra>", methods=["GET"])
def fileTree(estra):
    data_pre = []
    # Leer el archivo y transformarlo en una matriz
    data = pd.read_csv('static/files/file', engine='python', index_col=0)
    # Agrupar los datos por herramienta promediando los datos
    data_tree = data.groupby(['HERRAMIENTA']).mean().drop(['#ESTUDIANTE', '#MUJERES', '#HOMBRE'], axis=1)
    # Determinar las herramientas viables y no viables - TRUE FALSE
    mean = pd.DataFrame(data_tree.mean(axis=1) > 3.1, columns=['VIABLE'])
    # Agregar la columna de la viabilidad
    data_tree = data_tree.assign(VIABLE=mean.iloc[:, 0])
    # Variables predictorias :-> Toma todas las fila, columnas.
    X = data_tree.iloc[:, 0:8]
    # Variables a predecir
    Y = data_tree.iloc[:, 8]
    print(data_tree[(data_tree['VIABLE'] == False)].shape)
    print(data_tree[(data_tree['VIABLE'] == True)].shape)
    # Llamamos al constructor del arbol de desición, maxímo 5 niveles.
    arbol = tree.DecisionTreeClassifier(min_samples_split=20, min_samples_leaf=5, max_depth=4,
                           class_weight={1: 2.23})
    # Establecemos el modelo; Var Predictoras, Var a predecir.
    arbol_test = arbol.fit(X, Y)
    # Definir la data que va a predecir
    exp = data[(data['ESTRATEGIA'] == estra)].groupby(['HERRAMIENTA']).mean().drop(
        ['#ESTUDIANTE', '#MUJERES', '#HOMBRE'], axis=1)
    # Establecer que se desea saber que si son viables las herramientas
    exp = exp.assign(PROMEDIO=True)
    x_test = pd.DataFrame(columns=(
    'INTERACCION', 'DISENO', 'USABILIDAD', 'DOCUMENTACION', 'ACTUALIZACIONES', '%APROVECHAMIENTO', '%APROBACION',
    'VALORACION'))
    best = pd.DataFrame()

    for i in range(len(exp)):
        x_test.loc[0] = exp.iloc[i, 0:8]
        y_pred = arbol_test.predict(x_test)
        y_proba = arbol_test.predict_proba(x_test)
        result = {'HERRAMIENTA': exp.index[i], 'PORCENTAJE': round(y_proba[0][1] * 100, 2)}
        best = best.append(result, ignore_index=True)

    data_result = best.nlargest(6, ['PORCENTAJE'])
    for i in range(len(data_result)):
        data_pre.append(data_result.iloc[i, 0])
    for i in range(len(data_result)):
        data_pre.append(data_result.iloc[i, 1])
    return data_pre

#Ejecución de la aplicación flask
if __name__ == '__main__':
    app.run(debug=True)




