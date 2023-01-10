FROM gitpod/workspace-full:latest
#docker pull gitpod/workspace-full:2022-06-09-20-58-43

# Move where Pyenv is stored
#RUN sudo mv /home/gitpod/.pyenv /workspace/pyenv
#RUN sudo ln -s /workspace/pyenv /home/gitpod/.pyenv

RUN wget -O /home/gitpod/requirements.txt https://raw.githubusercontent.com/gsingers/search_engineering/main/requirements.txt

RUN echo 'export PATH="$HOME/.pyenv/bin:$PATH"' >> /home/gitpod/.bashrc
RUN echo 'eval "$(pyenv init -)"' >> /home/gitpod/.bashrc
RUN echo 'eval "$(pyenv virtualenv-init -)"' >> /home/gitpod/.bashrc

RUN pyenv install 3.10.6
RUN pyenv global 3.10.6

RUN pyenv virtualenv 3.10.6 search_eng
RUN bash  -i -c "pyenv activate search_eng && pip install -r /home/gitpod/requirements.txt"
