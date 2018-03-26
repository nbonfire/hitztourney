FROM python:2.7
MAINTAINER Nick Bonfatti "nick@bonfatti.net"

RUN git clone https://github.com/nbonfire/hitztourney.git
WORKDIR /hitztourney
RUN pip install -r requirements.txt
RUN mkdir db && python -c 'from model import *; jsonrestore()'
ENTRYPOINT ["python"]
CMD ["HitzApp.py"]

