FROM python:3.11

ENV HOME_DIR = /opt/http

RUN pip install --upgrade pip && pip install pipenv
RUN adduser httpuser

USER httpuser
WORKDIR $HOME_DIR
COPY --chown=httpuser:httpuser . /$HOME_DIR
RUN pip install --user -r requirements.txt && pipenv install
RUN --mount=target=/opt/http/storage,type=bind,source=/opt/storage/

EXPOSE 5000
ENTRYPOINT [ "python", "./main.py"]