FROM python:3.11-alpine
ADD accessToken.py .
ADD authentication.py .
ADD fyrssocket.py .

RUN python3 -m venv envpackage
RUN source envpackage/bin/activate
RUN pip install fyers-apiv3

CMD ["python3", "fyrssocket.py"]