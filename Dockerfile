FROM python:3.6-stretch as builder

WORKDIR /home/powen/AltServerGUI

RUN pip install --no-cache-dir pyinstaller \
    && pip install -e . \
    && pyinstaller -i Icon.ico UI.spec

FROM debian:buster-slim

COPY --from=builder /home/powen/AltServerGUI/dist/AltServerGUI /home/powen/AltServerGUI