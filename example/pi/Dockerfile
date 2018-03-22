# Python 3 docker based image.
FROM python:3

# Setting the working directory.
WORKDIR /

# Adding the research code here.
ADD compute.py .

# Setting the input and output volumes.
VOLUME /precision
VOLUME /computed

# Running the research code.
CMD [ "python", "compute.py" ]
