FROM conda/miniconda3

WORKDIR /opt/workdir
ENV PYTHONPATH=.

RUN echo "#!/bin/bash\nsource activate py3\nexec \"\$@\"" > /entrypoint.sh && chmod +x /entrypoint.sh
ENTRYPOINT [ "/entrypoint.sh" ]

EXPOSE 9991

# install conda packages
COPY . /opt/workdir
COPY env.yml /opt/workdir/env.yml
COPY env-dev.yml /opt/workdir/env-dev.yml
RUN conda env create -n py3 --file env.yml

# add in dev packages if building dev image
ARG dev
RUN if ($dev -eq 'true'); then conda env update -n py3 --file env-dev.yml; fi;

CMD [ "python", "run.py" ]