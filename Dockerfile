FROM jupyter/scipy-notebook

WORKDIR $HOME/fcxplayground

COPY requirements.txt  .

RUN conda install conda-libmamba-solver \
    && conda config --set solver libmamba \
    && conda install --file requirements.txt

COPY . .

EXPOSE 8888
ENTRYPOINT ["jupyter", "notebook","--allow-root","--ip=0.0.0.0","--port=8888","--no-browser"]