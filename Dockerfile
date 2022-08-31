FROM continuumio/miniconda3:4.10.3 AS env-builder
SHELL ["/bin/bash", "-c"]

ARG MLSERVER_ENV_NAME="mlserver-custom-env" \
    MLSERVER_ENV_TARBALL="./envs/base.tar.gz"

RUN conda config --add channels conda-forge && \
    conda install conda-pack

# Copy everything else
COPY . .

RUN mkdir $(dirname $MLSERVER_ENV_TARBALL); \
    for envFile in environment.yml environment.yaml conda.yml conda.yaml; do \
        if [[ -f $envFile ]]; then \
            conda env create \
                --name $MLSERVER_ENV_NAME \
                --file $envFile; \
            conda-pack --ignore-missing-files \
                -n $MLSERVER_ENV_NAME \
                -o $MLSERVER_ENV_TARBALL; \
        fi \
    done; \
    chmod -R 776 $(dirname $MLSERVER_ENV_TARBALL)

FROM seldonio/mlserver:1.1.0-slim
SHELL ["/bin/bash", "-c"]

# Copy all potential sources for custom environments
COPY \
    --chown=1000 \
    --from=env-builder \
    /envs/base.tar.g[z] \
    ./envs/base.tar.gz
COPY \
    ./settings.jso[n] \
    ./model-settings.jso[n] \
    ./requirements.tx[t] \
    .

USER root
# Install dependencies system-wide, to ensure that they are available for every
# user
RUN ./hack/build-env.sh . ./envs/base && \
    chown -R 1000:0 ./envs/base && \
    chmod -R 776 ./envs/base

RUN pip install --upgrade "jax[cuda11_cudnn82]" -f https://storage.googleapis.com/jax-releases/jax_cuda_releases.html
RUN pip install flax==0.6.0
RUN pip install torch==1.12

USER 1000

# Copy everything else
COPY . .

# Add path to newly added libs
ENV LD_LIBRARY_PATH="${LD_LIBRARY_PATH}:/opt/mlserver/envs/base/environment/lib"

# Override MLServer's own `CMD` to activate the embedded environment
# (optionally activating the hot-loaded one as well).
CMD source ./hack/activate-env.sh ./envs/base.tar.gz ./envs/base && \
    mlserver start $MLSERVER_MODELS_DIR
