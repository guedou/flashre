# flashe x Docker
FROM guedou/r2m2
MAINTAINER Guillaume Valadon <guillaume@valadon.net>

# Clean /home/r2m2/
RUN rm -rf * examples/ miasm/ src/ test/ tools/ && unset -v PYTHONPATH

# Install binutils
RUN cd /home/r2m2/ && \
    curl -O https://ftp.gnu.org/gnu/binutils/binutils-2.31.tar.gz && \
    tar xzf binutils-2.31.tar.gz && \
    cd binutils-2.31 && ./configure --target=mep --prefix=/home/r2m2/ && make && \
    make install && \
    cd .. && rm -rf binutils-2.31* 

ENV PATH="/home/r2m2/bin/:${PATH}"

# Install flashre
USER root
RUN pacman -S --noconfirm python2-pip 
USER r2m2
COPY . /home/r2m2/flashre/
RUN cd /home/r2m2/flashre/ && pip2 install --user -r requirements.txt && pip2 install --user .
USER root
RUN rm -rf /home/r2m2/flashre/
USER r2m2
ENV PATH="/home/r2m2/.local/bin/:${PATH}"

# Install Sybil
RUN git clone --depth=1 https://github.com/cea-sec/Sibyl && \
    cd Sibyl && python2 setup.py install --user && cd .. && rm -rf Sibyl
