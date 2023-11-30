from flask import Flask, render_template
from flask import request, redirect, url_for
import os
import pymysql
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)

#open connection
try:
    db = pymysql.connect(
        host    ='k6cserver1.mysql.database.azure.com',
        user    ='k6cadmin',
        passwd  ='kelompok_6',
        database='db_todo',
        ssl = {'ca' :os.getenv("SSL")}

    )

    print('berhasil konek ke database')
    print(os.getenv('DB_NAME'))
except Exception as err:
    print(f'gagal konek ke database, error: {err}')

#home
@app.route('/')
def home():
    cursor_todo = db.cursor()
    cursor_todo.execute('SELECT tbl_todo.id, tbl_user.nim, tbl_user.nama, tbl_todo.nama, tbl_todo.tanggal, tbl_todo.jam from tbl_user, tbl_todo where tbl_user.nim = tbl_todo.nim_user order by tanggal')
    result_todo = cursor_todo.fetchall()
    cursor_todo.close()

       
    return render_template('todo.html', hasil_todo=result_todo)

@app.route('/about/')
def about():
    return render_template('about.html')

@app.route('/add/', methods=['POST', 'GET'])
def add():
    nims = request.form['nims']
    names = request.form['names']
    kelas = request.form['kelas']
    prodi = request.form['prodi']
        
    cur = db.cursor()
    cur.execute('INSERT INTO tbl_user (nim, nama, kelas, prodi) VALUES (%s, %s, %s, %s)', (nims, names, kelas, prodi))
    db.commit()
    cur.close()
        
    return redirect(url_for('duser'))

@app.route('/histori/')
def histori():
    cursor_histori = db.cursor()
    cursor_histori.execute('SELECT * FROM tbl_histori')
    result_histori = cursor_histori.fetchall()
    cursor_histori.close()
    return render_template('histori.html', hasil_histori=result_histori)

@app.route('/del_histori/')
def del_histori():
    cursor = db.cursor()
    cursor.execute('DELETE FROM tbl_histori')
    db.commit()
    cursor.close()
    return redirect(url_for('histori'))

@app.route('/data_user/')
def duser():
    cursor_duser = db.cursor()
    cursor_duser.execute('SELECT * FROM tbl_user')
    result_duser = cursor_duser.fetchall()
    cursor_duser.close()
    return render_template('data_user.html', hasil_user=result_duser)


@app.route('/cari/', methods=['POST','GET'])
def cari():
    if request.method == 'POST':
        user = request.form['nm']
        return redirect(url_for('user', nama=user))
    else:
        return redirect(url_for('home'))

#proses pencarian 
@app.route('/cari/<nama>')
def user(nama):
    cursor = db.cursor()
    cursor.execute('SELECT tbl_todo.id, tbl_user.nim, tbl_user.nama, tbl_todo.nama, tbl_todo.tanggal, tbl_todo.jam from tbl_user, tbl_todo where tbl_user.nim = tbl_todo.nim_user and nim_user = %s  order by tanggal', (nama,)) 
    res = cursor.fetchall()
    cursor.close()
    return render_template('todo.html', hasil_cari=res)
    

@app.route('/proses_add/', methods=['POST', 'GET'])
def proses_add():
    NIM = request.form['NIM']
    kegiatan = request.form['kegiatan']
    tanggal = request.form['tanggal']
    jam = request.form['jam']
        
    cur = db.cursor()
    cur.execute('INSERT INTO tbl_todo (nim_user, nama, tanggal, jam) VALUES (%s, %s, %s, %s)', (NIM, kegiatan, tanggal, jam))
    db.commit()
    cur.close()
        
    return redirect(url_for('home'))
          


@app.route('/delete/<int:id>')
def delete(id):
    cursor = db.cursor()

    cursor.execute('DELETE FROM tbl_todo WHERE id = %s', (id,))
    db.commit()
    cursor.close()

    return redirect(url_for('home'))

# Route untuk menandai data sebagai selesai dan memindahkan ke tabel histori
@app.route('/complete/<int:id>', methods=['POST'])
def complete(id):
    cursor = db.cursor()

    # Mendapatkan data yang akan dipindahkan ke tabel histori
    cursor.execute('SELECT * FROM tbl_todo WHERE id = %s', (id,))
    data_to_move = cursor.fetchone()

    # Menambahkan data ke tabel histori
    cursor.execute('INSERT INTO tbl_histori (nim_user, nama, tanggal) VALUES (%s, %s, %s)',
               (data_to_move[1], data_to_move[2], data_to_move[3] ))

    db.commit()

    cursor.execute('DELETE FROM tbl_todo WHERE id = %s', (id,))
    db.commit()

    cursor.close()

    return redirect(url_for('home'))

if __name__== '__main__':
	app.run(debug=True)