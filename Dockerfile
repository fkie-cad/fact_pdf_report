FROM phusion/baseimage:0.11

WORKDIR /opt/app

COPY . /opt/app

RUN install_clean git python3 python3-pip python3-wheel python3-setuptools texlive-latex-base texlive-latex-extra lmodern

RUN pip3 install -r requirements.txt

RUN apt-get remove -y python3-pip

ENTRYPOINT ["./docker_entry.py"]
