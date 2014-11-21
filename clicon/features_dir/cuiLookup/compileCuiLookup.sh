JAR_PATHS=metamapBase/public_mm/src/javaapi/dist/MetaMapApi.jar:metamapBase/public_mm/src/javaapi/dist/prologbeans.jar

javac -d . -sourcepath src -cp $JAR_PATHS src/cuiLookup.java
