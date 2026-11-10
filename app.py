
from flask import Flask, render_template, request, redirect, url_for
import mysql.connector
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)

app.config['UPLOAD_FOLDER'] = 'static/img'
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024

# CONEXION A MYSQL

def conectar():
    return mysql.connector.connect(
        host='localhost',
        user='root',
        password='1234',
        database='ecoconsumo'
    )


# OBTENER TODOS LOS PRODUCTOS

def obtener_productos():
    conexion = conectar()
    cursor = conexion.cursor(dictionary=True)

    cursor.execute("SELECT * FROM productos ORDER BY id DESC")

    productos = cursor.fetchall()

    cursor.close()
    conexion.close()

    return productos


# PAGINA PRINCIPAL

@app.route('/')
def inicio():
    productos = obtener_productos()

    return render_template(
        'index.html',
        productos=productos
    )


# AGREGAR PRODUCTO

@app.route('/agregar', methods=['GET', 'POST'])
def agregar():

    if request.method == 'POST':

        nombre = request.form['nombre']
        descripcion = request.form['descripcion']
        elaboracion = request.form['elaboracion']
        vencimiento = request.form['vencimiento']
        precio = request.form['precio']
        stock = request.form['stock']

        archivo = request.files.get('foto')
        nombre_imagen = None

        if archivo and archivo.filename:
            nombre_imagen = secure_filename(archivo.filename)

            ruta = os.path.join(
                app.config['UPLOAD_FOLDER'],
                nombre_imagen
            )

            archivo.save(ruta)

        conexion = conectar()
        cursor = conexion.cursor()

        cursor.execute("""
            INSERT INTO productos
            (nombre, descripcion, fecha_elaboracion,
            fecha_vencimiento, precio, stock, imagen)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            nombre,
            descripcion,
            elaboracion,
            vencimiento,
            precio,
            stock,
            nombre_imagen
        ))

        conexion.commit()

        cursor.close()
        conexion.close()

        return redirect(url_for('inicio'))

    return render_template('agregar.html')


# MODIFICAR PRODUCTO

@app.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar(id):

    conexion = conectar()
    cursor = conexion.cursor(dictionary=True)

    if request.method == 'POST':

        nombre = request.form['nombre']
        descripcion = request.form['descripcion']
        precio = request.form['precio']
        stock = request.form['stock']

        cursor.execute("""
            UPDATE productos
            SET nombre = %s,
                descripcion = %s,
                precio = %s,
                stock = %s
            WHERE id = %s
        """, (nombre, descripcion, precio, stock, id))

        conexion.commit()

        cursor.close()
        conexion.close()

        return redirect(url_for('inicio'))

    cursor.execute(
        "SELECT * FROM productos WHERE id = %s",
        (id,)
    )

    producto = cursor.fetchone()

    cursor.close()
    conexion.close()

    if producto is None:
        return redirect(url_for('inicio'))

    return render_template(
        'agregar.html',
        producto=producto,
        editar=True
    )


# ELIMINAR PRODUCTO

@app.route('/eliminar/<int:id>', methods=['POST'])
def eliminar(id):

    conexion = conectar()
    cursor = conexion.cursor()

    cursor.execute(
        "DELETE FROM productos WHERE id = %s",
        (id,)
    )

    conexion.commit()

    cursor.close()
    conexion.close()

    return redirect(url_for('inicio'))


# COMPRAR PRODUCTO

@app.route('/comprar/<int:id>', methods=['POST'])
def comprar(id):

    cantidad = request.form.get('cantidad', 1, type=int)

    if cantidad is None or cantidad < 1:
        return redirect(url_for('inicio'))

    conexion = conectar()
    cursor = conexion.cursor()

    cursor.execute("""
        UPDATE productos
        SET stock = stock - %s
        WHERE id = %s AND stock >= %s
    """, (cantidad, id, cantidad))

    conexion.commit()

    cursor.close()
    conexion.close()

    return redirect(url_for('inicio'))


if __name__ == '__main__':
    app.run(debug=True)
