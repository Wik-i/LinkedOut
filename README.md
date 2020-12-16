# LinkedOut


how to run it 

1. python 3.x
2. mongodb
3. install the packets(command : pip isntall -r requirements)
4. python app.py run 

install nginx
1. apt-get install nginx
2. sudo service nginx start



deploy on server
1. pip install wsgi
2. pip install gunicorn
3. nohup  gunicorn -w 4 -b 127.0.0.1:5000（your ip ： your port） run:app &
