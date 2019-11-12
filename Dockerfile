FROM python:3.6

COPY . /

SHELL ["/bin/bash", "-c"]

RUN pip install Django==2.1 && pip install requests 

EXPOSE 8000

CMD ["python", "./manage.py", "runserver", "0.0.0.0:8000"]

