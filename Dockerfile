FROM python:3.11-slim-bullseye AS base

FROM base AS dev

ARG USERNAME=user
ARG GROUPNAME=user
ARG UID=1000
ARG GID=1000


RUN apt-get update \
  && apt-get install sudo git zsh apt-transport-https ca-certificates unzip gnupg curl -y \
  && curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | gpg --dearmor -o /usr/share/keyrings/cloud.google.gpg \
  && echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] https://packages.cloud.google.com/apt cloud-sdk main" | tee -a /etc/apt/sources.list.d/google-cloud-sdk.list \
  && apt-get update -y \
  && apt-get install google-cloud-sdk -y \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/* \
  && curl -OL https://releases.hashicorp.com/terraform/1.8.4/terraform_1.8.4_linux_amd64.zip \
  && unzip terraform_1.8.4_linux_amd64.zip -d /bin \
  && rm terraform_1.8.4_linux_amd64.zip \
  && groupadd -g $GID $GROUPNAME \
  && useradd -m -s /usr/bin/zsh -u $UID -g $GID $USERNAME \
  && echo ${USERNAME} ALL=\(root\) NOPASSWD:ALL > /etc/sudoers.d/${USERNAME} \
  && chmod 0440 /etc/sudoers.d/${USERNAME} \
  && sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"

USER $USERNAME

WORKDIR /home/${USERNAME}
WORKDIR /workspace

COPY ./requirements.txt ./requirements.txt

RUN pip install -r requirements.txt

FROM base AS prod

WORKDIR /app

COPY ./requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["gunicorn", "app:app", "--bind", ":8080", "--workers", "1"]