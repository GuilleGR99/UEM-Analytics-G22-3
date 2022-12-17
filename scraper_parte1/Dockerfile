FROM python:3.9

ADD scraper.py .

RUN pip install \
    requests \
    lxml \
    python-time \
    pymongo

CMD [ "python", "./scraper.py" ]

