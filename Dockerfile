# Release polish item. Do not build locally; GitHub Actions builds it around week 12.
FROM continuumio/miniconda3:latest

WORKDIR /app
COPY environment.yml pyproject.toml README.md ./
COPY src ./src
RUN conda env create -f environment.yml && conda clean -afy

SHELL ["conda", "run", "-n", "bimtwin", "/bin/bash", "-c"]
COPY configs ./configs
ENTRYPOINT ["conda", "run", "--no-capture-output", "-n", "bimtwin", "bimtwin"]
CMD ["--help"]
