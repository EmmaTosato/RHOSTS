# Use a Debian-based image with both Python and Java
FROM python:3.9

# Install Java (default version for Debian 12)
RUN apt-get update && apt-get install -y default-jdk && rm -rf /var/lib/apt/lists/*

# Set Java environment variables
ENV JAVA_HOME="/usr/lib/jvm/default-java"
ENV PATH="$JAVA_HOME/bin:$PATH"

# Verify installations
RUN java -version && python3 --version

# Download Jython (optional)
RUN wget https://repo1.maven.org/maven2/org/python/jython-installer/2.7.3/jython-installer-2.7.3.jar

# Install Python dependencies
RUN pip install numpy>=1.16.0 scipy>=1.5.0 persim>=0.3.1 pybind11>=2.5.0 h5py>=2.10.0
RUN pip install --use-deprecated=legacy-resolver cechmate>=0.0.10

# Install Jupyter Notebook
RUN pip install jupyter

# Set the working directory to /repo
WORKDIR /repo

# Expose ports for Jupyter and other processes
EXPOSE 8888

# Set the default commands
CMD ["sh", "-c", "jupyter notebook --ip=0.0.0.0 --port=8888 --no-browser --allow-root --NotebookApp.token='' --NotebookApp.password='' > /repo/jupyter.log 2>&1 & exec bash"]
