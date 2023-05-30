FROM python:3.8-buster
WORKDIR /app
RUN apt-get update \    
&& apt-get install -y libgdal-dev locales
# Update C env vars so compiler can find gdal
ENV CPLUS_INCLUDE_PATH=/usr/include/gdal
ENV C_INCLUDE_PATH=/usr/include/gdal

RUN apt-get update \    
&& apt-get install tmux -y \    
&& apt-get install -y libgdal-dev locales \
&& pip install numpy \     
&& pip install GDAL==$(gdal-config --version) \    
&& apt-get install -y python3-opencv

COPY requirements.txt requirements.txt

RUN pip install --upgrade pip
RUN pip install -r requirements.txt
RUN pip install git+https://github.com/facebookresearch/segment-anything.git

COPY . .