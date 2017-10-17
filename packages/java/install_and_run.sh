cd ~/imglib2-tutorials/

# compile java code
mvn -Dimagej.app.directory=/home/dan/ImageJ.app

# run code (NOPE: this doesn't work, use import existing pom.xml from eclipse)
java -cp target/imglib2-tutorials-0.1.0-SNAPSHOT.jar Example1a